import datetime
from dateutil import parser
from .user import User

from pydantic import BaseModel


class Category(BaseModel):
    name: str
    limit: int
    rent_price: float
    overdue_penalty: float


class Book(BaseModel):
    category: int
    amount: int
    name: str
    serial_number: str
    sell_price: float = 0.0
    @staticmethod
    def from_db(db_obj):
        return Book(category=db_obj.category, amount=db_obj.amount, name=db_obj.name, serial_number=db_obj.serial_number)

class TakenBookStatus(BaseModel):
    RECEIVED = 1
    TAKEN = 0
    OVERDUE = 2
    OVERDUE_DELIVERED = 3
    SOLD = 4

class TakenBook(BaseModel):
    book: int
    user: int
    taken_date: datetime.datetime
    returning_date: datetime.datetime
    valid_borrowed_days: int
    bill: float = 0.0
    status: int = 0

    @staticmethod
    def from_db(db_obj):
        taken_date = parser.parse(db_obj.taken_date)
        # returning_date = datetime.datetime.strptime(db_obj.returning_date, 'YYYY-MM-DDTHH:MM:SS. mmmmmm')
        returning_date = parser.parse(db_obj.returning_date)
        return TakenBook(book=db_obj.book, user=db_obj.user, taken_date=taken_date, returning_date=returning_date,
                         status=db_obj.status, bill=db_obj.bill, valid_borrowed_days=db_obj.valid_borrowed_days)