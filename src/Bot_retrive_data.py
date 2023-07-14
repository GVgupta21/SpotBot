import pymongo
import ssl
import asyncio
import datetime
import json
from pymongo import MongoClient
import certifi
from bson.json_util import dumps

ca = certifi.where()
    # Connect to MongoDB
    # client = MongoClient()


# Insert a document  c1JZR3FSQVxC
async def insertData(data):
    client = pymongo.MongoClient("mongodb+srv://Cluster50748:c1JZR3FSQVxC@cluster50748.bzqz5gp.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=ca)
    # client = pymongo.MongoClient("mongodb+srv://Cluster50748:c1JZR3FSQVxC@cluster50748.bzqz5gp.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=ca)
    db = client["Test_data"]
    collection = db["Test_collection"]
    for document in data:
        inserted_document = collection.insert_one(document)
    # print("Inserted document ID:", inserted_document.inserted_id)
    client.close()

def retrieveData(instance_location,instance_ratio,price):
    # Find documents
    client = pymongo.MongoClient("mongodb+srv://Cluster50748:c1JZR3FSQVxC@cluster50748.bzqz5gp.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=ca)
    db = client["Test_data"]
    collection = db["Test_collection"]
    documents = collection.find()
    flag=0
    for document in documents:
        if document['Region']==instance_location and document['Ratio']==instance_ratio and document['Price']<price:
            flag=1
            print(flag)
    client.close()
    return flag

def printDataAWS():
    # print("hii")
    client = pymongo.MongoClient("mongodb+srv://Cluster50748:c1JZR3FSQVxC@cluster50748.bzqz5gp.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=ca)
    db = client["Test_data"]
    collection = db["Test_collection"]
    # documents=collection.find()
    query = {"TimeStamp": {"$gt": datetime.datetime.now() - datetime.timedelta(hours=1, minutes=30)}, "CloudProvider": "AWS"}
    documents = collection.find(query)

    list_cur = list(documents)
    json_data = dumps(list_cur, indent=2)
    client.close()
    # print(datetime.datetime.now() -datetime.timedelta(hours=1))
    return json_data
def printDataAzure():
    # print("hii")
    client = pymongo.MongoClient("mongodb+srv://Cluster50748:c1JZR3FSQVxC@cluster50748.bzqz5gp.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=ca)
    db = client["Test_data"]
    collection = db["Test_collection"]
    # documents=collection.find()
    query = {"TimeStamp": {"$gt": datetime.datetime.now() - datetime.timedelta(hours=1, minutes=30)}, "CloudProvider": "Azure"}
    documents = collection.find(query)

    list_cur = list(documents)
    json_data = dumps(list_cur, indent=2)
    client.close()
    # print(datetime.datetime.now() -datetime.timedelta(hours=1))
    return json_data

