"""Contains the routes related to adding or logging in a user."""
from datetime import timedelta

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

import application.backend as backend
from application.app_routes.security import (ACCESS_TOKEN_EXPIRE_MINUTES,
                                             authenticate_user,
                                             create_access_token)
from application.models import UserModel


def create_a_new_user(user: UserModel) -> UserModel:
    """Create a new user in the database."""
    try:
        return backend.BACKEND.add_a_new_user(user=user)
    except backend.BackendException as error:
        raise HTTPException(status_code=400, detail=str(error))


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
