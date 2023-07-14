import pymongo
import certifi
import datetime
import json
from bson.json_util import dumps

cloud=input()
ratio=input()
location=input()
price_limit=float(input())
min_cpu=int(input())
min_memory=int(input())
ca = certifi.where()
# Connect to the MongoDB server
client = pymongo.MongoClient("mongodb+srv://Cluster50748:c1JZR3FSQVxC@cluster50748.bzqz5gp.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=ca)
db = client["Test_data"]
collection = db["Test_collection"]

# Retrieve data from MongoDB
final_results=[]
validLocations = ['ap-northeast-1a','ap-northeast-1c','ap-northeast-1d','ap-northeast-2a','ap-northeast-2b','ap-northeast-2c','ap-northeast-2d','ap-northeast-3a','ap-northeast-3b','ap-northeast-3c','ap-south-1a','ap-south-1b','ap-south-1c','ap-southeast-1a','ap-southeast-1b','ap-southeast-1c','ap-southeast-2a','ap-southeast-2b','ap-southeast-2c','ca-central-1a','ca-central-1b','ca-central-1d','eu-central-1a','eu-central-1b','eu-central-1c','eu-north-1a','eu-north-1b','eu-north-1c','eu-west-1a','eu-west-1b','eu-west-1c','eu-west-2a','eu-west-2b','eu-west-2c','eu-west-3a','eu-west-3b','eu-west-3c','sa-east-1a','sa-east-1b','sa-east-1c','us-east-1a','us-east-1b','us-east-1c','us-east-1d','us-east-1e','us-east-1f','us-east-2a','us-east-2b','us-east-2c','us-west-1a','us-west-1c','us-west-2a','us-west-2b','us-west-2c','us-west-2d']
for loc in validLocations:
    if location in loc:
        query = {"TimeStamp": {"$gt": datetime.datetime.now() - datetime.timedelta(hours=1, minutes=30)}, "CloudProvider": cloud,"Ratio": ratio,
                "Region": loc,
                "vCPU": {"$gte": min_cpu},
                "Memory": {"$gte": min_memory},
                "Price (Per Month)": {"$lte": price_limit}}
        results = (collection.find(query)).sort("Price (Per Month)")
        final_results.append(results)
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
# print(data)
