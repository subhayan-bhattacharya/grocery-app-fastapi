"""Module for containing the routes of the application."""
from fastapi import APIRouter

import application.backend as backend
from application.models import Entries

router = APIRouter()


@router.get("/entries")
def get_grocery_entries() -> list[Entries]:
    """Get the current grocery entries which have not been purchased."""
    return backend.BACKEND.get_not_purchased_grocery_entries()
