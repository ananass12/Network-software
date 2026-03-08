from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Optional
from pydantic import BaseModel
from saga import next_state, compensate_on_payment_failure
import uuid

app = FastAPI(title="Saga Demo")

@app.exception_handler(Exception)
async def json_error_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": str(exc)})

SERVICE_DIR = Path(__file__).resolve().parent

class Product(BaseModel):
    id: int
    name: str
    quantity: int


class CartItem(BaseModel):
    product_id: int
    quantity: int

products_db: List[dict] = [
    {"id": 1, "name": "Карандаш", "quantity": 5},
    {"id": 2, "name": "Блокнот", "quantity": 10},
    {"id": 3, "name": "Книга", "quantity": 4},
]
PRODUCTS_INIT = [{"id": p["id"], "name": p["name"], "quantity": p["quantity"]} for p in products_db]
orders_db: dict = {}
order_state = "NEW"
current_order_id: Optional[str] = None
reserved_items: dict = {}  # {order_id: {product_id: qty}}


def _reserve(order_id: str, product_id: int, qty: int):
    p = next((x for x in products_db if x["id"] == product_id), None)
    if not p or p["quantity"] < qty:
        raise HTTPException(400, f"Недостаточно товара {product_id}")
    p["quantity"] -= qty
    if order_id not in reserved_items:
        reserved_items[order_id] = {}
    reserved_items[order_id][product_id] = reserved_items[order_id].get(product_id, 0) + qty


def _cancel_reserve(order_id: str):
    if order_id not in reserved_items:
        return
    for pid, qty in reserved_items[order_id].items():
        p = next((x for x in products_db if x["id"] == pid), None)
        if p:
            p["quantity"] += qty
    reserved_items[order_id] = {}


@app.get("/shop")
async def shop():
    return FileResponse(SERVICE_DIR / "shop.html")


@app.get("/api/products")
async def get_products():
    return products_db


@app.get("/api/saga/state")
async def get_state():
    return {"state": order_state, "order_id": current_order_id}


@app.post("/api/orders/create")
async def create_order(items: List[CartItem]):
    global order_state, current_order_id
    order_id = str(uuid.uuid4())[:8]
    order_items = []
    for it in items:
        p = next((x for x in products_db if x["id"] == it.product_id), None)
        if not p or p["quantity"] < it.quantity:
            raise HTTPException(400, f"Нет товара {it.product_id} или недостаточно")
        order_items.append({"product_id": p["id"], "name": p["name"], "quantity": it.quantity})
    orders_db[order_id] = {"id": order_id, "items": order_items, "status": "NEW"}
    current_order_id = order_id
    order_state = "NEW"
    return {"order_id": order_id, "state": order_state}


@app.post("/api/saga/reserve")
async def reserve():
    global order_state, current_order_id
    if not current_order_id or current_order_id not in orders_db:
        raise HTTPException(400, "Сначала создайте заказ")
    order = orders_db[current_order_id]
    try:
        for it in order["items"]:
            _reserve(current_order_id, it["product_id"], it["quantity"])
    except HTTPException as e:
        _cancel_reserve(current_order_id)
        order_state = next_state(order_state, "RESERVE_FAIL")
        order["status"] = "CANCELLED"
        return JSONResponse(
            status_code=200,
            content={
                "state": order_state,
                "message": f"Ошибка резервирования: {e.detail}",
            },
        )
    order["status"] = "RESERVED"
    return {"state": order_state, "message": "Зарезервировано"}


@app.post("/api/saga/pay-ok")
async def pay_ok():
    global order_state
    if not current_order_id or current_order_id not in reserved_items or not reserved_items[current_order_id]:
        raise HTTPException(400, "Сначала зарезервируйте")
    order_state = next_state(order_state, "PAY_OK")
    orders_db[current_order_id]["status"] = "PAID"
    return {"state": order_state, "message": "Оплачено"}


@app.post("/api/saga/pay-fail")
async def pay_fail():
    global order_state
    if not current_order_id:
        raise HTTPException(400, "Нет заказа")
    order_state = next_state(order_state, "PAY_FAIL")
    orders_db[current_order_id]["status"] = "CANCELLED"
    compensate_on_payment_failure(lambda: _cancel_reserve(current_order_id), max_retries=3)
    return {"state": order_state, "message": "Отменено, товары возвращены"}


@app.post("/api/saga/complete")
async def complete():
    global order_state
    if order_state != "PAID":
        raise HTTPException(400, "Сначала оплатите")
    order_state = next_state(order_state, "COMPLETE")
    orders_db[current_order_id]["status"] = "DONE"
    if current_order_id in reserved_items:
        reserved_items[current_order_id] = {}
    return {"state": order_state, "message": "Готово"}


@app.post("/api/saga/reset")
async def reset():
    global order_state, current_order_id, products_db, reserved_items, orders_db
    order_state = "NEW"
    current_order_id = None
    reserved_items = {}
    orders_db = {}
    products_db = [dict(p) for p in PRODUCTS_INIT]  # копии для сброса
    return {"state": order_state, "message": "Сброс"}
