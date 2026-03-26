from typing import Annotated, Tuple
from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schema.userDetailsSchema import WebscrapeTimetableModel
from app.dependencies import getDb
from app.models.table.data import Data
from app.services.scrapingService import calculateCurrentDayOfYear, extractTimetable, get_current_day_of_year, getChromeDriver, login_to_kent_vision, navigate_to_timetable, rewind_timetable, take_screenshot
from app.services.userDetailsService import getIdFromJwt
from app.dependencies import redis, baseTimetableKey

from bs4 import BeautifulSoup

scrapingRouter = APIRouter()

"""
Function used to check for updates to the user's timetable
"""
@scrapingRouter.post('/scraping-service/v1/webscrape-timetable')
async def checkForUpdate(details: WebscrapeTimetableModel,
                         background_tasks: BackgroundTasks,
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
        
        print("[LOGS] Base Timetable found!")

        # Grab the base timetable data from the database
        stmt = select(Data.base_timetable).where(Data.user_id == user_id)
        result = await db.execute(stmt)
        base_timetable_html = result.scalar()

        background_tasks.add_task(
            run_background_task,
            base_timetable_html,
            user_id,
            details.email,
            details.password
        )

def run_background_task(base_timetable_html: str | None,
                        user_id: int,
                        email: str,
                        password: str):

    soup = BeautifulSoup(str(base_timetable_html), "html.parser") 

    # Collect the base timetable info into a list
    base_timetable_info = collect_timetable_data(soup)
 
    driver = getChromeDriver()

    wait = WebDriverWait(driver, timeout=50)
    
    driver = login_to_kent_vision(driver, wait, user_id, email, password)

    driver = navigate_to_timetable(driver, wait)

    current_day = get_current_day_of_year(driver, wait)

    driver = rewind_timetable(driver, wait, current_day,)

    found, new_data = look_for_changes(driver, wait, str(base_timetable_html)) 

    if found:
        collect_new_events(new_data, base_timetable_info, user_id)
    else:
        print("[LOGS] No new events found!")
        redis.hmset(f"user:{user_id}:data", {})

def collect_new_events(new_data, base_timetable_info, user_id):

    res_dict = {}

    for data in new_data:
        # Each entry into the dict will contain the data that needs to be returned
        # Create new soup for each entry and grab the timetable data
        soup = BeautifulSoup(str(data), "html.parser") 
        new_timetable_info = collect_timetable_data(soup)

        # Check if any new timetable data was found
        if not new_timetable_info:
            continue
    
        # Find the differences between the 2 sets
        added = [d for d in new_timetable_info if d not in base_timetable_info]
        removed = [d for d in base_timetable_info if d not in new_timetable_info]

        print("----------------[LOGS] ADDED--------------------------")
        print(added)

        print("----------------[LOGS] REMOVED--------------------------")
        print(removed)

        res = {}

        res["status"] = "UPDATED"
        res["added"] = [event for event in added]
        res["removed"] = [event for event in removed]

        date = new_timetable_info[0]["date"]

        res_dict[date] = res

    redis.hmset(f"user:{user_id}:data", res_dict)

def look_for_changes(driver: WebDriver, wait: WebDriverWait, base_timetable_html: str) -> Tuple[bool, list[str]]:

    take_screenshot(driver)

    try:
        # Use an explicit wait to allow for the main timetable to load.
        wait.until(
            EC.visibility_of_element_located((
                By.CLASS_NAME, 
                "ttb_title"
            ))
        )

        print("[LOGS] Timetable found! Beginning Check...")    

        # Parse the page for the current dates at which the timetable displays for.
        timetable_subheading = driver.find_element(By.CLASS_NAME, "ttb_title")          
  
        print("[LOGS] Calculating the current day of year...")
        # Webscrape every other timtable until the end of term
        current_day_of_year = calculateCurrentDayOfYear(timetable_subheading.text) 
        
        print("[LOGS] Looking for outstanding timtables...")
        # Check which term you are in. Then look for any changes to the timetable.
        found, new_data = look_for_difference(driver, base_timetable_html, current_day_of_year, wait)

        print("[LOGS] Check over!")

        return found, new_data

    except Exception as e:
        print("[ERROR] Error found! Please investigate further: " +  str(e))

    return False, [""]

# Function used to find any differences between the user's usual activities during the week
def look_for_difference(driver, base_timetable_html, currentDay, wait) -> Tuple[bool, list[str]]:
    print("[LOGS] Entered the look_for_difference function!") 

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
    new_data = []
    
    print("[LOGS] Printing the base timetable function in the look for difference timtable")
    print(str(base_timetable_html))

    while currentDay < borderDay:
        
        next_week_button = wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                "button[data-ttb-action='CHANGE_DATE_NEXT']"
            ))        
        )

        # Extract the HTML of the current timetable present and compare
        data = extractTimetable(driver) 
        
        # Check if it differs from the base timetable 
        if (data != base_timetable_html):
            new_data.append(data)
            print("[LOGS] Appending different HTML data! Current day" + str(currentDay))
            take_screenshot(driver)

        take_screenshot(driver)

        wait.until(
            EC.invisibility_of_element_located((
                By.CLASS_NAME,
                "ttb_loading_dialog"
            ))
        )
        
        next_week_button.click()

        wait.until(
            EC.invisibility_of_element_located((
                By.CLASS_NAME,
                "ttb_loading_dialog"
            ))
        )

        # Function uses an explicit wait to grab the current day.
        currentDay = get_current_day_of_year(driver, wait)

        print("[LOGS] Moving onto the next timetable! current day: " + str(currentDay))

    if len(new_data) != 0:
        return True, new_data

    return False, [""]

def collect_timetable_data(soup) -> list[dict]:
    # Filter the HTML based on the classes applied to each lecture/class
    # Only select the HTML that applies these specific classes
    # timetable_list = soup.find('ul', class_='sitsjqttitems').select('div.sitsjqtteventcontainer.sitsjqttitem.sitsjqttevent.sitsjqtteventhover.sv-tooltip-filter')
    timetable_list = soup.find_all('li', class_='sitsjqtteventcontainer')
   
    data = []
    for activity in timetable_list:
        
        content = activity.select_one("div.sv-col-xs-12 div[style*='font-weight:bold']")
        event_date_content = activity.select_one("span.sv-sr-only")
        
        if content:
            event_raw_data = list(content.stripped_strings)
            event_date = event_date_content.get_text(strip=True)
            
            event = {
                "date": event_date,
                "time": event_raw_data[0],
                "module": event_raw_data[1],
                "type": event_raw_data[2].strip(", "),
                "name": event_raw_data[3],
                "location": event_raw_data[5],
                "staff": [s for s in event_raw_data[7:] if s != ',']
            }

            data.append(event)
    
    return data
