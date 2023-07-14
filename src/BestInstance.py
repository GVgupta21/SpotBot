import pymongo
import ssl
import asyncio
import datetime
import json
from bson.json_util import dumps
# from pymongo import MongoClient
import certifi
ca = certifi.where()

client = pymongo.MongoClient("mongodb+srv://Cluster50748:c1JZR3FSQVxC@cluster50748.bzqz5gp.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=ca)
    # client = pymongo.MongoClient("mongodb+srv://Cluster50748:c1JZR3FSQVxC@cluster50748.bzqz5gp.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=ca)
db = client["Test_data"]
collection = db["Test_collection"]
ratio=input()
location=input()
exact_cpu=int(input())
min_cpu=int(input())
min_memory=int(input())
cloudProvider=input()
final_results=[]
validLocations = ['eastus', 'eastus2', 'westus', 'centralus', 'northcentralus', 'southcentralus', 'northeurope', 'westeurope', 'eastasia', 'southeastasia', 'japaneast', 'japanwest', 'australiaeast', 'australiasoutheast', 'australiacentral', 'brazilsouth', 'southindia', 'centralindia', 'westindia', 'canadacentral', 'canadaeast', 'westus2', 'westcentralus', 'uksouth', 'ukwest', 'koreacentral', 'koreasouth', 'francecentral', 'southafricanorth', 'uaenorth', 'switzerlandnorth', 'germanywestcentral', 'norwayeast', 'jioindiawest', 'westus3', 'swedencentral', 'qatarcentral', 'polandcentrl']
for loc in validLocations:
    if location in loc:
        if exact_cpu!=-1:
            query = {
                "Ratio": ratio,
                "Region": loc,
                "vCPU": exact_cpu,
                "Memory": {"$gte": min_memory},
                "TimeStamp": {"$gt": datetime.datetime.now() - datetime.timedelta(hours=1, minutes=30)},
                "CloudProvider":cloudProvider
            }
        else:
            query = {
                "Ratio": ratio,
                "Region": loc,
                "vCPU": {"$gte": min_cpu},
                "Memory": {"$gte": min_memory},
                "TimeStamp": {"$gt": datetime.datetime.now() - datetime.timedelta(hours=1, minutes=30)},
                "CloudProvider":cloudProvider
            }
        # Execute the query
        results = collection.find(query).sort("Price (Per Month)")
        # results = list(results)  # Convert the cursor to a list of results
        final_results.append(results)
        # final_results.extend(results)
# Create a dictionary to store the top three cheapest instances for each category
cheapest_instances = {}
# Iterate over the results and store the top three cheapest instances for each category
for results in final_results:
    for result in results:
        if "Category" in result:
            category = result["Category"]
            if category not in cheapest_instances:
                cheapest_instances[category] = []
            if len(cheapest_instances[category]) < 3:
                datta={
                    'InstanceType':result['InstanceType'],
                    'Price (Per Month)':result['Price (Per Month)']
                }
                if datta not in cheapest_instances[category]:
                    cheapest_instances[category].append(datta)
        else:
            print(-1)
# Print the top three cheapest instances for each category
cheapest_instances=json.dumps(cheapest_instances)
print(cheapest_instances)


# Close the MongoDB connection
client.close()