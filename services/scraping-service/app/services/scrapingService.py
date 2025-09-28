from selenium import webdriver
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup

soup = BeautifulSoup()

""" 
TODO: implement manual login for selenium here.
Function will be used to return the HTML of the base timetable to store 
in the scraping service database.
"""
async def loginToKentVision(email: str, password: str) -> str:
    kentVisionWebsite = "https://evision.kent.ac.uk/urd/sits.urd/run/siw_lgn" 
    
    # Init the webdriver for chrome
    driver = webdriver.Chrome() 

    # Navigate to the KentVision Application Portal.
    driver.get(kentVisionWebsite)
    studentApplicationPortalButton = driver.find_element(By.ID, "kent-student-login-button")
    studentApplicationPortalButton.click()
    
    # Use provided email in the input field
    emailInput = driver.find_element(By.ID, "i0116")
    emailInput.send_keys(email)
    nextButton = driver.find_element(By.ID, "idSIButton9")
    nextButton.click()

    # Use provided password in the input field
    passwordInput = driver.find_element(By.ID, "i0118")
    passwordInput.send_keys(password) 
    signInButton = driver.find_element(By.ID, "idSIButton9")
    signInButton.click()

    # Check to see if the authenticator is there.
    authCheck = driver.find_element(By.ID, "idDiv_SAOTCAS_Title")

    if authCheck:
        print("SELE Working!")

    return ""
