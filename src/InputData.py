import pymongo
import datetime
from pymongo import MongoClient
import certifi
import asyncio
from bson.json_util import dumps
import tracemalloc

tracemalloc.start()
ca = certifi.where()

async def insertData(data):
    client = pymongo.MongoClient("mongodb+srv://Cluster50748:c1JZR3FSQVxC@cluster50748.bzqz5gp.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=ca)
    # client = pymongo.MongoClient("mongodb+srv://Cluster50748:c1JZR3FSQVxC@cluster50748.bzqz5gp.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=ca)
    db = client["Test_data"]
    collection = db["alert_config"]
    # for document in data:
    inserted_document = collection.insert_one(data)
    # print("Inserted document ID:", inserted_document.inserted_id)
    client.close()
    return inserted_document.inserted_id

instanceRatio=input()
instanceLocation=input()
instancePrice=float(input())
UserId=input()
TeamName=input()
cloudProvider=input()
minCPU=int(input())
minMemory=int(input())
data={
    "ratio": instanceRatio,
    "price":instancePrice,
    "location": instanceLocation,
    "UserId":UserId,
    "TeamName":TeamName,
    "CloudProvider":cloudProvider,
    "minCPU":minCPU,
    "minMemory":minMemory
}
print(asyncio.run(insertData(data)))



