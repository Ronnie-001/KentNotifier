from fastapi import APIRouter
from app.dependencies import redis

statusRouter = APIRouter()

"""
Define a router that will be used to check the state of the redis
K/V store, so that polling can be used on the frontend to get the user's 
MFA code.
"""
@statusRouter.post("/scraping-service/v1/login-status/{userID}")
def checkLoginStatus(user_id: str):
    # Grab the user dict
    user_dict = redis.hgetall(f"user:{user_id}:state")
    return user_dict
