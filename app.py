import os
import logging
import boto3
from datetime import datetime  
from datetime import timedelta
import pprint as pp
# import config
import sqlite3
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from botocore.signers import CloudFrontSigner
from botocore.exceptions import ClientError
from flask import Flask, render_template, redirect, url_for, request, session, g, abort, flash


app = Flask(__name__)
app.config.from_object(__name__)


def list_of_files():
    remote_obj_bucket = s3_resource.Bucket(remote_bucket_name)
    summaries = remote_obj_bucket.objects.all()
    files = []
    config_prefix = "projects/vdo_python"
    for file in summaries:
        if file.key.startswith(config_prefix):
            files.append(file.key)
            s3_client.download_file(
                remote_bucket_name,
                file.key,
                os.path.basename(file.key)
            )
    return files

# S3 configuration
s3_client      = boto3.client('s3')
s3_resource    = boto3.resource('s3')
s3_access_key  = os.environ['AWS_ACCESS_KEY_ID']
s3_secret_key  = os.environ['AWS_SECRET_ACCESS_KEY']
s3_bucket_name = 'dyx-us-east-2-kac124cloud'
s3_prefix      = 'movies'
s3_region      = 'us-east-2'
remote_bucket_name = 'configs-vars-secrets-309213020321'
remote_objects = list_of_files()

import config
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='vdoflix',
    PASSWORD='im2bz2bnvdo'
))

app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def rsa_signer(message):
    with open(config.cf_private_key, 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return private_key.sign(message, padding.PKCS1v15(), hashes.SHA1())


def s3_titles():
    signed_titles = dict()

    vdo_titles = s3_client.list_objects_v2(
        Bucket=s3_bucket_name,
        Prefix=s3_prefix,
    )
    print("get list of movies from S3...")
    
    key_id            = config.cf_key_pair_id
    now               = datetime.now() + timedelta(days=1)
    year              = int(now.strftime("%Y"))
    month             = int(now.strftime("%m"))
    day               = int(now.strftime("%d"))
    expire_date       = datetime(year, month, day)
    key_id            = config.cf_key_pair_id

    for vdo_title in vdo_titles['Contents']:
        movie_title = vdo_title['Key'][7:]
        try:
            key_id = config.cf_key_pair_id
            url = f"{config.cf_url}/movies/{movie_title}"
            cloudfront_signer = CloudFrontSigner(key_id, rsa_signer)
            signed_url = cloudfront_signer.generate_presigned_url(
                url, date_less_than=expire_date)
        except ClientError as e:
            logging.error(e)
        signed_titles[movie_title] = signed_url
    return signed_titles

# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = "Invalid username" 
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('welcome'))
    return render_template('login.html', error=error)


# landing page after login
@app.route('/welcome')
def welcome():
    if not session.get('logged_in'):
        abort(401)
    return render_template('listings.html')


@app.route('/')
def listings():
    vdo_titles_signed_url = s3_titles()
    return render_template('listings.html', 
                            video_titles=vdo_titles_signed_url)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))

# print(app.config)