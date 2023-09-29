"""Module for the pydantic models."""
import pydantic
from pydantic import EmailStr, SecretStr


class Token(pydantic.BaseModel):
    access_token: str
    token_type: str


class UserModel(pydantic.BaseModel):
    """Base model for a user."""

    name: str
    lastName: str
    email: EmailStr
    password: SecretStr


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
