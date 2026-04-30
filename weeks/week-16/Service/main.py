import logging
import os
import secrets
import time
import uuid
from collections import defaultdict, deque
from typing import Deque, DefaultDict, List

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from schemas import Product, ProductCreate

disable_docs = os.getenv("INVENTORY_DISABLE_DOCS", "0") == "1"
app = FastAPI(
    title="Inventory",
    docs_url=None if disable_docs else "/docs",
    redoc_url=None if disable_docs else "/redoc",
    openapi_url=None if disable_docs else "/openapi.json",
)

products_db: List[Product] = [
    Product(id=1, name="Карандаш", description="красного цвета", quality="новый", quantity=1),
    Product(id=2, name="Блокнот", description="подарен на новый год", quality="потрепанный", quantity=1),
    Product(id=3, name="Книга", description="классический роман", quality="новый", quantity=2),
]

id_counter = max((p.id for p in products_db), default=0) + 1


logger = logging.getLogger("inventory")
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

API_KEY_HEADER = "X-API-Key"
API_KEY_ENV = "INVENTORY_API_KEY"

MAX_BODY_BYTES = int(os.getenv("INVENTORY_MAX_BODY_BYTES", "16384"))  # 16 KiB
RATE_LIMIT_WINDOW_S = int(os.getenv("INVENTORY_RATE_LIMIT_WINDOW_S", "10"))
RATE_LIMIT_MAX_REQUESTS = int(os.getenv("INVENTORY_RATE_LIMIT_MAX_REQUESTS", "30"))


def _client_id(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def require_api_key(request: Request) -> None:
    expected = os.getenv(API_KEY_ENV)
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Write operations are disabled. Set {API_KEY_ENV}.",
        )
    provided = request.headers.get(API_KEY_HEADER, "")
    if not secrets.compare_digest(provided, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


class RequestSecurityMiddleware(BaseHTTPMiddleware):
    _requests: DefaultDict[str, Deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id

        cl = request.headers.get("content-length")
        if cl is not None:
            try:
                if int(cl) > MAX_BODY_BYTES:
                    raise HTTPException(status_code=413, detail="Request body too large")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid Content-Length")
        else:
            if request.method in {"POST", "PUT", "PATCH"}:
                body = await request.body()
                if len(body) > MAX_BODY_BYTES:
                    raise HTTPException(status_code=413, detail="Request body too large")

        cid = _client_id(request)
        now = time.time()
        q = self._requests[cid]
        while q and (now - q[0]) > RATE_LIMIT_WINDOW_S:
            q.popleft()
        if len(q) >= RATE_LIMIT_MAX_REQUESTS:
            raise HTTPException(status_code=429, detail="Too Many Requests")
        q.append(now)

        start = time.time()
        try:
            response: Response = await call_next(request)
        finally:
            duration_ms = int((time.time() - start) * 1000)
            logger.info(
                "request",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "client": cid,
                    "duration_ms": duration_ms,
                },
            )

        response.headers["X-Request-Id"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=()"
        response.headers["Cross-Origin-Resource-Policy"] = "same-site"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response


app.add_middleware(RequestSecurityMiddleware)

trusted_hosts = os.getenv("INVENTORY_TRUSTED_HOSTS")
if trusted_hosts:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=[h.strip() for h in trusted_hosts.split(",") if h.strip()])

cors_origins = os.getenv("INVENTORY_CORS_ORIGINS", "http://localhost,http://127.0.0.1").split(",")
cors_origins = [o.strip() for o in cors_origins if o.strip()]
if cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
        max_age=600,
    )


@app.post("/products/", response_model=Product, status_code=201)
async def create_product(product: ProductCreate, request: Request, _=Depends(require_api_key)):
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
async def get_product(product_id: int, request: Request, _=Depends(require_api_key)):
    """
    Получение товара по ID
    """
    product = next((p for p in products_db if p.id == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Предмет не найден")
    return product


@app.delete("/products/{product_id}", status_code=204)
async def delete_product(product_id: int, request: Request, _=Depends(require_api_key)):
    global products_db
    """
    Удаление товара по ID
    """
    product = next((p for p in products_db if p.id == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Предмет не найден")

    products_db.remove(product)


@app.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: int, updated: ProductCreate, request: Request, _=Depends(require_api_key)):
    """
    Обновление товара по ID
    """
    for i, product in enumerate(products_db):
        if product.id == product_id:
            new_product = Product(id=product_id, **updated.model_dump())
            products_db[i] = new_product
            return new_product

    raise HTTPException(status_code=404, detail="Предмет не найден")
