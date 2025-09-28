from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routes import DetailsRouter, ScrapingRouter
from app.database.dbconn import Base, engine


# Bind all the tables to the engine so that the tables will be created.
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

# include the different routers.
app.include_router(DetailsRouter.detailsRouter)
app.include_router(ScrapingRouter.scrapingRouter)

# test endpoint
@app.get("/scraping-service/v1/test")
async def root():
    return {"test": "Working"}
