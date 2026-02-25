from fastapi import FastAPI, HTTPException
from typing import List
from schemas import Product, ProductCreate

app = FastAPI(title="Inventory")

products_db: List[Product] = [
    Product(id=1, name="Карандаш", description="красного цвета", quality="новый", quantity=1),
    Product(id=2, name="Блокнот", description="подарен на новый год", quality="потрепанный", quantity=1),
    Product(id=3, name="Книга", description="классический роман", quality="новая", quantity=2),
]

id_counter = 1


@app.post("/products/", response_model=Product, status_code=201)
async def create_product(product: ProductCreate):
    """
    Добавление нового товара
    """
    global id_counter
    new_product = Product(id=id_counter, **product.model_dump())
    products_db.append(new_product)
    id_counter += 1
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
        raise HTTPException(status_code=404, detail="Предмет не найден")
    return product


@app.delete("/products/{product_id}", status_code=204)
async def delete_product(product_id: int):
    global products_db
    """
    Удаление товара по ID
    """
    product = next((p for p in products_db if p.id == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Предмет не найден")

    products_db.remove(product)


@app.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: int, updated: ProductCreate):
    """
    Обновление товара по ID
    """
    for i, product in enumerate(products_db):
        if product.id == product_id:
            new_product = Product(id=product_id, **updated.model_dump())
            products_db[i] = new_product
            return new_product

    raise HTTPException(status_code=404, detail="Предмет не найден")
