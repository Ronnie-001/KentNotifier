from typing import Annotated, Tuple
from fastapi import APIRouter, Depends, Header, HTTPException

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from sqlalchemy import create_pool_from_url, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schema.userDetailsSchema import WebscrapeTimetableModel
from app.dependencies import getDb
from app.models.table.data import Data
from app.services.scrapingService import calculateCurrentDayOfYear, extractTimetable, getCurrentDayOfYear, loginToKentVision, navigateToTimetable, takeScreenshot
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
        
        soup = BeautifulSoup(str(baseTimetableHtml), "html.parser") 
        baseTimetable_info = collectTimetableData(soup)
        
        driver = loginToKentVision(details.email, details.password, user_id)

        # Add explicit waits so next webpage can load properly
        wait = WebDriverWait(driver, timeout=50)
        
        driver = navigateToTimetable(driver, wait)
        currentDay = getCurrentDayOfYear(driver, wait)

        found, newData = lookForChanges(str(baseTimetableHtml), driver) 

        res_dict = {}

        if found:
            """
            Use beautiful soup to parse the newData and the base timetable html.
            Compare exactly to what is different about them, 
            """
            num = 0;
            for data in newData:
                # Each entry into the dict will contain the data that needs to be returned
                # Create new soup for each entry and grab the timetable data
                soup = BeautifulSoup(str(data), "html.parser") 
                newTimetable_info = collectTimetableData(soup)

                # Check if any new timetable data was found
                if not newTimetable_info:
                    # skip if nothing was found
                    continue
               
                # Clean the data before comparison
                base_cleaned = []
                for row in baseTimetable_info:
                    cleaned_row = tuple(item for item in row)
                    base_cleaned.append(cleaned_row)

                newInfo_cleaned = []
                for row in newTimetable_info:
                    cleaned_row = tuple(item for item in row)
                    newInfo_cleaned.append(cleaned_row)

                # Compare the base timetable with the data collected data.
                baseTimetableSet = set(base_cleaned)
                newDataSet = set(newInfo_cleaned)
                
                # Find the differences between the 2 sets
                added = newDataSet - baseTimetableSet
                removed = baseTimetableSet - newDataSet

                print("----------------[LOGS] ADDED--------------------------")
                print(added)

                print("----------------[LOGS] REMOVED--------------------------")
                print(removed)

                # Append the found changes.
                res_dict["status"] = "UPDATED"
                res_dict["added"] = [list(item) for item in added]
                res_dict["removed"] = [list(item) for item in removed]

        else:
            print("[LOGS] NO new events found!")
            
            return {
                "status": "NO CHANGE",
                "added": [],
                "removed": []
            }
        
        return res_dict 

def normalize_timetable_data(data_list):
    """
    1. Splits text to remove \n \t and extra spaces.
    2. Rejects any strings that become empty.
    3. Returns a set of clean tuples.
    """
    cleaned_set = set()
    
    for row in data_list:
        clean_row = []
        for item in row:
            text = " ".join(str(item).split())
            if text:  # ONLY add if text is not empty
                clean_row.append(text)
        
        if clean_row:
            cleaned_set.add(tuple(clean_row))
            
    return cleaned_set

"""
Function created to look for changes in the user's timetable.
"""
def lookForChanges(baseTimetableHtml: str, driver) -> Tuple[bool, list[str]]:
    wait = WebDriverWait(driver, timeout=50)    
    
    try:
        # Use an explicit wait to allow for the main timetable to load.
        wait.until(
            EC.visibility_of_element_located((
            By.ID, 
            "timetable_title"
            ))
        )

        print("[LOGS] Timetable found! Beginning Check...")    

        # Parse the page for the current dates at which the timetable displays for.
        timetableSubheading = driver.find_element(By.CLASS_NAME, "sitsjqtttitle")          
  
        print("[LOGS] Calculating the current day of year...")
        # Webscrape every other timtable until the end of term
        currentDayofYear = calculateCurrentDayOfYear(timetableSubheading.text) 
        
        print("[LOGS] Looking for outstanding timtables...")
        # Check which term you are in. Then look for any changes to the timetable.
        found, newData = lookForDifference(driver, baseTimetableHtml, currentDayofYear, wait)

        print("[LOGS] Check over!")

        return found, newData

    except Exception as e:
        print("[ERROR] Error found! Please investigate further: " +  str(e))

    return False, [""]

"""
Function used to find any differences between the user's usual activities during the week

and the current week being checked.
"""
def lookForDifference(driver, baseTimetableHtml, currentDay, wait) -> Tuple[bool, list[str]]:
    print("[LOGS] Entered the lookForDifference function!") 

    # Use the term dates here to find out which term you are currenly in.
    term1Start, term1End = 288, 344
    term2Start, term2End = 19, 79
    term3Start, term3End = 110, 170
        
    borderDay = -1

    if  currentDay > term1Start and currentDay < term1End:
        borderDay = term1End
    elif currentDay > term2Start and currentDay < term2End:
        borderDay = term2End
    elif currentDay > term3Start and currentDay < term3End:
        borderDay = term3End

    # Create an array to hold all the different timetables
    newData = []
    
    print("[LOGS] Printing the base timetable function in the look for difference timtable")
    print(str(baseTimetableHtml))

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
            # Extract the current timetable, add the data into the list
            html = extractTimetable(driver)            
            newData.append(html)

            print("[LOGS] Appending different HTML data! Current day" + str(currentDay))
            takeScreenshot(driver)

        # Use another explicit wait to make sure that the timetable is loaded, before moving onto the next timetable.
        nextButton = wait.until(
            EC.element_to_be_clickable(( 
                By.ID,
                "timetable_next"
            ))
        )
        
        takeScreenshot(driver)

        wait.until(
            EC.invisibility_of_element_located((
                By.CLASS_NAME,
                "ui-widget-overlay ui-front"
            ))
        )

        # Move onto the next timetable
        nextButton = driver.find_element(By.ID, "timetable_next")
        nextButton.click()

        wait.until(
            EC.invisibility_of_element_located((
                By.CLASS_NAME,
                "ui-widget-overlay ui-front"
            ))
        )
        # Function uses an explicit wait to grab the current day.
        currentDay = getCurrentDayOfYear(driver, wait)

        print("[LOGS] Moving onto the next timetable! current day: " + str(currentDay))

    if len(newData) != 0:
        return True, newData

    return False, [""]


# TODO: Implement function to collect the information from each lecture/class into an array.
def collectTimetableData(soup) -> list[str]:
    # Filter the HTML based on the classes applied to each lecture/class
    # Only select the HTML that applies these specific classes
    timetable_list = soup.find('ul', class_='sitsjqttitems').select('.sv-panel.sv-panel-default.sitsjqttitem.sitsjqttevent.sitsjqtteventhover.sv-tooltip-filter')
    
    data = []
    for activity in timetable_list:
        content = activity.select_one(".sv-row .sv-col-xs-12 div")
        event_data = list(content.stripped_strings)

        # TODO: Add check to see if the event data is empty.
        data.append(event_data)
    
    return data


def cleanData(text: str) -> str:
    print("[LOGS] Cleaning data!")
    if not text:
        return ""

    return text.replace("\n", "")

"""
Function purely for testing; used for putting the date back 
into the boundaries of the first term.
"""
def rewindTimetable(driver, currentDay, wait):
    count = 0;
    while count < 8:
        print("[LOGS] Rewinding the days of the year! Current day: " + str(currentDay))

        wait.until(
            EC.invisibility_of_element_located((
                By.CLASS_NAME,
                "ui-widget-overlay ui-front"
            ))
        )
        
        wait.until(
            EC.element_to_be_clickable((
                By.ID,
                "timetable_prev"
            ))
        )

        previousWeekButton = driver.find_element(By.ID, "timetable_prev") 
        previousWeekButton.click()

        wait.until(
            EC.invisibility_of_element_located((
                By.CLASS_NAME,
                "ui-widget-overlay ui-front"
            ))
        )

        # recalculate the currentDay
        currentDay = getCurrentDayOfYear(driver, wait)

        # increment count
        count += 1;

    print("[LOGS] Rewind over!")

    return driver
