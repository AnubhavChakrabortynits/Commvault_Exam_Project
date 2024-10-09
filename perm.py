import boto3
import json
from dotenv import load_dotenv
from botocore.exceptions import ClientError
import os
load_dotenv()

session_3 = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name='eu-north-1'
)

s3 = session_3.client('s3')
bucket_name = os.getenv('BUCKET_NAME')

bucket_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*", 
            "Action": [
                "s3:PutObject",
                "s3:GetObject"
            ], 
            "Resource": f"arn:aws:s3:::{bucket_name}/*"
        }
    ]
}


bucket_policy_json = json.dumps(bucket_policy)

try:
    s3.put_bucket_policy(
        Bucket=bucket_name,
        Policy=bucket_policy_json
    )
    print(f"Bucket policy applied to {bucket_name}. Public uploads are now allowed.")
except ClientError as e:
    print(f"An error occurred while applying the bucket policy: {e}")

try:
    current_policy = s3.get_bucket_policy(Bucket=bucket_name)
    print("Current bucket policy:", current_policy['Policy'])
except ClientError as e:
    print(f"An error occurred while fetching the bucket policy: {e}")
