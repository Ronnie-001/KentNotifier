import redis
from app.database.dbconn import Session

# create a single session / database connection for each request
async def getDb():
    async with Session() as session:
        yield session

# Configure the redis server
redis_server = redis.Redis(
    host='redis', 
    port=6379, 
    decode_responses=True)

baseTimetableKey = "hasBaseTimetable"
