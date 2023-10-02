"""Module to deal with routes related to a category."""
from fastapi import HTTPException

import application.backend as backend
from application.models import Category


def create_a_new_category(category: Category) -> Category:
    """Create a new category."""
    try:
        return backend.BACKEND.add_a_new_category(category=category)
    except backend.BackendException as error:
        raise HTTPException(status_code=400, detail=str(error))


def get_the_list_of_categories():
    """Get the list of all categories."""
    return backend.BACKEND.get_all_the_categories()
