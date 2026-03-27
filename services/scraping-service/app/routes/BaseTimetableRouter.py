import asyncio
from typing import Annotated

from fastapi import APIRouter, Header, BackgroundTasks
from fastapi.exceptions import HTTPException

from app.models.schema.userDetailsSchema import LoginDetailsModel
from app.services.scrapingService import run_background_task
from app.services.userDetailsService import getIdFromJwt

detailsRouter = APIRouter()

"""
Send a POST request to grab the users login, so that their specific 
timetable can be webscraped from KentVision.
"""

@detailsRouter.post("/scraping-service/v1/get-login-details")
async def getBaseTimetable(details: LoginDetailsModel, 
                           background_tasks: BackgroundTasks,
                           Authorization: Annotated[str | None, Header()] = None):

    # throw an exception if no authorisation headers are found
    jwt_exception = HTTPException(
        status_code=401,
        detail="Could not extract the JWT token from 'Authorization' header.",
        headers={"WWW-Authenticate" : "Bearer"},
    )
    
    # check if the Auth header was recieved.
    if Authorization is None:
        raise jwt_exception

    """
    Parse the jwt for the users ID. Don't need to worry about validating the JWT here, since
    JWT validaion is handled using the KrakenD API gateway.
    """
    users_id = await getIdFromJwt(Authorization.split(" "))
    
    loop = asyncio.get_running_loop()

    background_tasks.add_task(
        run_background_task, 
        details.email, 
        details.password, 
        users_id,
        loop
    )

    return {"Message": "Base timetable successfully retreived!", "email": details.email, "user_id" : users_id}
