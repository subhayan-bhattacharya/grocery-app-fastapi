"""Module for the pydantic models."""
import datetime

import pydantic
from pydantic import EmailStr, SecretStr


class Bucket(pydantic.BaseModel):
    """Base model for a grocery bucket."""

    name: str


class Token(pydantic.BaseModel):
    """Base model for an access token."""

    access_token: str
    token_type: str


class UserModel(pydantic.BaseModel):
    """Base model for a user."""

    name: str
    lastName: str
    email: EmailStr
    password: SecretStr


class UserModelWithId(UserModel):
    """Base model for user with user id."""

    id: int


class Entries(pydantic.BaseModel):
    """Base model for pydantic entries."""

    item_name: str
    category_name: str
    quantity: int
    description: str | None
    purchased: bool


class SuperMarket(pydantic.BaseModel):
    """Base model for a supermarket."""

    name: str


class Category(pydantic.BaseModel):
    """Base model for category."""

    name: str
    description: str
