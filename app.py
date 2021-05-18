import os
import logging
import boto3
import datetime
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
s3_client = boto3.client('s3')
vdo_objects = s3_client.list_objects_v2(
    Bucket=config.s3_bucket_name,
    EncodingType='url',
)
expiry = datetime.datetime.now() + 7200
expires = datetime.datetime.today() + 86400

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
    # get move list from S3
    vdo_titles = config['s3_client'].list_objects_v2(
        Bucket=config['s3_bucket_name'],
        Prefix=config['s3_prefix'],
        ContinuationToken='string'
    )
    return render_template('listings.html', vdo_titles=vdo_titles)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))

print(app.config)