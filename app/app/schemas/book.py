import datetime

from .user import User

from pydantic import BaseModel

class Category(BaseModel):
    name: str
    limit: int


class Book(BaseModel):
    category: int
    amount: int
    name: str
    serial_number: str


class TakenBook(BaseModel):
    book: int
    user: int
    taken_date: datetime.datetime
    returning_date: datetime.datetime
    bill: float = 0.0
