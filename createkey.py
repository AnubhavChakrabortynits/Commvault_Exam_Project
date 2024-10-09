import os
import boto3
from dotenv import load_dotenv
load_dotenv()

ec2 = boto3.resource('ec2',
                     aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                     aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                     region_name=os.getenv('EC2_REGION'))
ec2 = boto3.client('ec2',
                   aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                   aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                   region_name=os.getenv('EC2_REGION'))
def create_key_pair(key_name):
    try:
        response = ec2.create_key_pair(KeyName=key_name)

        private_key = response['KeyMaterial']

        with open(f'{key_name}.pem', 'w') as file:
            file.write(private_key)

        os.chmod(f'{key_name}.pem', 0o400)

        print(f"Key pair '{key_name}' created and saved to {key_name}.pem")
    except Exception as e:
        print(f"Error creating key pair: {e}")

if __name__ == "__main__":
    create_key_pair(os.getenv('KEY_PAIR'))