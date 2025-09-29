from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup

soup = BeautifulSoup()

# TODO: Set the opotions for the chromedriver needed.
async def getChromeDriver():
    # Set the options for the chrome driver that we will recieve.
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=chrome_options)

    return driver

""" 
TODO: implement manual login for selenium here.
Function will be used to return the HTML of the base timetable to store 
in the scraping service database.
"""
async def loginToKentVision(email: str, password: str) -> str:
    kentVisionWebsite = "https://evision.kent.ac.uk/urd/sits.urd/run/siw_lgn" 
    
    # Init the webdriver for chrome
    driver = await getChromeDriver()

    # Navigate to the KentVision Application Portal.
    driver.get(kentVisionWebsite)
    studentApplicationPortalButton = driver.find_element(By.ID, "kent-student-login-button")
    studentApplicationPortalButton.click()
    print("[LOGS] Application Portal Button clicked!")
    
    # Make selenium wait
    driver.implicitly_wait(3)

    # Use provided email in the input field
    emailInput = driver.find_element(By.ID, "i0116")
    emailInput.send_keys(email)
    nextButton = driver.find_element(By.ID, "idSIButton9")
    nextButton.click()
    print("[LOGS] Next button clicked!")
    
    driver.implicitly_wait(3)

    # Use provided password in the input field
    passwordInput = driver.find_element(By.ID, "i0118")
    passwordInput.send_keys(password) 

    signInButtonIsClicked = clickElement("idSIButton9", driver)
    if signInButtonIsClicked:
        print("[LOGS] Sign in button clicked!")
    
    driver.implicitly_wait(20)

    # Check to see if the authenticator is there.
    try:
        authCheck = driver.find_element(By.ID, "idDiv_SAOTCAS_Title")
        print("Element exists!")
    except Exception as e:
        print("Element not found!")

    return ""

"""
Use to avoid StaleElementReferenceExceptions when clicking an element,
most likley caused due to rapid changes in the DOM.
"""
async def clickElement(id: str, driver) -> bool:
    result = False
    attempts = 0
    while attempts < 2:
        try:
            button = driver.find_element(By.ID, id)
            button.click()
            result = True
            break
        except StaleElementReferenceException: 
            pass
        attempts += 1

    return result;
