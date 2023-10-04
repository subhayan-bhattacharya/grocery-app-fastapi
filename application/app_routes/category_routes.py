"""Module to deal with routes related to a category."""
from fastapi import HTTPException

import application.backend as backend
from application.models import CategoryWithId, Category


def create_a_new_category(category: Category) -> CategoryWithId:
    """Create a new category."""
    try:
        return backend.BACKEND.add_a_new_category(category=category)
    except backend.BackendException as error:
        raise HTTPException(status_code=400, detail=str(error))


def get_the_list_of_categories() -> list[CategoryWithId]:
    """Get the list of all categories."""
    return backend.BACKEND.get_all_the_categories()


def get_a_single_category(category_id: int) -> CategoryWithId:
    """Get the details of a single category."""
    try:
        return backend.BACKEND.get_a_single_category(category_id=category_id)
    except backend.ResourceNotFound as error:
        raise HTTPException(detail=str(error), status_code=404)


def delete_a_category(category_id: int):
    """Delete a single category."""
    try:
        backend.BACKEND.delete_a_single_category(category_id=category_id)
    except backend.ResourceNotFound as error:
        raise HTTPException(detail=str(error), status_code=404)
