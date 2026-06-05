from datetime import datetime
from bson.objectid import ObjectId


MAX_BATCHES_PER_USER = 3


def can_allocate_batch(
        batches_collection,
        username):

    count = batches_collection.count_documents({
        "allocated_to": username
    })

    return count < MAX_BATCHES_PER_USER


def allocate_batch(
        batches_collection,
        batch_id,
        username):

    batch = batches_collection.find_one({
        "_id": ObjectId(batch_id)
    })

    if not batch:
        return False, "Batch not found"

    if batch.get("allocated_to"):
        return False, "Batch already allocated"

    if not can_allocate_batch(
            batches_collection,
            username):
        return False, "Maximum 3 batches allowed"

    batches_collection.update_one(
        {
            "_id": ObjectId(batch_id)
        },
        {
            "$set": {
                "allocated_to": username,
                "status": "Allocated",
                "allocated_at": datetime.now()
            }
        }
    )

    return True, "Batch allocated successfully"


def release_batch(
        batches_collection,
        batch_id):

    batches_collection.update_one(
        {
            "_id": ObjectId(batch_id)
        },
        {
            "$set": {
                "allocated_to": None,
                "status": "Available"
            }
        }
    )

    return True


def get_user_batches(
        batches_collection,
        username):

    return list(
        batches_collection.find({
            "allocated_to": username
        })
    )