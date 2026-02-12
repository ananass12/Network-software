from fastapi import FastAPI, HTTPException
from typing import List
from schemas import Product, ProductCreate
import json
import os

app = FastAPI(title="Inventory Microservice")

DATA_FILE = "/data/products.json"

products_db: List[Product] = []
id_counter = 1

def load_data():
    global products_db, id_counter

    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            products_db = [Product(**item) for item in data]
            if products_db:
                id_counter = max(p.id for p in products_db) + 1


def save_data():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

    with open(DATA_FILE, "w") as f:
        json.dump([p.model_dump() for p in products_db], f, indent=4)


@app.on_event("startup")
def startup():
    load_data()


@app.post("/products/", response_model=Product, status_code=201)
async def create_product(product: ProductCreate):
    """
    Добавление нового товара
    """
    global id_counter
    new_product = Product(id=id_counter, **product.model_dump())
    products_db.append(new_product)
    id_counter += 1
    save_data()
    return new_product


@app.get("/")
async def root():
    """
    Приветственная страница
    """
    return {"message":"Ку ку! Посмотри что у меня есть"}


@app.get("/products/", response_model=List[Product])
async def get_products():
    """
    Получение списка всех товаров
    """
    return products_db

@app.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    """
    Получение товара по ID
    """
    product = next((p for p in products_db if p.id == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return product


@app.delete("/products/{product_id}", status_code=204)
async def delete_product(product_id: int):
    global products_db
    """
    Удаление товара по ID
    """
    product = next((p for p in products_db if p.id == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    products_db.remove(product)
    save_data()


@app.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: int, updated: ProductCreate):
    """
    Обновление товара по ID
    """
    for i, product in enumerate(products_db):
        if product.id == product_id:
            new_product = Product(id=product_id, **updated.model_dump())
            products_db[i] = new_product
            save_data()
            return new_product

    raise HTTPException(status_code=404, detail="Товар не найден")
