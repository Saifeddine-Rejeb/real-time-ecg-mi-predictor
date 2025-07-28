from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

import os
import dotenv

dotenv.load_dotenv('.env')

client = MongoClient(os.getenv('MONGO_URI'), server_api=ServerApi('1'))
db = client[os.getenv('DB_NAME')]


try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Ensure the database connection is established
try:
    db.test_collection.find_one()
    print("Database is usable.")
except Exception as e:
    print("Database is not usable:", e)



# # --- TEST: Create Users collection and add a user ---
# users = db.Users  

# # Example user document
# user_doc = {
#     "name": "Test User",
#     "email": "testuser@example.com",
#     "password_hash": "hashedpassword123",
#     "type": "admin"
# }

# insert_result = users.insert_one(user_doc)
# print(f"Inserted user with _id: {insert_result.inserted_id}")

# # Fetch and print the user
# fetched_user = users.find_one({"_id": insert_result.inserted_id})
# print("Fetched user:", fetched_user)