import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

CONNECTION_STRING = os.getenv("MONGODB_STRING")
DATABASE = os.getenv("MONGODB_DB")

db = MongoClient(CONNECTION_STRING).get_database(DATABASE)

collection = db.get_collection("edu2review")

date_str = "29-03-2021"

user = {
    "_id": "user-review-209212",
    "school": "SIU",
    "user_id": "userid",
    "date": "date",
    "comment": "comment",
}
# print(type(user))
posts = collection.insert_one(user)
