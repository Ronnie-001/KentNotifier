import os
import asyncio

from fastapi import Depends

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.table import data
from app.dependencies import redis, baseTimetableKey
from app.dependencies import getDb
from app.database.dbconn import Session

def getChromeDriver() -> WebDriver:
    # Set the options for the chrome driver that we will recieve.
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("----disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)

    return driver

# Orchestrator function that handles logging into kentvision, scraping the base timetable and commiting this to the database.
def run_background_task(email: str, password: str, user_id: int, loop):

    driver = getChromeDriver()

    # Add explicit waits so next webpage can load properly
    wait = WebDriverWait(driver, 60)

    driver = login_to_kent_vision(driver, wait, user_id, email, password)
    
    driver = navigate_to_timetable(driver, wait)

    # Rewind the timetable so simulate webscraping during term time.
    current_day = get_current_day_of_year(driver, wait)

    driver = rewind_timetable(driver, wait, current_day)

    base_timetable_html = find_base_timetable(driver, wait)

    driver.quit()

    print("[LOGS] " + str(base_timetable_html))

    asyncio.run_coroutine_threadsafe(commit_to_database(user_id, email, base_timetable_html), loop)

# Starts filling out the sign in  information.
def handle_inital_navigation(driver: WebDriver, 
                             wait: WebDriverWait, 
                             user_id: int, 
                             email: str,
                             password: str) -> WebDriver:

    kent_vision_website = "https://evision.kent.ac.uk/urd/sits.urd/run/siw_lgn" 

    # Set the current state of the user to 'logging in'
    redis.hset(f"user:{user_id}:state", mapping={
                    "status":"LOGGING_IN",
                    "mfa_code": "NULL",
               })

    # Navigate to the KentVision Application Portal.
    driver.get(kent_vision_website)
    studentApplicationPortalButton = driver.find_element(By.ID, "kent-student-login-button")
    studentApplicationPortalButton.click()
    print("[LOGS] Student and Staff Button clicked!")

    take_screenshot(driver)

    wait.until(
        EC.visibility_of_element_located((
        By.ID, 
        "i0116"
        ))
    )

    take_screenshot(driver)

    # Use provided email in the input field
    emailInput = driver.find_element(By.ID, "i0116")
    emailInput.send_keys(email)
    nextButton = driver.find_element(By.ID, "idSIButton9")
    nextButton.click()

    take_screenshot(driver)

    print("[LOGS] Next button clicked!")
    
    wait.until(
        EC.visibility_of_element_located((
        By.ID, 
        "i0118"
        ))
    )

    # Use provided password in the input field
    passwordInput = driver.find_element(By.ID, "i0118")
    passwordInput.send_keys(password) 
    signInButtonClicked = clickElement("idSIButton9", driver, wait)

    if signInButtonClicked:
        print("[LOGS] Sign in button clicked!")

    print("[LOGS] Waiting for the next page to appear...")

    take_screenshot(driver)

    return driver

def login_to_kent_vision(driver: WebDriver,
                         wait: WebDriverWait, 
                         user_id: int,
                         email: str,
                         password: str) -> WebDriver:

    driver = handle_inital_navigation(driver, wait, user_id, email, password)
    
    try:
        signed_in_prompt = driver.find_elements(By.XPATH, "//*[contains(text(), 'Stay signed in?')]")

        if signed_in_prompt and signed_in_prompt[0].is_displayed():
            driver = handle_stay_signed_in_prompt(driver, wait, user_id)
        else:
            driver = handle_mfa_prompt(driver, wait, user_id)
        
        return driver

    except TimeoutException:
        print("[ERROR] Error when trying to log in! TimeoutException caught!")

        redis.hset(f"user:{user_id}:state", mapping={
                    "status": "FAILED",
                    "mfa_code": "NULL",
               })

        take_screenshot(driver)

    except Exception as e:
        print("[ERROR] Ran into an error: " + str(e))

        redis.hset(f"user:{user_id}:state", mapping={
                    "status": "FAILED",
                    "mfa_code": "NULL",
               })

        take_screenshot(driver)

    return driver

def handle_stay_signed_in_prompt(driver: WebDriver, wait: WebDriverWait, user_id: int) -> WebDriver:
    wait.until(
        EC.visibility_of_element_located((
        By.XPATH, 
        "//*[contains(text(), 'Stay signed in?')]"
        ))
    )

    print("[LOGS] Stay signed in page found!")
   
    driver.implicitly_wait(5)

    yesButton = driver.find_element(By.ID, "idSIButton9") 
    yesButton.click()

    driver.implicitly_wait(5)
    
    # Check for the main homepage
    wait.until(
        EC.visibility_of_element_located((
            By.XPATH, 
            "//*[contains(text(), 'Welcome to KentVision')]"
        ))
    )

    print("[LOGS] Main Homepage found!")

    # Set the current state of the user to 'logging in'
    redis.hset(f"user:{user_id}:state", mapping={
                    "status":"SUCCESS",
                    "mfa_code": "NULL",
               })

    return driver

def handle_mfa_prompt(driver: WebDriver, wait: WebDriverWait, user_id: int) -> WebDriver:

     wait.until(
        EC.visibility_of_element_located((
             By.XPATH, 
             "//*[contains(text(), 'Approve sign in request')]"
        ))
     )
     
     # Extract the MFA code from the webpage
     mfaAuthElement = driver.find_element(By.ID, "idRichContext_DisplaySign")
     mfaAuthNumber = mfaAuthElement.text
     print("[LOGS] MFA Number found!: " + mfaAuthNumber)

     # Set the current state of the user to 'MFA_WAITING'
     redis.hset(f"user:{user_id}:state", mapping={
                     "status":"MFA_WAITING",
                     "mfa_code": mfaAuthNumber,
                })

     print("[LOGS]")
    
     # Wait for the user to enter in the MFA code.
     # Check if the 'Stay signed in? In on screen instead
     wait.until(
         EC.visibility_of_element_located((
             By.XPATH, 
             "//*[contains(text(), 'Stay signed in?')]"
         ))
     )

     # Set the current state of the user to 'SUCCESS'
     redis.hset(f"user:{user_id}:state", mapping={
                     "status":"SUCCESS",
                     "mfa_code": mfaAuthNumber,
                })

     print("[LOGS] MFA code entered!")
     
     # Go to the KentVison homepage
     yesButton = driver.find_element(By.ID, "idSIButton9") 
     yesButton.click()

     driver.implicitly_wait(10)

     take_screenshot(driver)

     return driver

def navigate_to_timetable(driver: WebDriver, wait: WebDriverWait) -> WebDriver:

    print("[LOGS] Naviagting to timetable!")

    take_screenshot(driver)

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

        print("[LOGS] Timetable found!")    

        return driver

    except TimeoutException as e:
        print("[ERROR] Timeout exception caught!: " + str(e))
        take_screenshot(driver)

    return driver

def find_base_timetable(driver: WebDriver, wait: WebDriverWait) -> str:
    try:
        currentDayofYear = get_current_day_of_year(driver, wait)

        print("[LOGS] Current days into the year: " + str(currentDayofYear))

        term1Start, term1End = 288, 365
        term2Start, term2End = 19, 79
        term3Start, term3End = 110, 170
        
        # Look for the first week of term.
        if (currentDayofYear < term1End and currentDayofYear > term1Start):
            findBaseTimetableDate(currentDayofYear, term1Start, driver, wait)
        elif (currentDayofYear < term2End and currentDayofYear > term2Start):
            findBaseTimetableDate(currentDayofYear, term2Start, driver, wait)
        elif (currentDayofYear < term3End and currentDayofYear > term3Start):
            findBaseTimetableDate(currentDayofYear, term3Start, driver, wait)
            
        # Once you have found the base timetable, webscrape it.
        timetableData = extractTimetable(driver)

        redis.set(baseTimetableKey, 'True') 

        return timetableData

    except TimeoutException:
        print("[ERROR] Unable to load the timetable page!")
        take_screenshot(driver)

    return "NO TIMETABLE DATA"

def get_current_day_of_year(driver: WebDriver, wait: WebDriverWait) -> int:
    wait.until(
        EC.visibility_of_element_located((
            By.CLASS_NAME,
            "ttb_title"
        ))
    )

    # Parse the page for the current dates at which the timetable displays for.
    timetableSubheading = driver.find_element(By.CLASS_NAME, "ttb_title")          
    currentDayofYear = calculateCurrentDayOfYear(timetableSubheading.text)

    return currentDayofYear

"""
Function purely for testing; used for putting the date back 
into the boundaries of the first term.
"""
def rewind_timetable(driver: WebDriver, wait: WebDriverWait, currentDay: int) -> WebDriver:
    count = 0;
    while count < 8:
        print("[LOGS] Rewinding the days of the year! Current day: " + str(currentDay))

        prev_week_button = wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR, 
                "button[data-ttb-action='CHANGE_DATE_PREV']"
            ))
        )

        prev_week_button.click()

        wait.until(
            EC.invisibility_of_element_located((
                By.ID,
                "ttb_loading_dialog"
            ))
        )

        wait.until(
            EC.element_to_be_clickable((
                By.CLASS_NAME,
                "ttb_title"
            ))
        )

        # recalculate the currentDay
        currentDay = get_current_day_of_year(driver, wait)

        # increment count
        count += 1;

    print("[LOGS] Rewind over!")
    
    take_screenshot(driver)

    return driver

async def commit_to_database(user_id: int, 
                             email: str,
                             base_timetable_html: str,
                             db: AsyncSession = Depends(getDb)):

    async with Session() as db:
        try:
            # add a new user into the database, accociate the user's ID with their KentVision details.
            user_details = data.Data (
                user_id = user_id,
                email = email,
                base_timetable = base_timetable_html,
            )
    
            db.add(user_details)
            await db.commit()
            await db.refresh(user_details)
            print(f"[LOGS] Successfully saved user {user_id} to Postgres.")
        
        except Exception as e:
            print(f"[ERROR] Failed to save to Postgres: {e}")
            await db.rollback()

"""
Use to avoid StaleElementReferenceExceptions when clicking an element, 
most likley caused due to rapid changes in the DOM.
"""
def clickElement(id: str, driver, wait) -> bool:
    result = False
    attempts = 0
    while attempts < 5:
        try:

            wait.until(
                EC.visibility_of_element_located((
                    By.ID, 
                    id
                ))
            )

            button = driver.find_element(By.ID, id)
            button.click()
            result = True
            break
        except StaleElementReferenceException: 
            pass
        attempts += 1

    return result;

"""
Function used to take a screenshot of the current page. 
Mainly used for debugging purposes.
"""
def take_screenshot(driver):
    DEBUG_DIR = "/app/debug_output"
    os.makedirs(DEBUG_DIR, exist_ok=True) 

    # Take a screenshot of the current page.
    screen_shot_path = os.path.join(DEBUG_DIR, "debug.png")
    driver.save_screenshot(screen_shot_path)

    print(f"Path to the screenshot: {screen_shot_path}")   


"""
Function used to calculate the current day of the year of the FIRST day
of the week (the monday) on the timtable.
"""
def calculateCurrentDayOfYear(text: str) -> int:
    """
    The map stores the cumuliative number of days BEFORE the month.
    This way, to calculate the day that the calendar is currently looking at,
    all that is needed is the day of the month + total number of days before
    the current month. 
    """
    map = {
        "January": 0,

        # NOTE: Change the name back to Febuary, they spelt the name of the month wrong
        "February": 31,
        "March": 59,
        "April": 90,
        "May": 120,
        "June": 151,
        "July": 181,
        "August": 212,
        "September": 243,
        "October": 273,
        "November": 304,
        "December": 334
    }
    
    arr = text.split(" ")

    
    day = -1
    month = ""

    if len(arr) == 6:
        day = int(arr[0])
        month = str(arr[1])        
    else:
        # Grab the day, month from the text
        day = int(arr[0])
        month = str(arr[3])

    totalDays = day + map[month]

    return totalDays

# Function used to find the first week of term (the base timetable)
def findBaseTimetableDate(currentDay, borderDay, driver, wait):
    while True:
        if currentDay - 7 < borderDay:
            print("[LOGS] Base timetable found!")
            break
        else:
            print("[LOGS] Currently looking at a timetable!")
        
            prev_week_button = wait.until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    "button[data-ttb-action='CHANGE_DATE_PREV']"
                ))        
            )

            prev_week_button.click()

            wait.until(
                EC.invisibility_of_element_located((
                    By.ID,
                    "ttb_loading_dialog"
                ))
            )

            wait.until(
                EC.element_to_be_clickable((
                    By.CLASS_NAME,
                    "ttb_title"
                ))
            )

            currentDay = get_current_day_of_year(driver, wait)
            print("[LOGS] New day found! " + str(currentDay))

# Function used to grab the HTML data from the base timetable.
def extractTimetable(driver) -> str:
    timetable = driver.find_element(By.CLASS_NAME, "sitsjqttitems")
    timetableHTML = timetable.get_attribute("outerHTML")

    return timetableHTML
