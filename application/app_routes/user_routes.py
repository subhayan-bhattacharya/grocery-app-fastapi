"""Contains the routes related to adding or logging in a user."""
import functools
import os
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

import application.backend.user_backend as user_backend
from application.backend import BackendException, instantiate_backend
from application.models import Bucket, BucketWithId, UserModel, UserModelWithId

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 2

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@functools.cache
def get_user_backend() -> user_backend.UserBackend:
    """Instantiate the category backend."""
    return instantiate_backend(
        sqlite_db_path=os.getenv("DB_FILE"),
        backend_class=user_backend.UserBackend,
    )


def authenticate_user(backend: user_backend.UserBackend, email: str, password: str):
    """Authenticate the user using email and password."""
    try:
        user = backend.get_a_user(email=email)
        backend.check_password_of_user(user=user, password=password)
        return user
    except user_backend.IncorrectCredentials as error:
        raise error


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserModelWithId:
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
    backend = get_user_backend()
    user = backend.get_a_user(email=email)
    if user is None:
        raise credentials_exception
    return user


def create_a_new_user(
    user: UserModel,
    backend: Annotated[user_backend.UserBackend, Depends(get_user_backend)],
) -> UserModel:
    """Create a new user in the database."""
    try:
        return backend.add_a_new_user(user=user)
    except BackendException as error:
        raise HTTPException(status_code=400, detail=str(error))


def login_a_user(
    backend: Annotated[user_backend.UserBackend, Depends(get_user_backend)],
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """Login a user into the app."""
    try:
        user = authenticate_user(
            backend=backend, email=form_data.username, password=form_data.password
        )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"email": user.email}, expires_delta=access_token_expires
        )
    except user_backend.IncorrectCredentials as error:
        raise HTTPException(status_code=401, detail="Incorrect user name or password!")

    return {"access_token": access_token, "token_type": "bearer"}


def create_a_grocery_bucket_for_the_user(
    bucket: Bucket,
    current_user: Annotated[
        UserModelWithId,
        Depends(get_current_user),
    ],
    backend: Annotated[user_backend.UserBackend, Depends(get_user_backend)],
) -> BucketWithId:
    """Creates a grocery bucket of the logged-in user."""
    try:
        return backend.create_a_grocery_bucket(bucket=bucket, user=current_user)
    except BackendException as error:
        raise HTTPException(status_code=400, detail=str(error))


def get_the_list_of_buckets_for_the_logged_in_user(
    current_user: Annotated[
        UserModelWithId,
        Depends(get_current_user),
    ],
    backend: Annotated[user_backend.UserBackend, Depends(get_user_backend)],
) -> list[BucketWithId]:
    """Gets the list of buckets that the user created."""
    return backend.get_all_buckets_for_user(user=current_user)
