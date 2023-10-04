"""Module for dealing with grocery entries."""
from application.models import BucketItemEntry
import application.backend as backend


def add_a_grocery_entry(bucket_id: int, entry: BucketItemEntry) -> BucketItemEntry:
    """Add an entry to a bucket."""
    return backend.BACKEND.add_a_grocery_entry(bucket_id=bucket_id, entry=entry)
