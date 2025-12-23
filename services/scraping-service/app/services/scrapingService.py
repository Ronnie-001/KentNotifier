import os

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.dependencies import redis, baseTimetableKey

def getChromeDriver() -> WebDriver:
    # Set the options for the chrome driver that we will recieve.
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=chrome_options)

    return driver

""""
Set the driver to the return type so that we can access the current state (the logged in user) 
for other things.
"""
def loginToKentVision(email: str, password: str, user_id: int) -> WebDriver:
    kentVisionWebsite = "https://evision.kent.ac.uk/urd/sits.urd/run/siw_lgn" 

    # Init the webdriver for chrome
    driver = getChromeDriver()

    # Add explicit waits so next webpage can load properly
    wait = WebDriverWait(driver, timeout=30)
    
    # Set the current state of the user to 'logging in'
    redis.hset(f"user:{user_id}:state", mapping={
                    "status":"LOGGING_IN",
                    "mfa_code": "NULL",
               })

    # Navigate to the KentVision Application Portal.
    driver.get(kentVisionWebsite)
    studentApplicationPortalButton = driver.find_element(By.ID, "kent-student-login-button")
    studentApplicationPortalButton.click()
    print("[LOGS] Student and Staff Button clicked!")

    wait.until(
        EC.visibility_of_element_located((
        By.ID, 
        "i0116"
        ))
    )

    # Use provided email in the input field
    emailInput = driver.find_element(By.ID, "i0116")
    emailInput.send_keys(email)
    nextButton = driver.find_element(By.ID, "idSIButton9")
    nextButton.click()
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
    
    try:
        # Check if the 'Stay signed in? In on screen instead
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
                        "status":"MFA_WAITING",
                        "mfa_code": "NULL",
                   })

        return driver 

    except TimeoutException:
        print("[ERROR] Error when trying to log in! TimeoutException caught!")
        print("[LOGS] Checking if MFA page was seen instead...")
        
        takeScreenshot(driver)

        # Check if the MFA Code appears instead. 
        try:
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
    
            driver.implicitly_wait(20)

            takeScreenshot(driver)

            return driver

        except TimeoutException:
           print("[ERROR] Error when trying to log in! TimeoutException caught!")
           takeScreenshot(driver)
    
    except Exception as e:
        print("[ERROR] Ran into an error: " + str(e))
        takeScreenshot(driver)

    return driver

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
def takeScreenshot(driver):
    DEBUG_DIR = "/app/debug_output"
    os.makedirs(DEBUG_DIR, exist_ok=True) 

    # Take a screenshot of the current page.
    screen_shot_path = os.path.join(DEBUG_DIR, "debug.png")
    driver.save_screenshot(screen_shot_path)

    print(f"Path to the screenshot: {screen_shot_path}")   

"""
Function will return the HTML for the base timetable.
"""
def findBaseTimetable(driver, wait) -> str:
        
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

        currentDayofYear = getCurrentDayOfYear(driver, wait)

        print("[LOGS] Current days into the year: " + str(currentDayofYear))

        term1Start, term1End = 288, 357
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
        takeScreenshot(driver)

    return "NO TIMETABLE DATA"


"""
Function used to get the current day of the year on the 

"""
def getCurrentDayOfYear(driver, wait):

    wait.until(
        EC.visibility_of_element_located((
            By.CLASS_NAME,
            "sitsjqtttitle"
        ))
    )

    # Parse the page for the current dates at which the timetable displays for.
    timetableSubheading = driver.find_element(By.CLASS_NAME, "sitsjqtttitle")          
    currentDayofYear = calculateCurrentDayOfYear(timetableSubheading.text)

    return currentDayofYear

def calculateCurrentDayOfYear(text: str) -> int:
    """
    The map stores the cumuliative number of days BEFORE the month.
    This way, to calculate the day that the calendar is currently looking at,
    all that is needed is the day of the month + total number of days before
    the current month.
    """
    map = {
        "Jan": 0,
        "Feb": 31,
        "Mar": 59,
        "Apr": 90,
        "May": 120,
        "Jun": 151,
        "Jul": 181,
        "Aug": 212,
        "Sep": 243,
        "Oct": 273,
        "Nov": 304,
        "Dec": 334
    }

    # Grab the last 46 characters of the string and split it into an array.
    arr = text[-46:].split(" ")
    date = arr[3]

    # Convert the date into the number of days that you are into the year.
    dateArr = date.split("/")
    day, month = int(dateArr[0]), dateArr[1]
    totalDays = day + map[month]

    return totalDays

# Function used to find the first week of term (the base timetable)
def findBaseTimetableDate(currentDay, borderDay, driver, wait):
    while True:
        if currentDay - 7 < borderDay:
            print("[LOGS] Base timetable found!")
            break
        else:
            wait.until(
                EC.element_to_be_clickable((
                    By.ID,
                    "timetable_prev"
                ))
            )

            print("[LOGS] Currently looking at a timetable!")

            wait.until(
                EC.invisibility_of_element_located((
                    By.CLASS_NAME,
                    "ui-widget-overlay ui-front"
                ))
            )
        
            previousWeekButton = driver.find_element(By.ID, "timetable_prev") 
            previousWeekButton.click()

            currentDay = getCurrentDayOfYear(driver, wait)
            print("[LOGS] New day found! " + str(currentDay))

# Function used to grab the HTML data from the base timetable.
def extractTimetable(driver) -> str:
    timetable = driver.find_element(By.CLASS_NAME, "sitsjqttitems")
    timetableHTML = timetable.get_attribute("outerHTML")

    return timetableHTML
