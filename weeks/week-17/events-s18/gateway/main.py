import os
from datetime import datetime
from typing import Any
from uuid import UUID

import httpx
import strawberry
from fastapi import FastAPI, HTTPException, Request, Response
from strawberry.fastapi import GraphQLRouter


EVENTS_SVC_URL = os.environ.get("EVENTS_SVC_URL", "http://events-svc-s18:8277")

app = FastAPI(title="api-gateway (events-s18)")


@app.get("/health")
def health():
    return {"ok": True}


async def _proxy(request: Request, upstream_path: str) -> Response:
    async with httpx.AsyncClient(base_url=EVENTS_SVC_URL, timeout=5) as client:
        upstream = await client.request(
            request.method,
            upstream_path,
            params=request.query_params,
            content=await request.body(),
            headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
        )
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        media_type=upstream.headers.get("content-type"),
    )


@app.api_route("/api/events", methods=["GET", "POST"])
async def api_events(request: Request):
    return await _proxy(request, "/events")


@app.api_route("/api/events/{event_id}", methods=["GET"])
async def api_event_by_id(event_id: str, request: Request):
    return await _proxy(request, f"/events/{event_id}")


@strawberry.type
class Event:
    id: strawberry.ID
    title: str
    location: str
    created_at: datetime


async def _events_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(base_url=EVENTS_SVC_URL, timeout=5)


@strawberry.type
class Query:
    @strawberry.field
    async def events(self) -> list[Event]:
        async with await _events_client() as client:
            r = await client.get("/events")
        r.raise_for_status()
        items: list[dict[str, Any]] = r.json()
        return [Event(**x) for x in items]


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def createEvent(self, title: str, location: str) -> Event:
        async with await _events_client() as client:
            r = await client.post("/events", json={"title": title, "location": location})
        if r.status_code >= 400:
            try:
                detail = r.json()
            except Exception:
                detail = {"detail": r.text}
            raise HTTPException(status_code=r.status_code, detail=detail)
        return Event(**r.json())


schema = strawberry.Schema(query=Query, mutation=Mutation)
app.include_router(GraphQLRouter(schema), prefix="/graphql")

