import json
import pymongo


client = pymongo.MongoClient()
db = client["etl"]
col = db["currencies"]

with open('../transform/transformed_data.json') as file:
    data = json.load(file)
try:
    col.insert_many(data)
except pymongo.errors.BulkWriteError:
    print("duplicates!!!")

client.close()
