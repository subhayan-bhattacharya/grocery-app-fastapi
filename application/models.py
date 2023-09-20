"""Module for the pydantic models."""
import pydantic


class GroceryEntries(pydantic.BaseModel):
    """Base model for pydantic entries."""
    item_name: str
    category_name: str
    quantity: int
    description: str
    purchased: bool
