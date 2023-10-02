"""Main module for the fastapi app."""
import os
import pathlib
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from application.app_routes.bucket_routes import (
    create_a_grocery_bucket, get_the_list_of_buckets_for_the_logged_in_user)
from application.app_routes.category_routes import (create_a_new_category,
                                                    get_the_list_of_categories)
from application.app_routes.supermarket_routes import (
    create_a_supermarket_entry, get_supermarket_entries)
from application.app_routes.user_routes import create_a_new_user, login_a_user
from application.backend import instantiate_backend
from application.models import Bucket, Category, SuperMarket, Token, UserModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    # load the environment from the file app.env in the project directory
    basedir = pathlib.Path(__file__).parent.parent
    load_dotenv(basedir / "app.env")
    instantiate_backend(sqlite_db_path=os.getenv("DB_FILE"))
    yield


app = FastAPI(lifespan=lifespan)

# The below section is to avoid circular imports

# User routes
create_a_new_user = app.post("/users", response_model=UserModel, status_code=201)(
    create_a_new_user
)
login_a_user = app.post(path="/login", response_model=Token)(login_a_user)

# bucket routes
get_the_list_of_buckets_for_the_logged_in_user = app.get(
    "/buckets", response_model=list[Bucket], status_code=200
)(get_the_list_of_buckets_for_the_logged_in_user)
create_a_grocery_bucket = app.post("/buckets", response_model=Bucket, status_code=201)(
    create_a_grocery_bucket
)

# category routes
get_the_list_of_categories = app.get(path="/categories", response_model=list[Category])(
    get_the_list_of_categories
)
create_a_new_category = app.post(
    path="/categories", response_model=Category, status_code=201
)(create_a_new_category)

# supermarket routes
create_a_supermarket_entry = app.post(
    "/supermarkets", response_model=SuperMarket, status_code=201
)(create_a_supermarket_entry)
get_supermarket_entries = app.get(
    path="/supermarkets", response_model=list[SuperMarket]
)(get_supermarket_entries)
