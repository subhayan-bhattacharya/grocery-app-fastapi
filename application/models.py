"""Module for the pydantic models."""
import pydantic


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
