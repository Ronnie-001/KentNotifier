from fastapi import APIRouter
from app.dependencies import redis


statusRouter = APIRouter()

"""
Define a router that will be used to check the state of the redis
K/V store,
"""

@statusRouter.post("/scraping-service/v1/login-status/{userID}")
def checkLoginStatus():
    pass    
