import boto3
# import config
import mysql.connector
from datetime import datetime  
from datetime import timedelta

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from botocore.signers import CloudFrontSigner


def rsa_signer(message):
    with open('pk-APKAINHXN3VFSLBKFE3Q.pem', 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return private_key.sign(message, padding.PKCS1v15(), hashes.SHA1())

key_id = "APKAINHXN3VFSLBKFE3Q"
url = f"https://d3ix6m9kij1edr.cloudfront.net/movies/10.mp4"
expire_date = datetime(2022, 1, 1)
# expire_date = datetime.now() + timedelta(days=1)

cloudfront_signer = CloudFrontSigner(key_id, rsa_signer)

# Create a signed url that will be valid until the specfic expiry date
# provided using a canned policy.
signed_url = cloudfront_signer.generate_presigned_url(
    url, date_less_than=expire_date)
print(signed_url)

# def list_of_files():
#     remote_obj_bucket = s3_resource.Bucket(remote_bucket_name)
#     summaries = remote_obj_bucket.objects.all()
#     files = []
#     config_prefix = "projects/vdo_python"
#     for file in summaries:
#         if file.key.startswith(config_prefix):
#             files.append(file.key)
#             response = s3_client.download_file(
#                 remote_bucket_name,
#                 file.key,
#                 os.path.basename(file.key)
#             )
#     return files

# remote_bucket_name = 'configs-vars-secrets-309213020321'
# remote_objects = list_of_files()