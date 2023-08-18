import logging
from rocketry import Rocketry
from rocketry.conds import daily, after_success

from app import crud
from app.api import deps
from app.core.library_management import add_bill_to_tbs
from app.db.session import SessionLocal

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Body, Depends

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__file__)


# Create Rocketry app
app = Rocketry(execution="async")


# Create a task
@app.task("every 5 seconds")
async def test_rocketry():
    logger.info("------rocketry run schedule-------")

# @app.task(daily)
@app.task(daily)
async def check_taken_books_bills(*, db: AsyncSession = Depends(deps.get_db_async)):
    db = SessionLocal()
    logger.info("(Daily) Checking Taken Books Bills")
    tbs = crud.taken_book.get_undelivered_tbs(db)
    logger.info(f"(Daily) Processing {len(tbs)} Books")
    # apply daily bill to users those have taken books & check if a taken book is overdue or not
    await add_bill_to_tbs(db, tbs)
    logger.info("(Daily) Finished Checking Taken Books Bills Successfully")

if __name__ == "__main__":
    app.run()








