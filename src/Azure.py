import requests
import json
import math
import datetime
import asyncio
from Bot_retrive_data import insertData
from fractions import Fraction
from azure.identity import DefaultAzureCredential
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.compute import ComputeManagementClient
# import os

# # Set the Azure credentials as environment variables
# os.environ["AZURE_TENANT_ID"] = "71dbb522-5704-4537-9f25-6ad2dcd4278d"
# os.environ["AZURE_CLIENT_ID"] = "04a5ffcf-2682-4a0c-8ccf-c9b37d460ef9"
# os.environ["AZURE_CLIENT_SECRET"] = "BrR8Q~oQOtc3VCWlzeduAIgx7ugSDSJ3AP5Nwc02"
# os.environ["AZURE_SUBSCRIPTION_ID"] = "24bef186-cea0-46f2-96ec-350c96f8c268"
# # client_id = '04a5ffcf-2682-4a0c-8ccf-c9b37d460ef9'  # Replace with your managed identity's object ID
# from azure.identity import ClientSecretCredential

# tenant_id = '71dbb522-5704-4537-9f25-6ad2dcd4278d'
# client_id = '04a5ffcf-2682-4a0c-8ccf-c9b37d460ef9'
# client_secret = 'BrR8Q~oQOtc3VCWlzeduAIgx7ugSDSJ3AP5Nwc02'

credential = DefaultAzureCredential()
currentTime=datetime.datetime.now()
print(currentTime)
subscription_id = '24bef186-cea0-46f2-96ec-350c96f8c268'
subscription_client = SubscriptionClient(credential)
# locations = subscription_client.subscriptions.list_locations(subscription_id)
compute_client = ComputeManagementClient(credential, subscription_id)
locations={'eastus', 'eastus2', 'westus', 'centralus', 'northcentralus', 'southcentralus', 'northeurope', 'westeurope',' eastasia', 'southeastasia', 'japaneast', 'japanwest', 'australiaeast', 'australiasoutheast', 'australiacentral', 'brazilsouth', 'southindia', 'centralindia', 'westindia', 'canadacentral', 'canadaeast', 'westus2','westcentralus', 'uksouth', 'ukwest', 'koreacentral', 'koreasouth', 'francecentral', 'southafricanorth', 'uaenorth', 'switzerlandnorth', 'germanywestcentral', 'norwayeast', 'jioindiawest', 'westus3', 'swedencentral', 'qatarcentral', 'polandcentral'}

from decimal import Decimal

def find_ratio(num1, num2):
    if isinstance(num1, float) or isinstance(num2, float):
        # Convert float inputs to Decimal objects for precise calculations
        decimal1 = Decimal(str(num1))
        decimal2 = Decimal(str(num2))
        # Calculate the ratio by dividing the decimals
        ratio = decimal1 / decimal2
        # Convert the ratio to a Fraction object for consistent output format
        ratio = Fraction(ratio).limit_denominator()
        ratio_str = f"{ratio.numerator}:{ratio.denominator}"
    else:
        # For integers, use the original logic with the Fraction class
        ratio = Fraction(int(num1), int(num2))
        ratio_str = f"{ratio.numerator}:{ratio.denominator}"
    return ratio_str
async def get_price():
    price_li=[]
    for location in locations:
        # Price data Fetch Begin
        url = f"https://prices.azure.com/api/retail/prices?$filter=serviceName eq 'Virtual Machines' and armRegionName eq '{location}' and priceType eq 'Consumption'&$top=1000&api-version=2023-01-01-preview"

        # Send the GET request to the Pricing API
        response = requests.get(url)
        # Parse the response JSON
        data = json.loads(response.text)

        # Check if 'Items' key is present in the response
        if 'Items' in data:
            items = data['Items']
            for item in items:
                datta = {
                    'InstanceType': item['armSkuName'],
                    'Region': location,
                    'TimeStamp': currentTime,
                    'Price (Per Month)': float(item['retailPrice']) * 30 * 24,
                    'CloudProvider': 'Azure'
                }
                price_li.append(datta)

    specs = []
    for location in locations:
        vm_sizes = compute_client.virtual_machine_sizes.list(location)
        for vm_size in vm_sizes:
            x = float(vm_size.memory_in_mb / 1024)
            y = float(vm_size.number_of_cores)
            comp = find_ratio(y,x)
            datta = {
                'InstanceType': vm_size.name,
                'vCPU': vm_size.number_of_cores,
                'Memory': float(vm_size.memory_in_mb / 1024),
                'Ratio': comp
            }
            specs.append(datta)

    ite = []
    for item in price_li:
        for spec in specs:
            if spec['InstanceType'] == item['InstanceType']:
                category=None
                # print(len(item['InstanceType']))
                # print(item['InstanceType'])
                if item['InstanceType'][0]=='S':
                    first_letter = item['InstanceType'][9]
                else:
                    first_letter = item['InstanceType'][6]
                if first_letter=='A':
                    category="A Series"
                elif first_letter=='B':
                    category="Bs Series"
                elif first_letter=='D':
                    category="D Series"
                elif first_letter=='E':
                    category="E Series"
                elif first_letter=='F':
                    category="F Series"
                elif first_letter=='G':
                    category="G Series"
                elif first_letter=='H':
                    category="H Series"
                elif first_letter=='L':
                    category="L Series"
                elif first_letter=='M':
                    category="M Series"
                else:
                    category="L Series"
                # print(first_letter)
                datta = {
                    'InstanceType': spec['InstanceType'],
                    'vCPU': spec['vCPU'],
                    'Memory': spec['Memory'],
                    'Ratio': spec['Ratio'],
                    'Region': item['Region'],
                    'TimeStamp': item['TimeStamp'],
                    'Price (Per Month)': round(item['Price (Per Month)'],2),
                    'CloudProvider': 'Azure',
                    'Category': category
                }
                if datta not in ite:
                    ite.append(datta)


    # print(ite)
    await insertData(ite)
    currentTime1=datetime.datetime.now()
    print(currentTime1)

async def main():
    await get_price()

# Call the main coroutine
asyncio.run(main())
