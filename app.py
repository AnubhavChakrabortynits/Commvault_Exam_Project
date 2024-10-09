from flask import Flask, request, render_template, redirect, flash, session
import boto3
import bcrypt
import os 
from dotenv import load_dotenv
from utils import *
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24) 
session_3 = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name='eu-north-1'
)

s3 = session_3.client('s3')
bucket_name = os.getenv('BUCKET_NAME')

users = {}
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            flash('Username already exists!')
            return redirect('/register')
        
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        users[username] = hashed
        flash('Registration successful!')
        return redirect('/login')
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username not in users or not bcrypt.checkpw(password.encode('utf-8'), users[username]):
            flash('Invalid username or password!')
            return redirect('/login')
        
        session['username'] = username 
        flash('Login successful!')
        return redirect('/images')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect('/login')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'username' not in session:
        flash('You need to log in to upload files!')
        return redirect('/login')
    files = request.files.getlist('image')
    for file in files:
        s3.upload_fileobj(
    file,
    bucket_name,
    file.filename,
    ExtraArgs={
        'ContentType': file.content_type,
        'ContentDisposition': f'attachment; filename="{file.filename}"'
    }
)
    return "Upload successful!"

@app.route('/')
def upload_page():
    return render_template('upload.html')


@app.route('/images')
def list_images():
    if 'username' not in session:
        flash('You need to log in to view images!')
        return redirect('/login')
    
    objects = s3.list_objects_v2(Bucket=bucket_name)
    images = []
    for obj in objects.get('Contents', []):
        image = {
            'name': obj['Key'],
            'view_url': f"https://{bucket_name}.s3.amazonaws.com/{obj['Key']}",
        }
        images.append(image)
    
    return render_template('viewimg.html', images=images)
if __name__ == '__main__':
    app.run(debug=True)
