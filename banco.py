import os
from dotenv import load_dotenv
from pymongo import MongoClient
load_dotenv()
url=os.getenv("URL")
client=MongoClient(url)
try:
    client.admin.command("ping")
    print("Connected successfully")
    client.close()
except Exception as e:
    raise Exception(
        "The following error occurred: ", e)