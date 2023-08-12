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
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash
from app.utils import APIResponseType, APIResponse
from app import exceptions as exc
from app.utils.user import (
    verify_password_reset_token,
)
from cache import cache, invalidate
from cache.util import ONE_DAY_IN_SECONDS



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
    # TODO check if book can be borrowed

    book = await crud.taken_book.create(db, obj_in=book_in)
    return APIResponse(book)

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
                          limit: int = Body(None)
                          ):
    current_category = await crud.category.get_by_id(db, c_id)
    category = schemas.Category(name=name, limit=limit)
    updated_category = await crud.category.update(db, db_obj=current_category, obj_in=category)
    return APIResponse(updated_category)