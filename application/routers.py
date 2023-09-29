"""Module for containing the routes of the application."""
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

import application.backend as backend
from application.models import Category, Entries, SuperMarket, Token, UserModel
from application.security import (ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM,
                                  SECRET_KEY, authenticate_user,
                                  create_access_token)

router = APIRouter()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = backend.BACKEND.get_a_user(email=email)
    if user is None:
        raise credentials_exception
    return user


@router.post("/users", response_model=UserModel, status_code=201)
def create_a_new_user(user: UserModel) -> UserModel:
    """Create a new user in the database."""
    try:
        return backend.BACKEND.add_a_new_user(user=user)
    except backend.BackendException as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.post(path="/login", response_model=Token)
def login_a_user(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login a user into the app."""
    try:
        user = authenticate_user(email=form_data.username, password=form_data.password)
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"email": user.email}, expires_delta=access_token_expires
        )
    except backend.IncorrectCredentials as error:
        raise HTTPException(status_code=401, detail="Incorrect user name or password!")

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/entries")
def get_grocery_entries() -> list[Entries]:
    """Get the current grocery entries which have not been purchased."""
    return backend.BACKEND.get_not_purchased_grocery_entries()


@router.post("/supermarkets", response_model=SuperMarket, status_code=201)
def create_a_supermarket_entry(supermarket: SuperMarket) -> SuperMarket:
    """Create an entry into the supermarket table."""
    try:
        return backend.BACKEND.add_a_supermarket(supermarket=supermarket)
    except backend.BackendException as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.get(path="/supermarkets", response_model=list[SuperMarket])
def get_supermarket_entries() -> list[SuperMarket]:
    """Get the list of supermarket entries."""
    return backend.BACKEND.get_the_list_of_supermarkets()


@router.post(path="/categories", response_model=Category, status_code=201)
def create_a_new_category(category: Category) -> Category:
    """Create a new category."""
    try:
        return backend.BACKEND.add_a_new_category(category=category)
    except backend.BackendException as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.get(path="/categories", response_model=list[Category])
def get_the_list_of_categories():
    """Get the list of all categories."""
    return backend.BACKEND.get_all_the_categories()
