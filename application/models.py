"""Module for the pydantic models."""
import functools
import os
from typing import Optional

import pydantic
from pydantic import EmailStr, Field, SecretStr


@functools.lru_cache()
def base_uri():
    return os.getenv("BASE_URI")


class BucketItemEntry(pydantic.BaseModel):
    """Base model for a grocery item entry."""

    item_id: Optional[int] = Field(exclude=True, default=None)
    name: Optional[str] = None
    category_id: Optional[int] = Field(exclude=True, default=None)
    category_name: Optional[str] = None
    bucket_id: int = Field(exclude=True)
    quantity: int
    description: str
    purchased: bool = False


class BucketItemEntryWithId(BucketItemEntry):
    """Base model for grocery item with id."""

    id: int = Field(exclude=True)
    link: Optional[str] = None

    def __init__(
        self,
        id,
        item_id,
        name,
        category_id,
        category_name,
        bucket_id,
        quantity,
        description,
        purchased,
    ):
        super().__init__(
            id=id,
            name=name,
            item_id=item_id,
            category_id=category_id,
            category_name=category_name,
            bucket_id=bucket_id,
            quantity=quantity,
            description=description,
            purchased=purchased,
            link=f"{base_uri()}/buckets/{bucket_id}/items/{id}",
        )


class Bucket(pydantic.BaseModel):
    """Base model for a grocery bucket."""

    name: str


class BucketWithId(Bucket):
    """Base model for bucket with id."""

    id: int = Field(exclude=True)
    link: Optional[str] = None

    def __init__(self, id, name):
        super().__init__(id=id, name=name, link=f"{base_uri()}/buckets/{id}")


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

    id: int = Field(exclude=True)


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


class SuperMarketWithId(SuperMarket):
    """Base model for supermarket with id."""

    id: int = Field(exclude=True)
    link: Optional[str] = None

    def __init__(self, id, name):
        super().__init__(id=id, name=name, link=f"{base_uri()}/supermarkets/{id}")


class Category(pydantic.BaseModel):
    """Base model for category."""

    name: str
    description: Optional[str] = None


class CategoryWithId(Category):
    """Base model for category with id."""

    id: int = Field(exclude=True)
    link: Optional[str] = None

    def __init__(self, id, description, name):
        super().__init__(
            id=id,
            name=name,
            description=description,
            link=f"{base_uri()}/categories/{id}",
        )
