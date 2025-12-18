from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.routes import BaseTimetableRouter, scrapingRouter
from app.database.dbconn import Base, engine

# Mainly used for testing purposes
async def DropAndCreateDbTables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


# Bind all the tables to the engine so that the tables will be created.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create and drop the database
    await DropAndCreateDbTables()
     
    # everything after 'yeild' is what happens when the application shuts down
    yield

app = FastAPI(lifespan=lifespan)

# include the different routers.
app.include_router(BaseTimetableRouter.detailsRouter)
app.include_router(scrapingRouter.scrapingRouter)

# test endpoint
@app.get("/scraping-service/v1/test")
async def root():
    return {"test": "Working"}
