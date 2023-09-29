"""Module for security."""

from datetime import datetime, timedelta

from jose import jwt

import application.backend as backend

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 2


def authenticate_user(email: str, password: str):
    """Authenticate the user using email and password."""
    try:
        user = backend.BACKEND.get_a_user(email=email)
        backend.BACKEND.check_password_of_user(user=user, password=password)
        return user
    except backend.IncorrectCredentials as error:
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
