"""Routes dealing with creating/deleting a user bucket."""
from typing import Annotated

from fastapi import Depends, HTTPException

import application.backend as backend
from application.app_routes.security import get_current_user
from application.models import Bucket, UserModelWithId


def create_a_grocery_bucket(
    bucket: Bucket, current_user: Annotated[UserModelWithId, Depends(get_current_user)]
) -> Bucket:
    """Creates a grocery bucket of the logged in user."""
    try:
        return backend.BACKEND.create_a_grocery_bucket(bucket=bucket, user=current_user)
    except backend.BackendException as error:
        raise HTTPException(status_code=400, detail=str(error))


def get_the_list_of_buckets_for_the_logged_in_user(
    current_user: Annotated[UserModelWithId, Depends(get_current_user)]
):
    """Gets the list of buckets that the user created."""
    return backend.BACKEND.get_all_buckets_for_user(user=current_user)


def delete_a_bucket(
    current_user: Annotated[UserModelWithId, Depends(get_current_user)]
):
    """Delete a bucket of the logged in user."""
    pass
