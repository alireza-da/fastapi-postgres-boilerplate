# TODO Since we have only one library manager we don't need semaphore and lock conditions but
#  In case of having multiple supervisors/managers we have to add lock acquire before selling/renting a book

import datetime
from datetime import timedelta

from fastapi import APIRouter, Body, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette import status
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

from app import crud, models, schemas, utils
from app.api import deps
from app.api.api_v1 import service
from app.core import security, library_management
from app.core.config import settings
from app.core.security import get_password_hash
from app.utils import APIResponseType, APIResponse
from app import exceptions as exc
from app.utils.user import (
    verify_password_reset_token,
)
from cache import cache, invalidate
from cache.util import ONE_DAY_IN_SECONDS

from dateutil import tz

router = APIRouter()
namespace = "book"

@router.get('/get-all')
async def get_all_books(
        request: Request,
        db: AsyncSession = Depends(deps.get_db_async),
    ):
    books = await crud.book.get_all(db)
    return APIResponse(books)

@router.post('/create')
async def create_book(*, db: AsyncSession = Depends(deps.get_db_async), book_in: schemas.Book):
    book = await crud.book.create(db, obj_in=book_in)
    return APIResponse(book)

@router.put('/update')
async def update(*, db: AsyncSession = Depends(deps.get_db_async),
                 book_id: int = Body(None),
                 name: str = Body(None),
                 category: int = Body(None),
                 serial_number: str = Body(None),
                 amount: int = Body(None)
                 ):
    current_book = await crud.book.get_by_id(db, book_id)
    book = schemas.Book(name=name, category=category, serial_number=serial_number, amount=amount)
    updated_book = await crud.book.update(db, db_obj=current_book, obj_in=book)
    return APIResponse(updated_book)

@router.get('/taken-books/get-all')
async def get_all_taken_books(
        request: Request,
        db: AsyncSession = Depends(deps.get_db_async),
    ):
    books = await crud.taken_book.get_all(db)
    return APIResponse(books)

@router.post('/taken-books/create')
async def create_taken_book(*, db: AsyncSession = Depends(deps.get_db_async), book_in: schemas.TakenBook):
    user = await crud.user.get_by_id(db, book_in.user)
    tbs = await crud.taken_book.get_by_user(db, user.id)
    return APIResponse(await service.rent_book(db, user, tbs, book_in))


@router.post('/taken-books/return-book')
async def return_taken_book(*, db:AsyncSession=Depends(deps.get_db_async), taken_book_id: int):
    msg = "Book delivered successfully."
    db_taken_book = await crud.taken_book.get_by_id(db, taken_book_id)
    return await service.return_book(db, msg, db_taken_book)

@router.put('/taken-books/update')
async def update_taken_book(*, db:AsyncSession=Depends(deps.get_db_async),
                            tb_id: int = Body(None),
                            book: int = Body(None),
                            user: int = Body(None),
                            taken_date: str = Body(None),
                            returning_date: str = Body(None),
                            bill: float = Body(None)
                            ):
    current_taken_book = await crud.taken_book.get_by_id(db, tb_id)
    taken_book = schemas.TakenBook(book=book, user=user, taken_date=taken_date, returning_date=returning_date, bill=bill)
    updated_book = await crud.book.update(db, db_obj=current_taken_book, obj_in=taken_book)
    return APIResponse(updated_book)

@router.get('/categories/get-all')
async def get_all_categories(
        request: Request,
        db: AsyncSession = Depends(deps.get_db_async),
    ):
    categories = await crud.category.get_all(db)
    return APIResponse(categories)

@router.post('/categories/create')
async def create_category(*, db: AsyncSession = Depends(deps.get_db_async), book_in: schemas.Category):
    category = await crud.category.create(db, obj_in=book_in)
    return APIResponse(category)


@router.put('/categories/update')
async def update_category(*, db: AsyncSession = Depends(deps.get_db_async),
                          c_id: int = Body(None),
                          name: str = Body(None),
                          limit: int = Body(None),
                          rent_price: float = Body(None),
                          overdue_penalty: float = Body(None)
                          ):
    current_category = await crud.category.get_by_id(db, c_id)
    category = schemas.Category(name=name, limit=limit, rent_price=rent_price, overdue_penalty=overdue_penalty)
    updated_category = await crud.category.update(db, db_obj=current_category, obj_in=category)
    return APIResponse(updated_category)


@router.get('/get-user-taken-books/{user_id}')
async def get_user_tbs(*, db: AsyncSession = Depends(deps.get_db_async), user_id: int,
                       name: str = None, category_id: int = None, borrowed_times: int = None, amount: int = None):
    book_ids = await crud.taken_book.get_books_per_user(db, user_id)
    books = []
    filtered = False
    for bi in book_ids:
        book = await crud.book.get_by_id(db, bi)
        if name:
            filtered = True
            if name in book.name:
                books.append(book)
                continue
        if category_id:
            filtered = True
            if book.category == category_id:
                books.append(book)
                continue
        if borrowed_times:
            filtered = True
            tbs = await crud.taken_book.get_by_book(db, bi)
            if len(tbs) == borrowed_times:
                books.append(book)
                continue
        if amount:
            filtered = True
            if book.amount == amount:
                books.append(book)
                continue
        if not filtered:
            books.append(book)

    return APIResponse(books)


@router.get('/find-available-books')
async def get_available_books(*, db: AsyncSession = Depends(deps.get_db_async)):
    books = await crud.book.get_all(db)
    res = []
    for b in books:
        if b.amount > 1:
            res.append(b)
    return APIResponse(res)

@router.get('/sell')
async def sell_book(*, db: AsyncSession = Depends(deps.get_db_async), book_id: int, user_id: int):
    user = await crud.user.get_by_id(db, user_id)
    book = await crud.book.get_by_id(db, book_id)
    return await service.sell_book(db, user, book)

@router.get('/statistics')
async def get_statistics(*, db: AsyncSession = Depends(deps.get_db_async)):
    tbs = await crud.taken_book.get_all(db)
    cats = await crud.category.get_all(db)
    cats_profit = {}
    for c in cats:
        cats_profit[str(c.id)] = 0
    sells = []
    sells_overall_gain = 0
    rents_overall_gain = 0
    rents = []
    in_rents = []
    for tb in tbs:
        book = await crud.book.get_by_id(db, tb.book)
        if book:
            cats_profit[str(book.category)] += tb.bill
        if tb.status == schemas.book.TakenBookStatus().SOLD:
            sells.append(tb)
            sells_overall_gain += tb.bill
        elif tb.status == schemas.book.TakenBookStatus().RECEIVED \
                or tb.status == schemas.book.TakenBookStatus().OVERDUE_DELIVERED:
            rents.append(tb)
            rents_overall_gain += tb.bill
        else:
            in_rents.append(tb)
    return {"msg": "Statistics Calculated",
            "sell": f"Sold {len(sells)} books | Gain: {sells_overall_gain}$",
            "rent": f"Loaned {len(rents)} books | Gain: {rents_overall_gain}$ & {len(in_rents)} books have been rented but not delivered yet ",
            "category_classified": cats_profit}


@router.get('/find-users-violations')
async def get_user_violations(*, db: AsyncSession = Depends(deps.get_db_async), ascending: bool = True):
    tbs = await crud.taken_book.get_all(db)
    violations = {}
    for tb in tbs:
        user = await crud.user.get_by_id(db, tb.user)
        if tb.status == schemas.book.TakenBookStatus().OVERDUE or \
                tb.status == schemas.book.TakenBookStatus().OVERDUE_DELIVERED:
            try:
                violations[str(user.id)] = (user.email, violations[str(user.id)][1] + 1)
            except KeyError as e:
                violations[str(user.id)] = (user.email, 1)

    return APIResponse(sorted(violations.items(), key= lambda x:x[1][1], reverse=ascending))


