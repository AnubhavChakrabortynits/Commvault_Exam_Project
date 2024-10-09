import boto3
from dotenv import load_dotenv
import os

load_dotenv()

session_3 = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name='us-east-1'
)
 

ec2 = session_3.resource('ec2')

tags = [{'Key': 'Name', 'Value': 'Commvault_Anubhav_exam'}]
instance = ec2.create_instances(
    ImageId='ami-0fff1b9a61dec8a5f',
    InstanceType='t2.micro',
    MinCount=1,
    MaxCount=1,
    TagSpecifications=[
        {'ResourceType': 'instance', 'Tags': tags}
    ]
)

ec2_client = boto3.client('ec2')

response = ec2_client.describe_security_groups(
    Filters=[
        {
            'Name': 'group-name',
            'Values': ['default']
        }
    ]
)

default_security_group_id = response['SecurityGroups'][0]['GroupId']

ec2_client.authorize_security_group_ingress(
    GroupId=default_security_group_id,
    IpPermissions=[
        {
            'IpProtocol': 'tcp',
            'FromPort': 80,
            'ToPort': 80,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        },
        {
            'IpProtocol': 'tcp',
            'FromPort': 443,
            'ToPort': 443,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }
    ]
)




