"""Минимальный REST API для сравнения с gRPC (POST /api/likes)."""
from uuid import uuid4

from fastapi import FastAPI

app = FastAPI(title="likes REST (bench)")
likes_storage: dict = {}


@app.post("/api/likes")
async def create_like(payload: dict):
    like_id = str(uuid4())
    target = payload.get("target", "")
    likes_storage[like_id] = {"target": target}
    return {"id": like_id, "target": target}
