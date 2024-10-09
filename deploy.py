import time
import boto3
import paramiko
import os
from dotenv import load_dotenv
load_dotenv()

ec2 = boto3.resource('ec2',
                     aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                     aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                     region_name=os.getenv('EC2_REGION'))

def launch_ec2_instance():
    print("Launching EC2 instance...")
    instances = ec2.create_instances(
        ImageId=os.getenv('IMAGE_ID'), 
        InstanceType='t2.micro',
        MinCount=1,
        MaxCount=1,
        KeyName=os.getenv('KEY_PAIR'),    
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [{'Key': 'Name', 'Value': 'FlaskAppInstance'}]
        }]
    )

    instance = instances[0]
    instance.wait_until_running()
    instance.reload()
    print(f"Instance launched: {instance.public_ip_address}")
    return instance


def ssh_connect(instance, key_file_path):
    print(f"Connecting to instance: {instance.public_ip_address}")
    key = paramiko.RSAKey.from_private_key_file(key_file_path)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    for _ in range(10):
        try:
            ssh.connect(hostname=instance.public_ip_address, username='ec2-user', pkey=key)
            print("Connected to the instance via SSH.")
            return ssh
        except Exception as e:
            print("Retrying SSH connection...")
            time.sleep(10)

    raise Exception("SSH connection failed")

def setup_environment(ssh):
    print("Setting up environment on the instance...")
    commands = [
        'sudo yum update -y',
        'sudo yum install python3 git -y',
        'pip3 install virtualenv',
        'sudo amazon-linux-extras install nginx1 -y',
        'sudo systemctl start nginx'
    ]

    for command in commands:
        stdin, stdout, stderr = ssh.exec_command(command)
        print(stdout.read().decode())


def upload_flask_app(ssh, local_path, remote_path):
    print(f"Uploading Flask app from {local_path} to {remote_path}...")
    sftp = ssh.open_sftp()
    sftp.put(local_path, remote_path)
    sftp.close()
    print("Flask app uploaded.")

def configure_nginx_and_start_app(ssh):
    print("Configuring Nginx and starting Flask app...")
    commands = [
        'cd /home/ec2-user',
        'virtualenv venv',
        'source venv/bin/activate',
        'pip install flask gunicorn',
        'gunicorn --bind 0.0.0.0:5000 app:app &',
        'sudo systemctl restart nginx'
    ]

    for command in commands:
        stdin, stdout, stderr = ssh.exec_command(command)
        print(stdout.read().decode())
def deploy_flask_app():
    instance = launch_ec2_instance()

    time.sleep(60) 
    key_file_path = 'anubhav-commvault-1-2-3.pem' 
    ssh = ssh_connect(instance, key_file_path)

    try:
        setup_environment(ssh)

  
        local_app_path = '/path/to/your/flask-app/app.py' 
        remote_app_path = '/home/ec2-user/app.py'
        upload_flask_app(ssh, local_app_path, remote_app_path)

        configure_nginx_and_start_app(ssh)

        print("Flask app successfully deployed!")

    finally:
        ssh.close()

if __name__ == "__main__":
    deploy_flask_app()