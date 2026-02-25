from typing import Annotated
from fastapi import APIRouter, Depends, Header
from fastapi.exceptions import HTTPException

from selenium.webdriver.support.wait import WebDriverWait
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schema.userDetailsSchema import LoginDetailsModel
from app.models.table import data
from app.routes.scrapingRouter import rewindTimetable
from app.services.scrapingService import findBaseTimetable, getCurrentDayOfYear, loginToKentVision, navigateToTimetable
from app.services.userDetailsService import getIdFromJwt
from app.dependencies import getDb

detailsRouter = APIRouter()

"""
Send a POST request to grab the users login, so that their specific 
timetable can be webscraped from KentVision.
"""

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

    """
    Parse the jwt for the users ID. Don't need to worry about validating the JWT since
    JWT validaion is handled using the KrakenD API gateway.
    """
    users_id = await getIdFromJwt(Authorization.split(" "))
    
    driver = loginToKentVision(details.email, details.password, users_id)

    # Add explicit waits so next webpage can load properly
    wait = WebDriverWait(driver, timeout=120)

    driver = navigateToTimetable(driver, wait)
   
    currentDay = getCurrentDayOfYear(driver, wait)

    # TO BE REMOVED: rewind the timetable
    # driver = rewindTimetable(driver, currentDay, wait)

    baseTimetableHtml = findBaseTimetable(driver, wait)

    driver.quit()

    print("[LOGS] Closed out of the selenium driver!")

    print("[LOGS] TIMETABLE: " + baseTimetableHtml)
   
    # add a new user into the database, accociate the user's ID with their KentVision details.
    user_details = data.Data (
        user_id = users_id,
        email = details.email,
        base_timetable = baseTimetableHtml,
    )
    
    db.add(user_details)
    await db.commit()
    await db.refresh(user_details)

    return {"Email": details.email, "UserID" : users_id}
