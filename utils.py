import boto3
import config
import mysql.connector
from datetime import datetime  
from datetime import timedelta

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from botocore.signers import CloudFrontSigner


def rsa_signer(message):
    with open('path/to/private_key.pem', 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return private_key.sign(message, padding.PKCS1v15(), hashes.SHA1())

key_id = config.cf_key_pair_id
url = f"{config.cf_url}/hello.txt"
# expire_date = datetime.datetime(2017, 1, 1)
expire_date = datetime.now() + timedelta(days=1)

cloudfront_signer = CloudFrontSigner(key_id, rsa_signer)

# Create a signed url that will be valid until the specfic expiry date
# provided using a canned policy.
signed_url = cloudfront_signer.generate_presigned_url(
    url, date_less_than=expire_date)
print(signed_url)
