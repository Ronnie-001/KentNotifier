from typing import Annotated
import redis
from fastapi import APIRouter, Depends, Header, HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schema.userDetailsSchema import WebscrapeTimetableModel
from app.dependencies import getDb
from app.models.table.data import Data
from app.services.userDetailsService import getIdFromJwt


# Configure the redis server
redis_server = redis.Redis(
    host='redis', 
    port=6379, 
    decode_responses=True)

baseTimetableKey = "hasBaseTimetable"

scrapingRouter = APIRouter()

"""
Function used to check for updates to the user's timetable
"""
@scrapingRouter.post('/scraping-service/v1/webscrape-timetable')
async def checkForUpdate(details: WebscrapeTimetableModel,
                         Authorization: Annotated[str | None, Header()] = None,  
                         db: AsyncSession = Depends(getDb)):

    # Check if the base timetable has been webscraped
    if redis_server.get(baseTimetableKey) == 'True':
        
        # Check is the Auth header is there
        jwt_exception = HTTPException(
            status_code=401,
            detail="Could not extract the JWT from the 'Authorization' header.",
            headers={"WWW-Authenticate" : "Bearer"},
        )
        
        if Authorization is None:
            raise jwt_exception

        # Grab the user's ID for database lookup
        userId = await getIdFromJwt(Authorization.split(" "))
        
        # Grab the base timetable data from the database
        stmt = select(Data.base_timetable).where(Data.user_id == userId)
        result = await db.execute(stmt)
        data = result.first()

        # Scan through, look for changes in the timetable.
        return {"base_timetable_data" : data} 

def lookForChanges(baseTimetableHtml: str, driver):
    pass
