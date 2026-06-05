from datetime import datetime


def log_action(
        audit_collection,
        username,
        action,
        target):

    audit_collection.insert_one({

        "username": username,

        "action": action,

        "target": target,

        "timestamp": datetime.now()

    })