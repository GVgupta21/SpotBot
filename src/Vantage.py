import ec2_spot_price as ec2sp
# print(ec2sp)
def pricing_function(): 
    df = ec2sp.spot_prices([], [], ['Linux/UNIX'])
    return df
# print(pricing_function())