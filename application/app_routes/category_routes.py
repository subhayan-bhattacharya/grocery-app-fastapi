"""Module to deal with routes related to a category."""
import functools
import os
from typing import Annotated

from fastapi import HTTPException, Depends

from application.backend import instantiate_backend, ResourceNotFound, BackendException
from application.backend import category_backend
from application.models import CategoryWithId, Category


@functools.cache
def get_category_backend() -> category_backend.BackendCategory:
    """Instantiate the category backend."""
    return instantiate_backend(
        sqlite_db_path=os.getenv("DB_FILE"),
        backend_class=category_backend.BackendCategory,
    )


def create_a_new_category(
    category: Category,
    backend: Annotated[category_backend.BackendCategory, Depends(get_category_backend)],
) -> CategoryWithId:
    """Create a new category."""
    try:
        return backend.add_a_new_category(category=category)
    except BackendException as error:
        raise HTTPException(status_code=400, detail=str(error))


def get_the_list_of_categories(
    backend: Annotated[category_backend.BackendCategory, Depends(get_category_backend)],
) -> list[CategoryWithId]:
    """Get the list of all categories."""
    return backend.get_all_the_categories()


def get_a_single_category(
    category_id: int,
    backend: Annotated[category_backend.BackendCategory, Depends(get_category_backend)],
) -> CategoryWithId:
    """Get the details of a single category."""
    try:
        return backend.get_a_single_category(category_id=category_id)
    except ResourceNotFound as error:
        raise HTTPException(detail=str(error), status_code=404)


def delete_a_category(
    category_id: int,
    backend: Annotated[category_backend.BackendCategory, Depends(get_category_backend)],
):
    """Delete a single category."""
    try:
        backend.delete_a_single_category(category_id=category_id)
    except ResourceNotFound as error:
        raise HTTPException(detail=str(error), status_code=404)
