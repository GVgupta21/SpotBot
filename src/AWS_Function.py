import boto3
import json
import html
import webbrowser
import re
from jinja2 import Template
import datetime
import math
from fractions import Fraction
import asyncio
from Vantage import pricing_function
from Bot_retrive_data import insertData
import datetime
# ratio =input("Enter the Memory:vcpus ratio: ")
# ratio=float(ratio)
ec2_client = boto3.client('ec2',region_name='us-east-1',aws_access_key_id="AKIA3343A5N7X45NWB5H",aws_secret_access_key="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")
response1 = ec2_client.describe_instance_types()

import tracemalloc
tracemalloc.start()

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

def check_i_in_instance_name(instance_name):
    # Use regular expression pattern to check for the condition
    pattern = r'\d.*i.*\.'

    # Check if the pattern matches the instance name
    match = re.search(pattern, instance_name)

    # Return True if the pattern is found, False otherwise
    return bool(match)

def check_g_in_instance_name(instance_name):
    # Use regular expression pattern to check for the condition
    pattern = r'\d.*g.*\.'

    # Check if the pattern matches the instance name
    match = re.search(pattern, instance_name)

    # Return True if the pattern is found, False otherwise
    return bool(match)

def check_a_in_instance_name(instance_name):
    # Use regular expression pattern to check for the condition
    pattern = r'\d.*a.*\.'

    # Check if the pattern matches the instance name
    match = re.search(pattern, instance_name)

    # Return True if the pattern is found, False otherwise
    return bool(match)

def check_d_in_instance_name(instance_name):
    # Use regular expression pattern to check for the condition
    pattern = r'\d.*d.*\.'

    # Check if the pattern matches the instance name
    match = re.search(pattern, instance_name)

    # Return True if the pattern is found, False otherwise
    return bool(match)

def get_available_regions():
    """Gets all the available regions.

    Returns:
        list: A list of available regions.
    """

    client = boto3.client("ec2",region_name='us-east-1')
    response = client.describe_regions()

    regions = []
    for region in response["Regions"]:
        regions.append(region["RegionName"])

    return regions


async def get_price():
  # regions=get_available_regions()
  # print(regions)
  instance_types1 = response1['InstanceTypes']

  pretty_response = json.dumps(instance_types1, indent=4)

  price_list=pricing_function()
#   print(price_list)
  data=[]
  for items in price_list:
    for it in instance_types1:
        if items['InstanceType']== it['InstanceType']:
            dat={
                'specs':it,
                'SpotPrice':items['SpotPrice'],
                'Region':items['AvailabilityZone']
            }
            data.append(dat)

  data = json.dumps(data, indent=4)
  data = json.loads(data)
#   print(data)
  price_li=[]
  for instance_type in data:
    x=float(instance_type['specs']['MemoryInfo']['SizeInMiB']/1024)
    y=float(instance_type['specs']['VCpuInfo']['DefaultVCpus'])
    comp=find_ratio(y,x)
    # print(comp)
    # print(ratio)
    NetworkPerformance=None
    NvmeSupport=None
    EbsBandwidth=None
    chip="Intel Xenon"
    if check_a_in_instance_name(instance_type['specs']['InstanceType']):
        chip="AMD EPYC"
    elif check_g_in_instance_name(instance_type['specs']['InstanceType']):
        chip="Graviton"
    if check_d_in_instance_name(instance_type['specs']['InstanceType']):
        ssd="SSD"
    else:
        ssd="Non SSD"
    category=None
    if instance_type['specs']['InstanceType'] and instance_type['specs']['InstanceType'][0].isalpha():
        first_letter = instance_type['specs']['InstanceType'][0]
        if first_letter=='m' or first_letter =='t':
            category="GeneralPurpose"
        elif first_letter=='c':
            category="ComputeOptimized"
        elif first_letter=='r' or first_letter=='x' or first_letter=='z' or first_letter=='u':
            category="MemoryOptimized"
        elif first_letter=='i' or first_letter=='d' or first_letter=='h' and instance_type['specs']['InstanceType'][1] != 'n':
            category="StorageOptimized"
        else:
           category="AcceleartedOptimized"
    if 'NetworkInfo' in instance_type['specs']:
       if 'NetworkPerformance' in instance_type['specs']['NetworkInfo']:
          NetworkPerformance=instance_type['specs']['NetworkInfo']['NetworkPerformance']
    if 'EbsInfo' in instance_type['specs']:
       if 'NvmeSupport' in instance_type['specs']['EbsInfo']:
          NvmeSupport=instance_type['specs']['EbsInfo']['NvmeSupport']
       if 'EbsOptimizedInfo' in instance_type['specs']['EbsInfo']:
          if 'MaximumBandwidthInMbps' in instance_type['specs']['EbsInfo']['EbsOptimizedInfo']:
             EbsBandwidth=instance_type['specs']['EbsInfo']['EbsOptimizedInfo']['MaximumBandwidthInMbps']
          if 'MaximumIops'in instance_type['specs']['EbsInfo']['EbsOptimizedInfo']:
             iops=instance_type['specs']['EbsInfo']['EbsOptimizedInfo']['MaximumIops']
    currentTime=datetime.datetime.now()
    datta={
            'InstanceType':instance_type['specs']['InstanceType'],
            'vCPU':float(instance_type['specs']['VCpuInfo']['DefaultVCpus']),
            'Memory':float(instance_type['specs']['MemoryInfo']['SizeInMiB']/1024),
            'Storage':instance_type['specs']['InstanceStorageSupported'],
            'Ratio':comp,
            'NVME_Support':NvmeSupport,
            'Category':category,
            'Region':instance_type['Region'],
            'TimeStamp':currentTime,
            'SSD':ssd,
            'Chip':chip,
            'Price (Per Month)':round(float(instance_type['SpotPrice'])*30*24,2),
            'CloudProvider':'AWS'
        }
    #
    price_li.append(datta)
  # price_li=json.dumps(price_li)
  # data = dict(price_li)
  await insertData(price_li)

# display_html_in_browser(html_code)
async def main():
    await get_price()

# Call the main coroutine
asyncio.run(main())