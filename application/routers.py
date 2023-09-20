"""Module for containing the routes of the application."""
from application.models import GroceryEntries
from fastapi import APIRouter

router = APIRouter()


@router.get("/entries")
def get_grocery_entries() -> GroceryEntries:
    """Get the current grocery entries which have not been purchased."""
