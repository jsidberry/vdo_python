import boto3
import config
import mysql.connector

options = {
    'version' : 'latest',
    'region'  : config['s3']['region'],
    'key'     : config['s3']['key'],
    'secret'  : config['s3']['secret']
}

s3client = boto3.client('s3')
client   = boto3.client('cloudfront')


def database_connection():
    mydb = mysql.connector.connect(
        host=config['database']['server'],
        database=config['database']['name'],
        user=config['database']['username'],
        password=config['database']['password']
    )

    print(mydb) 