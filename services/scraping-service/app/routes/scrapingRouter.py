from typing import Annotated, Tuple
from fastapi import APIRouter, Depends, Header, HTTPException

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schema.userDetailsSchema import WebscrapeTimetableModel
from app.dependencies import getDb
from app.models.table.data import Data
from app.services.scrapingService import calculateCurrentDayOfYear, extractTimetable, extractTimetable, getCurrentDayOfYear
from app.services.userDetailsService import getIdFromJwt
from app.dependencies import redis, baseTimetableKey

from bs4 import BeautifulSoup

scrapingRouter = APIRouter()

"""
Function used to check for updates to the user's timetable
"""
@scrapingRouter.post('/scraping-service/v1/webscrape-timetable')
async def checkForUpdate(details: WebscrapeTimetableModel,
                         Authorization: Annotated[str | None, Header()] = None,  
                         db: AsyncSession = Depends(getDb)):

    # Check is the Auth header is there
    jwt_exception = HTTPException(
        status_code=401,
        detail="Could not extract the JWT from the 'Authorization' header.",
        headers={"WWW-Authenticate" : "Bearer"},
    )
    
    if Authorization is None:
        raise jwt_exception

    # Grab the user's ID for database lookup
    user_id = await getIdFromJwt(Authorization.split(" "))

    # Check if the base timetable has been webscraped
    if redis.get(baseTimetableKey) == 'True':
        # Grab the base timetable data from the database
        stmt = select(Data.base_timetable).where(Data.user_id == user_id)
        result = await db.execute(stmt)
        baseTimetableHtml = result.scalar()

        # TODO: Implement way to parse the base timetable for the lectures/classes
        soup = BeautifulSoup(str(baseTimetableHtml), "html.parser") 

        collectBaseTimetableData(soup)

#        driver = loginToKentVision(details.email, details.password)
#        
#        # Scan through KV, look for changes in the timetable.
#        found, newData, currentDay = lookForChanges(str(baseTimetableHtml), driver) 
#
#        # Check if a new timteable has been found.
#        if found:
#            """
#            Use beautiful soup to parse the newData and the base timetable html.
#            Compare exactly to what is different about them, 
#            """
#            num = 0;
#            new_dict = {}
#            for data in newData:
#                # Each entry into the dict will contain the data that nee
#                parsed_data = grabInfo(data)
#                new_dict[str(num)] = parsed_data
#                num += 1

        return {"base_timetable_data" : "SUCCESSFUL"} 

def lookForChanges(baseTimetableHtml: str, driver) -> Tuple[bool, list[str], int]:
    wait = WebDriverWait(driver, timeout=30)    

    wait.until(
        EC.visibility_of_element_located((
        By.XPATH, 
        "//*[contains(text(), 'My Timetable & Events')]"
        ))
    )

    myTimetableAndEventsButton = driver.find_element(By.XPATH, "//*[contains(text(), 'My Timetable & Events')]") 
    myTimetableAndEventsButton.click()

    driver.implicitly_wait(5)
    
    myTimetablesButton = driver.find_element(By.XPATH, "//*[contains(text(), 'My Timetables')]") 
    myTimetablesButton.click()
    
    driver.implicitly_wait(5)

    viewTimetableButton = driver.find_element(By.XPATH, "//*[contains(text(), 'View Timetable')]") 
    viewTimetableButton.click()
    
    driver.implicitly_wait(5)
   
    try:
        # Switch windows to the timetable.
        original_window = driver.current_window_handle

        for wh in driver.window_handles:
            if wh != original_window:
                driver.switch_to.window(wh)
                break

        # Use an explicit wait to allow for the main timetable to load.
        wait.until(
            EC.visibility_of_element_located((
            By.ID, 
            "options_heading"
            ))
        )

        print("[LOGS] Timetable found! Beginning Check...")    

        # Webscrape every other timtable until the end of term
        currentDayofYear = calculateCurrentDayOfYear(driver) 

        # Check which term you are in. Then look for any changes to the timetable.
        found, newData, currentDay = lookForDifference(driver, baseTimetableHtml, currentDayofYear, wait)
        return found, newData, currentDay               

    except Exception as e:
        print("[ERROR] Error found! Please investigate further.")

    return False, [""], -1

"""
Function used to find any differences between the user's usual activities during the week
and the current week being checked.
"""
def lookForDifference(driver, baseTimetableHtml, currentDay, wait) -> Tuple[bool, list[str], int]:
    
    # Use the term dates here to find out which term you are currenly in.
    term1Start, term1End = 288, 346
    term2Start, term2End = 19, 79
    term3Start, term3End = 110, 170
        
    borderDay = -1

    if  currentDay > term1Start and currentDay < term1End:
        borderDay = term1End
    if currentDay > term2Start and currentDay < term2End:
        borderDay = term2End
    if currentDay > term3Start and currentDay < term3End:
        borderDay = term3End

    # Create an array to hold all the different timetables
    newData = []

    while currentDay < borderDay:
        # wait until the timetable has loaded onto the page
        wait.until(
            EC.element_to_be_clickable((
                By.ID,
                "timetable_prev"
            ))
        )

        # Extract the HTML of the current timetable present and compare
        data = extractTimetable(driver) 
        
        # Check if it differs from the base timetable 
        if (data != baseTimetableHtml):
            # Extract the current timetable
            html = extractTimetable(driver)            
            # Add the data into the list
            newData.append(html)

        # Use another explicit wait to make sure that the timetable is loaded, before moving onto the next timetable.
        nextButton = wait.until(
            EC.element_to_be_clickable(( 
                By.ID,
                "timetable_next"
            ))
        )
        
        # Move onto the next timetable
        nextButton = driver.find_element(By.ID, "timetable_next")
        nextButton.click()
        
        # Function uses an explicit wait to grab the current day.
        currentDay = getCurrentDayOfYear(driver, wait)
        
    if len(newData) != 0:
        return True, newData, currentDay

    return False, [""], -1


# TODO: Implement function to collect the information from each lecture/class into an array.
def collectBaseTimetableData(soup):
    # Filter the HTML based on the classes applied to each lecture/class
    timetable = soup.find('ul', class_='sitsjqttitems')
    # Only select the HTML that applies these specific classes
    timetable_list = soup.find('ul', class_='sitsjqttitems').select('.sv-panel.sv-panel-default.sitsjqttitem.sitsjqttevent.sitsjqtteventhover.sv-tooltip-filter')
    print(timetable_list)
    
    data = []

    for activity in timetable_list:
        content = activity.select_one(".sv-row .sv-col-xs-12 div")
        event_data = list(content.stripped_strings)
        data.append(event_data)

    # Loop through the list and parse each activity for important info (date, time, module code, etc)
    for x in data:
        print(str(x)+ "\n") 


# TODO: Implement function to find all the differences between the timetables.
def grabInfo(html: str) -> list[str]:
    return [""]
