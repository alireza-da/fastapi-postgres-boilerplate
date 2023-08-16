import datetime

from app import crud, models, schemas, utils, api
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
def find_valid_rent_days(db: Session | AsyncSession, book: schemas.Book):
    n = book.amount
    borrowed_cnt = find_borrowed_times(db, book)
    result = (((30 * n)/n) + borrowed_cnt)
    if result < 3:
        return 3
    return result

def find_borrowed_times(db: Session | AsyncSession, book: schemas.Book):
    tbs = crud.taken_book.get_by_book(db, book.id)
    last_30 = []
    for tb in tbs:
        now = datetime.datetime.now()
        taken_date = datetime.datetime.strptime(tb.taken_date)
        diff = now - taken_date
        days_30 = datetime.timedelta(days=30)
        if diff > days_30:
            last_30.append(tb)
    return len(last_30)

def can_borrow_from_cat(db: Session | AsyncSession, book: schemas.Book, user: schemas.User):
    category = crud.category.get_by_id(db, book.category)
    user_taken_books = crud.taken_books.get_by_user(db, user.id)
    tb_cnt = 0
    for tb in user_taken_books:
        if tb.status == schemas.TakenBookStatus.TAKEN or tb.status == schemas.TakenBookStatus.OVERDUE:
            _book = crud.book.get_by_id(tb.book)
            if _book.category == book.category:
                tb_cnt += 1
    if tb_cnt >= category.limit:
        return False
    return True

