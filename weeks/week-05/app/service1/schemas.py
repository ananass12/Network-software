from pydantic import BaseModel
from typing import List, Optional
import strawberry
from strawberry.types import Info
from models import SessionLocal, TicketModel
from sqlalchemy.orm import Session

class Product(BaseModel):
    id: int
    name: str
    description: str
    price: int
    quantity: int

class ProductCreate(BaseModel):
    name: str
    description: str
    price: int
    quantity: int

class CartItem(BaseModel):
    product_id: int
    quantity: int

class Order(BaseModel):
    id: str
    items: List[dict]
    total_amount: int
    status: str

@strawberry.type
class Ticket:
    id: strawberry.ID
    status: str

    @classmethod
    def from_db(cls, t: TicketModel) -> 'Ticket':
        return cls(id = t.id, status = t.status)

    # def __init__(self, id: int, status: str):
    #     self.id = id
    #     self.status = status

@strawberry.type
class Query:

    @strawberry.field
    def getTicket(self, id: strawberry.ID) -> Optional[Ticket]:
        db = SessionLocal()
        try:
            getTicket = db.query(TicketModel).filter(TicketModel.id == id).first()
            return Ticket.from_db(getTicket) if getTicket else None
        finally:
            db.close()

    @strawberry.field
    def getAllTickets(self) -> List[Ticket]:
        db = SessionLocal()
        try:
            tickets = db.query(TicketModel).all()
            return [Ticket.from_db(ticket) for ticket in tickets]
        finally:
            db.close()

@strawberry.input
class createTicketInput:
    status: str

@strawberry.type
class Mutation:

    @strawberry.mutation
    def createTicket(self, input:createTicketInput) -> Ticket:
        db = SessionLocal()
        try:
            db_ticket = TicketModel(status=input.status)
            db.add(db_ticket)
            db.commit()
            db.refresh(db_ticket)
            return Ticket.from_db(db_ticket)
        finally:
            db.close()
        
    @strawberry.mutation
    def deleteTicket(self, id: strawberry.ID) -> bool:
        db = SessionLocal()
        try:
            db_Ticket = db.query(TicketModel).filter(TicketModel.id == id).first()
            if db_Ticket:
                db.delete(db_Ticket)
                db.commit()
                return True
            return False
        finally:
            db.close()

schema = strawberry.Schema(query=Query, mutation=Mutation)