import datetime
from dateutil import parser

from app import crud, models, schemas, utils, api
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.encoders import jsonable_encoder


async def find_valid_rent_days(db: Session | AsyncSession, book: schemas.Book):
    n = book.amount
    if n == 0:
        return 0
    borrowed_cnt = await find_borrowed_times(db, book)
    result = (((30 * n)/n) + borrowed_cnt)
    if result < 3:
        return 3
    return result

async def find_borrowed_times(db: Session | AsyncSession, book: schemas.Book):
    tbs = await crud.taken_book.get_by_book(db, book.id)
    last_30 = []
    for tb in tbs:
        now = datetime.datetime.now()
        try:
            taken_date = parser.parse(tb.taken_date)
            taken_date = taken_date.replace(tzinfo=None)
            diff = now - taken_date
            days_30 = datetime.timedelta(days=30)
            if diff > days_30:
                last_30.append(tb)
        except Exception as e:
            print(e)
            continue
    return len(last_30)

async def can_borrow_from_cat(db: Session | AsyncSession, book: schemas.Book, user: schemas.User):
    category = await crud.category.get_by_id(db, book.category)
    user_taken_books = await crud.taken_book.get_by_user(db, user.id)
    tb_cnt = 0
    for tb in user_taken_books:
        if tb.status == schemas.book.TakenBookStatus().TAKEN or tb.status == schemas.book.TakenBookStatus().OVERDUE:
            _book = await crud.book.get_by_id(db, tb.book)
            if _book.category == book.category:
                tb_cnt += 1
    if tb_cnt >= category.limit:
        return False
    return True

async def add_bill_to_tbs(db: Session | AsyncSession, tbs: [models.book.TakenBook]):
    for tb in tbs:
        try:
            if not tb.book or not tb.user:
                print(f"Error: Taken Book Data has been saved incorrectly update it asap. ID: {tb.id}")
                crud.taken_book.delete()
                continue
            user = crud.user.get_by_id(db, tb.user)
            book = crud.book.get_by_id(db, tb.book)
            category = crud.category.get_by_id(db, book.category)
            current_user_data = jsonable_encoder(user)
            user_in = schemas.UserUpdate(**current_user_data)
            user_in.balance -= category.rent_price
            crud.user.update(db, db_obj=user, obj_in=user_in)
            taken_date = parser.parse(tb.taken_date)
            _td = schemas.TakenBook.from_db(db_obj=tb)
            _td.bill += category.rent_price
            if taken_date.replace(tzinfo=None) < datetime.datetime.now():
                _td.status = schemas.book.TakenBookStatus().OVERDUE
            crud.taken_book.update(db, db_obj=tb, obj_in=_td)
            print(f"Applied Bill[{tb.id}] Belonging to {user.email} by amount of {category.rent_price}")
        except TypeError as e:
            print(e)
            print(f"Error: Taken Book Data has been saved incorrectly update it asap. ID: {tb.id}")
            continue

