import datetime
from typing import Any, Dict, Union, Awaitable

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.models.book import *



class CRUDBook(CRUDBase[Book, Book, Book]):
    def get_by_id(
        self, db: Session | AsyncSession, book_id: int
    ) -> Book | None | Awaitable[Book | None]:
        query = select(Book).filter(Book.id == book_id)
        return self._first(db.scalars(query))

    def get_all(self, db: Session | AsyncSession):
        query = select(Book)
        return self._all(db.scalars(query))

    async def create(self, db: Session | AsyncSession, *, obj_in: Book) -> Book:
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data = {k: v for k, v in obj_in_data.items() if v is not None}
        return await super().create(db, obj_in=obj_in_data)

    def update(
        self,
        db: Session | AsyncSession,
        *,
        db_obj: Book,
        obj_in: Union[Book, Dict[str, Any]]
    ) -> Book | Awaitable[Book]:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)

class CRUDTakenBook(CRUDBase[TakenBook, TakenBook, TakenBook]):
    def get_by_id(
        self, db: Session | AsyncSession, tb_id: int
    ) -> TakenBook | None | Awaitable[TakenBook | None]:
        query = select(TakenBook).filter(TakenBook.id == tb_id)
        return self._first(db.scalars(query))
    def get_by_user(self, db: Session | AsyncSession, u_id: int):
        query = select(TakenBook).filter(TakenBook.user == u_id)
        return self._all(db.scalars(query))

    def get_by_book(self, db: Session | AsyncSession, b_id: int):
        query = select(TakenBook).filter(TakenBook.book == b_id)
        return self._all(db.scalars(query))

    def get_all(self, db: Session | AsyncSession):
        query = select(TakenBook)
        return self._all(db.scalars(query))

    async def create(self, db: Session | AsyncSession, *, obj_in: TakenBook) -> TakenBook:
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data = {k: v for k, v in obj_in_data.items() if v is not None and type(v) != datetime.datetime}

        return await super().create(db, obj_in=obj_in_data)

    def update(
        self,
        db: Session | AsyncSession,
        *,
        db_obj: TakenBook,
        obj_in: Union[TakenBook, Dict[str, Any]]
    ) -> Book | Awaitable[TakenBook]:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)

class CRUDCategory(CRUDBase[Category, Category, Category]):
    def get_by_id(
        self, db: Session | AsyncSession, c_id: int
    ) -> Category | None | Awaitable[Category | None]:
        query = select(Category).filter(Category.id == c_id)
        return self._first(db.scalars(query))

    def get_all(self, db: Session | AsyncSession):
        query = select(Category)
        return self._all(db.scalars(query))

    async def create(self, db: Session | AsyncSession, *, obj_in: Category) -> Category:
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data = {k: v for k, v in obj_in_data.items() if v is not None}
        return await super().create(db, obj_in=obj_in_data)

    def update(
        self,
        db: Session | AsyncSession,
        *,
        db_obj: Category,
        obj_in: Union[Category, Dict[str, Any]]
    ) -> Book | Awaitable[Category]:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super().update(db, db_obj=db_obj, obj_in=update_data)

book = CRUDBook(Book)
taken_book = CRUDTakenBook(TakenBook)
category = CRUDCategory(Category)

