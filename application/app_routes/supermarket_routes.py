"""Routes related to supermarket."""
import functools
import os
from typing import Annotated

from fastapi import HTTPException, Depends

from application.backend import instantiate_backend, BackendException, ResourceNotFound
from application.backend import supermarket_backend
from application.models import SuperMarketWithId


@functools.cache
def get_supermarket_backend() -> supermarket_backend.SupermarketBackend:
    """Instantiate the category backend."""
    return instantiate_backend(
        sqlite_db_path=os.getenv("DB_FILE"),
        backend_class=supermarket_backend.SupermarketBackend,
    )


def create_a_supermarket_entry(
    supermarket: SuperMarketWithId,
    backend: Annotated[
        supermarket_backend.SupermarketBackend, Depends(get_supermarket_backend)
    ],
) -> SuperMarketWithId:
    """Create an entry into the supermarket table."""
    try:
        return backend.add_a_supermarket(supermarket=supermarket)
    except BackendException as error:
        raise HTTPException(status_code=400, detail=str(error))


def get_supermarket_entries(
    backend: Annotated[
        supermarket_backend.SupermarketBackend, Depends(get_supermarket_backend)
    ]
) -> list[SuperMarketWithId]:
    """Get the list of supermarket entries."""
    return backend.get_the_list_of_supermarkets()


def get_a_single_supermarket(
    supermarket_id: int,
    backend: Annotated[
        supermarket_backend.SupermarketBackend, Depends(get_supermarket_backend)
    ],
) -> SuperMarketWithId:
    """Get the details of a single supermarket."""
    try:
        return backend.get_a_single_supermarket(supermarket_id=supermarket_id)
    except ResourceNotFound as error:
        raise HTTPException(detail=str(error), status_code=404)


def delete_a_supermarket(
    supermarket_id: int,
    backend: Annotated[
        supermarket_backend.SupermarketBackend, Depends(get_supermarket_backend)
    ],
):
    """Delete a single supermarket."""
    try:
        backend.delete_a_supermarket(supermarket_id=supermarket_id)
    except ResourceNotFound as error:
        raise HTTPException(detail=str(error), status_code=404)
