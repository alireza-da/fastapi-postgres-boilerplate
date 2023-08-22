from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.user import User

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    limit = Column(Integer, index=True)
    rent_price = Column(Float, index=True)
    overdue_penalty = Column(Float, index=True)

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(Integer, ForeignKey("categories.id"))
    # category_ref = relationship("Category", back_populates="books")
    amount = Column(Integer, index=True)
    serial_number = Column(String, index=True)
    sell_price = Column(Float, index=True)


class TakenBook(Base):
    __tablename__ = "takenbooks"

    id = Column(Integer, primary_key=True, index=True)
    book = Column(Integer, ForeignKey("books.id"))
    # book_ref = relationship("Book", back_populates="takenbooks")
    user = Column(Integer, ForeignKey("user.id"))
    # user_ref = relationship("User", back_populates="takenbooks")
    taken_date = Column(String, index=True)
    returning_date = Column(String, index=True)
    valid_borrowed_days = Column(Integer, index=True)
    status = Column(Integer, index=True)
    bill = Column(Float, index=True)

