from typing import Annotated
from fastapi import APIRouter, Depends, Header
from fastapi.exceptions import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schema.userDetailsSchema import LoginDetailsModel
from app.services.scrapingService import loginToKentVision
from app.dependencies import getDb

detailsRouter = APIRouter()

"""
Send a POST request to grab the users login, so that their specific 
timetable can be webscraped from KentVision.
"""

# TODO: Use sent details to login to KentVision with selenium
@detailsRouter.post("/scraping-service/v1/get-login-details")
async def getBaseTimetable(details: LoginDetailsModel, 
                               Authorization: Annotated[str | None, Header()] = None,
                               db: AsyncSession = Depends(getDb)):

    # throw an exception if no authorisation headers are found
    jwt_exception = HTTPException(
        status_code=401,
        detail="Could not extract the JWT token from 'Authorization' header.",
        headers={"WWW-Authenticate" : "Bearer"},
    )
    
    # check if the Auth header was recieved.
    if Authorization is None:
        raise jwt_exception
    
    loginToKentVision(details.email, details.password)

    """
    Parse the jwt for the users ID. Don't need to worry about validating the JWT since
    JWT validaion is handled using the KrakenD API gateway.
    """
    users_id = await getIdFromJwt(Authorization.split(" "))
    
    # add a new user into the database, accociate the user's ID with their KentVision details.
    user_details = data.Data (
        user_id = users_id,
        email = details.email,
        base_timetable = baseTimetableHtml,
        user_cookies = cookies
    )
    
    db.add(user_details)
    await db.commit()
    await db.refresh(user_details)

    return {"Email": details.email, "UserID" : users_id}

