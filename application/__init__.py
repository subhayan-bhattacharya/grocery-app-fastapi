"""Main module for the fastapi app."""
import os
import pathlib
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

import application.routers as routers
from application.backend import instantiate_backend


@asynccontextmanager
async def lifespan(app: FastAPI):
    # load the environment from the file app.env in the project directory
    basedir = pathlib.Path(__file__).parent.parent
    load_dotenv(basedir / "app.env")
    instantiate_backend(sqlite_db_path=os.getenv("DB_FILE"))
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(routers.router)
