import pymongo
import ssl
import asyncio
import datetime
import json
from bson.json_util import dumps
# from pymongo import MongoClient
from google_sheets import upload_excel
import openpyxl
# from Category import catagorie
import certifi
import pandas as pd
from Check_google_sheet import check
# import pandas as pd
# import json

ca = certifi.where()

client = pymongo.MongoClient("mongodb+srv://Cluster50748:c1JZR3FSQVxC@cluster50748.bzqz5gp.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=ca)
db = client["Test_data"]
collection = db["Test_collection"]
ratio = input()
location = input()
exact_cpu = int(input())
min_cpu = int(input())
min_memory = int(input())
cloudProvider = input()
final_results = []
# print(f"{ratio} + {location} + {exact_cpu} + {min_cpu} + {min_memory} + {nvme}+ {cloudProvider}")
validLocations = ['ap-northeast-1a', 'ap-northeast-1c', 'ap-northeast-1d', 'ap-northeast-2a', 'ap-northeast-2b',
                  'ap-northeast-2c', 'ap-northeast-2d', 'ap-northeast-3a', 'ap-northeast-3b', 'ap-northeast-3c',
                  'ap-south-1a', 'ap-south-1b', 'ap-south-1c', 'ap-southeast-1a', 'ap-southeast-1b', 'ap-southeast-1c',
                  'ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c', 'ca-central-1a', 'ca-central-1b',
                  'ca-central-1d', 'eu-central-1a', 'eu-central-1b', 'eu-central-1c', 'eu-north-1a', 'eu-north-1b',
                  'eu-north-1c', 'eu-west-1a', 'eu-west-1b', 'eu-west-1c', 'eu-west-2a', 'eu-west-2b', 'eu-west-2c',
                  'eu-west-3a', 'eu-west-3b', 'eu-west-3c', 'sa-east-1a', 'sa-east-1b', 'sa-east-1c', 'us-east-1a',
                  'us-east-1b', 'us-east-1c', 'us-east-1d', 'us-east-1e', 'us-east-1f', 'us-east-2a', 'us-east-2b',
                  'us-east-2c', 'us-west-1a', 'us-west-1c', 'us-west-2a', 'us-west-2b', 'us-west-2c', 'us-west-2d']

for loc in validLocations:
    if location in loc:
        if exact_cpu != -1:
            query = {
                "Ratio": ratio,
                "Region": loc,
                "vCPU": exact_cpu,
                "Memory": {"$gte": min_memory},
                "TimeStamp": {"$gt": datetime.datetime.now() - datetime.timedelta(hours=1, minutes=30)},
                "CloudProvider": cloudProvider
            }
        else:
            query = {
                "Ratio": ratio,
                "Region": loc,
                "vCPU": {"$gte": min_cpu},
                "Memory": {"$gte": min_memory},
                "TimeStamp": {"$gt": datetime.datetime.now() - datetime.timedelta(hours=1, minutes=30)},
                "CloudProvider": cloudProvider
            }
        # Execute the query
        results = collection.find(query).sort("Price (Per Month)")
        final_results.append(results)

# Create a dictionary to store the cheapest instances for each category, chip type, and SSD
cheapest_instances = {}

# Iterate over the results and store the cheapest instances for each category, chip type, and SSD
if cloudProvider == "AWS":
    for results in final_results:
        for result in results:
            if "Category" in result:
                category = result["Category"]
                chip = result["Chip"]
                ssd = result["SSD"]
                size = result["vCPU"]
                instance_name = result["InstanceType"]
                price = result["Price (Per Month)"]

                if category not in cheapest_instances:
                    cheapest_instances[category] = {}

                if chip not in cheapest_instances[category]:
                    cheapest_instances[category][chip] = {}

                if ssd not in cheapest_instances[category][chip]:
                    cheapest_instances[category][chip][ssd] = {}

                if size not in cheapest_instances[category][chip][ssd]:
                    cheapest_instances[category][chip][ssd][size] = {
                        "Instance": instance_name,
                        "Price": price
                    }
                
            else:
                print(-1)

# Print the cheapest instances for each category, chip type, and SSD
cheapest_instances_json = json.dumps(cheapest_instances, indent=4)
print(cheapest_instances_json)
# catagorie(cheapest_instances_json)
# excel_file = '/Users/gaurav.gupta2/Documents/program/botbuilder-samples/samples/python/05.multi-turn-prompt/Spot_Price_Comparision.xlsx'

# adjust_column_width(excel_file)
# x=upload_excel(excel_file)
# if(check(x)):
#     print(x)
# else:
#     print('')
# Close the MongoDB connection
client.close()

