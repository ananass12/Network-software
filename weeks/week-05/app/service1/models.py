# models.py
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

engine = create_engine('sqlite:///:memory:') 
SessionLocal = sessionmaker(bind=engine)

class TicketModel(Base):
    __tablename__ = 'tickets'
    id = Column(Integer, primary_key=True)
    status = Column(String)

# Base.metadata.create_all(engine)