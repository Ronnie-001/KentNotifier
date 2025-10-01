import os
import time

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

soup = BeautifulSoup()

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
    try:
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

        signInButtonClicked = await clickElement("idSIButton9", driver)
        if signInButtonClicked:
            print("[LOGS] Sign in button clicked!")
    
        # Check to see if the authenticator is there.
        print("[LOGS] Waiting for the MFA prompt to appear...")

        wait = WebDriverWait(driver, timeout=20)

        authCheck = wait.until(
            EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Approve sign in request')]")) 
        )

        print("[LOGS] The MFA Page found!")

    except StaleElementReferenceException as e:
        print("[ERROR] Error when trying to log in! StaleElementReferenceException caught!")
        
        DEBUG_DIR = "/app/debug_output"
        os.makedirs(DEBUG_DIR, exist_ok=True) 

        # Take a screenshot of the current page.
        screen_shot_path = os.path.join(DEBUG_DIR, "debug.png")
        driver.save_screenshot(screen_shot_path)

        print(f"Path to the screenshot: {screen_shot_path}")

    return ""

"""
Use to avoid StaleElementReferenceExceptions when clicking an element,
most likley caused due to rapid changes in the DOM.
"""
async def clickElement(id: str, driver) -> bool:
    result = False
    attempts = 0
    while attempts < 5:
        try:
            button = driver.find_element(By.ID, id)
            button.click()
            result = True
            break
        except StaleElementReferenceException: 
            pass
        attempts += 1

    return result;
