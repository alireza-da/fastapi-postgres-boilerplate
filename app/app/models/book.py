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
    category = Column(Integer, index=True) # SQLAlchemy had a problem with ForeignKey() and It hadn't been detecting ForeignKey as a column
    amount = Column(Integer, index=True)
    serial_number = Column(String, index=True)
    sell_price = Column(Float, index=True)


class TakenBook(Base):
    __tablename__ = "takenbooks"

    id = Column(Integer, primary_key=True, index=True)
    book = Column(Integer)
    # book = relationship(Book, foreign_keys=[book_id], primaryjoin='Book.id == TakenBook.book_id')
    user = Column(Integer)
    # user = relationship(User, foreign_keys=[user_id], primaryjoin='User.id == TakenBook.user_id')
    taken_date = Column(String, index=True)
    returning_date = Column(String, index=True)
    valid_borrowed_days = Column(Integer, index=True)
    status = Column(Integer, index=True)
    bill = Column(Float, index=True)

