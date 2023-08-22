from app import crud, models, schemas, utils
from fastapi.encoders import jsonable_encoder

import datetime
from datetime import timedelta

from app.core import library_management
from app.utils import APIResponseType, APIResponse
from app import exceptions as exc

async def sell_book(db, user: schemas.User, book: schemas.Book):
    if not book.sell_price:
        book.sell_price = 1
    if user.balance > book.sell_price:
        if book.amount > 0:
            current_user_data = jsonable_encoder(user)
            user_in = schemas.UserUpdate(**current_user_data)
            user_in.balance -= book.sell_price
            _book = schemas.book.Book.from_db(db_obj=book)
            _book.amount -= 1
            now = datetime.datetime.now()
            taken_book = schemas.book.TakenBook(user=user.id, book=book.id, taken_date=now, returning_date=now,
                                                valid_borrowed_days=-1, bill=book.sell_price,
                                                status= schemas.book.TakenBookStatus().SOLD)
            await crud.taken_book.create(db, obj_in=taken_book)
            await crud.user.update(db, db_obj=user, obj_in=user_in)
            return {"msg": f"Book[{book.name}({book.id})] has been sold to {user.email} | Price: {book.sell_price}"}
        else:
            raise exc.InternalServiceError(
                status_code=400,
                detail="The user can't buy book [Book Amount Limit]",
                msg_code=utils.MessageCodes.bad_request,
            )
    else:
        raise exc.InternalServiceError(
            status_code=400,
            detail="The user can't buy book [Insufficient Account Balance]",
            msg_code=utils.MessageCodes.bad_request,
        )

async def rent_book(db, user, tbs, book_in):
    for tb in tbs:
        if tb.status == schemas.book.TakenBookStatus().OVERDUE:
            raise exc.InternalServiceError(
                status_code=400,
                detail="The user can't borrow book [User has undelivered overdue book(s)]",
                msg_code=utils.MessageCodes.bad_request,
            )
    db_book = await crud.book.get_by_id(db, book_in.book)
    book = schemas.Book.from_db(db_obj=db_book)
    if await library_management.can_borrow_from_cat(db, book, user):
        days = await library_management.find_valid_rent_days(db, db_book)
        category = await crud.category.get_by_id(db, book.category)
        if days == 0:
            raise exc.InternalServiceError(
                status_code=400,
                detail="The user can't borrow book [Target Books have been rented: Out of Capacity]",
                msg_code=utils.MessageCodes.bad_request,
            )

        elif user.balance < 3 * category.rent_price:
            raise exc.InternalServiceError(
                status_code=400,
                detail="The user can't borrow book [Insufficient Account Balance]",
                msg_code=utils.MessageCodes.bad_request,
            )
        book_in.valid_borrowed_days = days
        book.amount -= 1
        await crud.book.update(db, db_obj=db_book, obj_in=book)
        created_tb = await crud.taken_book.create(db, obj_in=book_in)
        return created_tb
    raise exc.InternalServiceError(
        status_code=400,
        detail="The user can't borrow book [Category Limit]",
        msg_code=utils.MessageCodes.bad_request,
    )

async def return_book(db, msg, db_taken_book):
    if db_taken_book.status == schemas.book.TakenBookStatus().RECEIVED \
            or db_taken_book.status == schemas.book.TakenBookStatus().OVERDUE_DELIVERED:
        return {"msg": "Book already been delivered"}
    user = await crud.user.get_by_id(db, db_taken_book.user)
    current_user_data = jsonable_encoder(user)
    user_in = schemas.UserUpdate(**current_user_data)
    taken_book = schemas.TakenBook.from_db(db_obj=db_taken_book)
    db_book = await crud.book.get_by_id(db, taken_book.book)
    book = schemas.Book.from_db(db_obj=db_book)
    category = await crud.category.get_by_id(db, book.category)
    taken_book.returning_date = datetime.datetime.now()
    naive_td = taken_book.taken_date.replace(tzinfo=tz.tzutc())
    naive_rd = taken_book.returning_date.replace(tzinfo=tz.tzutc())
    diff = naive_rd - naive_td
    thirty_days = timedelta(days=taken_book.valid_borrowed_days)
    if diff <= thirty_days:
        taken_book.status = schemas.book.TakenBookStatus().RECEIVED
    elif diff > thirty_days:
        taken_book.status = schemas.book.TakenBookStatus().OVERDUE_DELIVERED
        user_in.balance -= category.overdue_penalty
        taken_book.bill += category.overdue_penalty
        await crud.user.update(db, db_obj=user, obj_in=user_in)
        msg += f"\nOverdue Delivery({diff.days} days), User received a penalty of {category.overdue_penalty}"
    book.amount += 1
    await crud.book.update(db, db_obj=db_book, obj_in=book)
    taken_book.taken_date = taken_book.taken_date.strftime('YYYY-MM-DDTHH:MM:SS')
    taken_book.returning_date = taken_book.returning_date.strftime('YYYY-MM-DDTHH:MM:SS')
    await crud.taken_book.update(db, db_obj=db_taken_book, obj_in=taken_book)
    return {"msg": msg, "details": taken_book}

async def find_user_tbs(db, book_ids, name: str = None, category_id: int = None
                        , borrowed_times: int = None, amount: int = None):
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
    return books