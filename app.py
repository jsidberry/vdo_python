import os
import logging
import boto3
import datetime
import pprint as pp
from botocore.exceptions import ClientError
import config
import sqlite3
from flask import Flask, render_template, redirect, url_for, request, session, g, abort, flash

app = Flask(__name__)
app.config.from_object(__name__)


app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='vdoflix',
    PASSWORD='im2bz2bnvdo'
))

app.config.from_envvar('FLASKR_SETTINGS', silent=True)

# S3 configuration
s3_client      = boto3.client('s3')
s3_access_key  = os.environ['AWS_ACCESS_KEY_ID']
s3_secret_key  = os.environ['AWS_SECRET_ACCESS_KEY']
s3_bucket_name = 'dyx-us-east-2-kac124cloud'
s3_prefix      = 'movies'
s3_region      = 'us-east-2'

# vdo_objects = s3_client.list_objects_v2(
#     Bucket=s3_bucket_name,
#     EncodingType='url',
# )
# expiry = datetime.datetime.now() + 7200
# expires = datetime.datetime.today() + 86400

def create_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response

def s3_titles():
    signed_titles = dict()
    vdo_titles = s3_client.list_objects_v2(
        Bucket=s3_bucket_name,
        Prefix=s3_prefix,
    )
    for vdo_title in vdo_titles['Contents']:
        movie_title = vdo_title['Key'][7:]
        signed_url = create_presigned_url(s3_bucket_name, vdo_title['Key'], expiration=7200)
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
    return render_template('listings.html', video_titles=vdo_titles_signed_url)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))

print(app.config)