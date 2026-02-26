from typing import Annotated
from fastapi import APIRouter, Header, HTTPException
from app.dependencies import redis

statusRouter = APIRouter()

"""
Define a router that will be used to check the state of the redis
K/V store, so that polling can be used on the frontend to get the user's 
MFA code.
"""
@statusRouter.get("/scraping-service/v1/login-status/{userID}")
def checkLoginStatus(user_id: str, Authorization: Annotated[str | None, Header()] = None):

    # Check is the Auth header is there
    jwt_exception = HTTPException(
        status_code=401,
        detail="Could not extract the JWT from the 'Authorization' header.",
        headers={"WWW-Authenticate" : "Bearer"},
    )
    
    if Authorization is None:
        raise jwt_exception

    # Grab the user dict
    user_dict = redis.hgetall(f"user:{user_id}:state")
    return user_dict
