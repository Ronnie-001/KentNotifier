from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Header

from selenium import webdriver
from selenium.webdriver.common.by import By
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import getDb
from app.services.userDetailsService import encryptPassword, getIdFromJwt, verifyPassword
from app.models.table.data import Data

scrapingRouter = APIRouter()

# Navigate to the timeable where the user's timetable is.
@scrapingRouter.get("/scraping-service/v1/webscrape-timetable")
async def webscrape(Authorization: Annotated[str | None, Header()] = None,
                        db: AsyncSession = Depends(getDb)):

    # throw an exception if no authorisation headers are found
    jwt_exception = HTTPException(
        status_code=401,
        detail="Could not extract the JWT token from 'Authorization' header.",
        headers={"WWW-Authenticate" : "Bearer"},
    )
    
    if Authorization is None:
        raise jwt_exception

    # Grab the students email & password from the database, to login to KentVision.
    users_id = await getIdFromJwt(Authorization.split(" "))

    emailStmt = select(Data.email).where(Data.user_id == users_id)
    emailResult = await db.execute(emailStmt)
    email = emailResult.scalars().first()

    return {"email" : email}
