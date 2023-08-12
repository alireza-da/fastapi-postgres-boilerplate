from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    limit = Column(Integer, index=True)


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = ForeignKey("Category")
    amount = Column(Integer, index=True)
    serial_number = Column(String, index=True)


class TakenBook(Base):
    __tablename__ = "takenbooks"
    id = Column(Integer, primary_key=True, index=True)
    book = ForeignKey("Book")
    user = ForeignKey("User")
    taken_date = Column(String, index=True)
    returning_date = Column(String, index=True)
    bill = Column(Float, index=True)
