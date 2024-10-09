import boto3
import json
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
load_dotenv()

session_3 = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name='eu-north-1'
)

s3 = session_3.client('s3', region_name='eu-north-1')
bucket_name = os.getenv('BUCKET_NAME')

response = s3.create_bucket(
    Bucket=bucket_name,
    CreateBucketConfiguration={
        'LocationConstraint': 'eu-north-1'
    }
)
print("Bucket created:", response)

try:
    s3.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            'BlockPublicAcls': False, 
            'IgnorePublicAcls': False,
            'BlockPublicPolicy': False,
            'RestrictPublicBuckets': False 
        }
    )
    print("Public access block configuration set successfully.")
except ClientError as e:
    print(f"An error occurred: {e}")

bucket_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": [
                f"arn:aws:s3:::{bucket_name}",
                f"arn:aws:s3:::{bucket_name}/*"
            ]
        },
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:ListBucket",
            "Resource": f"arn:aws:s3:::{bucket_name}"
        }
    ]
}

bucket_policy_json = json.dumps(bucket_policy)

try:
    s3.put_bucket_policy(
        Bucket=bucket_name,
        Policy=bucket_policy_json
    )
    print(f"Public access granted for bucket: {bucket_name}")
except ClientError as e:
    print(f"An error occurred while applying bucket policy: {e}")
