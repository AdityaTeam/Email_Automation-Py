from pymongo import MongoClient

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['email_generator']
collection = db['emails']

# Check if database and collection exist
print("Databases:", client.list_database_names())
print("Collections in email_generator:", db.list_collection_names())

# Check if any documents exist
count = collection.count_documents({})
print(f"Number of documents in emails collection: {count}")

# If documents exist, print one
if count > 0:
    print("Sample document:", collection.find_one())
