import os
from datetime import datetime, timezone
from uuid import UUID, uuid4

import grpc
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import DateTime, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

import events_pb2 as pb2
import events_pb2_grpc as pb2_grpc


DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://events:events@postgres:5432/events"
)
GRPC_ADDR = os.environ.get("EVENTS_GRPC_ADDR", "events-grpc:50051")


class Base(DeclarativeBase):
    pass


class Event(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    location: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="events-svc-s18")


class EventCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    location: str = Field(min_length=1, max_length=128)


class EventOut(BaseModel):
    id: UUID
    title: str
    location: str
    created_at: datetime


def _validate_location_via_grpc(location: str) -> str:
    with grpc.insecure_channel(GRPC_ADDR) as channel:
        stub = pb2_grpc.EventsServiceStub(channel)
        resp = stub.ValidateLocation(pb2.ValidateLocationRequest(location=location), timeout=2)
    if not resp.ok:
        raise HTTPException(status_code=400, detail=f"invalid location: {resp.message}")
    return resp.normalized


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/events", response_model=list[EventOut])
def list_events():
    with Session(engine) as session:
        rows = session.execute(select(Event).order_by(Event.created_at.desc())).scalars()
        return [
            EventOut(
                id=UUID(e.id),
                title=e.title,
                location=e.location,
                created_at=e.created_at,
            )
            for e in rows
        ]


@app.get("/events/{event_id}", response_model=EventOut)
def get_event(event_id: UUID):
    with Session(engine) as session:
        e = session.get(Event, str(event_id))
        if not e:
            raise HTTPException(status_code=404, detail="event not found")
        return EventOut(
            id=UUID(e.id),
            title=e.title,
            location=e.location,
            created_at=e.created_at,
        )


@app.post("/events", response_model=EventOut, status_code=201)
def create_event(payload: EventCreate):
    location = _validate_location_via_grpc(payload.location)
    now = datetime.now(timezone.utc)
    e = Event(id=str(uuid4()), title=payload.title.strip(), location=location, created_at=now)
    with Session(engine) as session:
        session.add(e)
        session.commit()
    return EventOut(id=UUID(e.id), title=e.title, location=e.location, created_at=e.created_at)

