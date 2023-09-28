"""Module for containing the routes of the application."""
from fastapi import APIRouter

import application.backend as backend
from application.models import Category, Entries, SuperMarket

router = APIRouter()


@router.get("/entries")
def get_grocery_entries() -> list[Entries]:
    """Get the current grocery entries which have not been purchased."""
    return backend.BACKEND.get_not_purchased_grocery_entries()


@router.post("/supermarkets", response_model=SuperMarket, status_code=201)
def create_a_supermarket_entry(supermarket: SuperMarket) -> SuperMarket:
    """Create an entry into the supermarket table."""
    return backend.BACKEND.add_a_supermarket(supermarket=supermarket)


@router.get(path="/supermarkets", response_model=list[SuperMarket])
def get_supermarket_entries() -> list[SuperMarket]:
    """Get the list of supermarket entries."""
    return backend.BACKEND.get_the_list_of_supermarkets()


@router.post(path="/categories", response_model=Category, status_code=201)
def create_a_new_category(category: Category) -> Category:
    """Create a new category."""
    return backend.BACKEND.add_a_new_category(category=category)


@router.get(path="/categories", response_model=list[Category])
def get_the_list_of_categories():
    """Get the list of all categories."""
    return backend.BACKEND.get_all_the_categories()
