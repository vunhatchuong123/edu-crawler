import os
import pprint

from dotenv import find_dotenv, load_dotenv
from pymongo import MongoClient

load_dotenv(find_dotenv())

password = os.environ.get("MONGODB_PWD")

connection_string = f"mongodb://Crawleradmin:{password}@localhost:27017/edu-crawler"

db = MongoClient(connection_string).get_database("edu-crawler")

collection = db.get_collection("edu2review")

date_str = "29-03-2021"

user = {
    "school": "SIU",
    "user_id": "userid",
    "date": "date",
    "comment": "comment",
}
posts = collection.insert_one(user)
