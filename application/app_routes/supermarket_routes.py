"""Routes related to supermarket."""
import functools
import os
from typing import Annotated

from fastapi import HTTPException, Depends

from application.backend import instantiate_backend, BackendException
from application.backend import supermarket_backend
from application.models import SuperMarket


@functools.cache
def get_supermarket_backend() -> supermarket_backend.SupermarketBackend:
    """Instantiate the category backend."""
    return instantiate_backend(
        sqlite_db_path=os.getenv("DB_FILE"),
        backend_class=supermarket_backend.SupermarketBackend,
    )


def create_a_supermarket_entry(
    supermarket: SuperMarket,
    backend: Annotated[
        supermarket_backend.SupermarketBackend, Depends(get_supermarket_backend)
    ],
) -> SuperMarket:
    """Create an entry into the supermarket table."""
    try:
        return backend.add_a_supermarket(supermarket=supermarket)
    except BackendException as error:
        raise HTTPException(status_code=400, detail=str(error))


def get_supermarket_entries(
    backend: Annotated[
        supermarket_backend.SupermarketBackend, Depends(get_supermarket_backend)
    ]
) -> list[SuperMarket]:
    """Get the list of supermarket entries."""
    return backend.get_the_list_of_supermarkets()
