import pymongo
import ssl
import asyncio
import datetime
import json
from bson.json_util import dumps
# from pymongo import MongoClient
from google_sheets import upload_excel
import openpyxl
from Category import catagorie
import certifi
import pandas as pd

def adjust_column_width(excel_file):
    """
    Adjusts the column width in the Excel file to accommodate the data entered.

    Args:
        excel_file: The path to the Excel file.

    Returns:
        None
    """
    # Load the Excel file
    workbook = openpyxl.load_workbook(excel_file)

    # Iterate over all sheets in the workbook
    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]
        
        # Adjust the column width for each column
        for column in sheet.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except TypeError:
                    pass
            adjusted_width = (max_length + 2) * 1.2
            sheet.column_dimensions[column[0].column_letter].width = adjusted_width

    # Save the changes to the Excel file
    workbook.save(excel_file)

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
# excel_file = '/Users/gaurav.gupta2/Documents/program/progs/formatted_data.xlsx'

# adjust_column_width(excel_file)
# print(upload_excel(excel_file))
# Close the MongoDB connection
client.close()
