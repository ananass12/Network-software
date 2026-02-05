from fastapi import FastAPI, HTTPException
from typing import List
from schemas import Product, ProductCreate

app = FastAPI(title="Inventory Microservice")

# Имитация базы данных
products_db =
id_counter = 1

@app.post("/products/", response_model=Product, status_code=201)
async def create_product(product: ProductCreate):
    global id_counter
    new_product = Product(id=id_counter, **product.model_dump())
    products_db.append(new_product)
    id_counter += 1
    return new_product

@app.get("/products/", response_model=List[Product])
async def get_products():
    return products_db

@app.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    product = next((p for p in products_db if p.id == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return product