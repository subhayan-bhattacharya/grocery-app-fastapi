"""Routes related to supermarket."""
from fastapi import HTTPException

import application.backend as backend
from application.models import SuperMarket


def create_a_supermarket_entry(supermarket: SuperMarket) -> SuperMarket:
    """Create an entry into the supermarket table."""
    try:
        return backend.BACKEND.add_a_supermarket(supermarket=supermarket)
    except backend.BackendException as error:
        raise HTTPException(status_code=400, detail=str(error))


def get_supermarket_entries() -> list[SuperMarket]:
    """Get the list of supermarket entries."""
    return backend.BACKEND.get_the_list_of_supermarkets()
