import os
import boto3
from progressbar import ProgressBar
from random import randint
from pathlib import Path, PurePosixPath
from common.pix4d_libs import get_jwt, create_project, project_s3_creds, register_images, start_processing, get_project

PIX4D_CLIENT_ID = os.environ['PIX4D_CLIENT_ID']
PIX4D_CLIENT_SECRET = os.environ['PIX4D_CLIENT_SECRET']
assert PIX4D_CLIENT_ID
assert PIX4D_CLIENT_SECRET

# Get access token
my_jwt = get_jwt(PIX4D_CLIENT_ID, PIX4D_CLIENT_SECRET)
print(my_jwt)

# Create project
project_id = create_project(f"demo {randint(0, 1000)}", my_jwt)['id']
print(project_id)

# Get AWS S3 credentials from pix4d endpoint
s3_creds = project_s3_creds(project_id, my_jwt)
print(s3_creds)

# Create service client at s3.
# TO DO: learn aws s3 api
s3_client = boto3.client("s3",
                          aws_access_key_id=s3_creds["access_key"],
                          aws_secret_access_key=s3_creds["secret_key"],
                          aws_session_token=s3_creds["session_token"])


# Uploading imanges
keys = []
images = list(Path("images/").glob("*.JPG"))    # "glob",short for global, expands *.
                                                # Path().glob() returns generator (it's like os.walk).
with ProgressBar(max_value=len(images)) as pbar:
  for i, image in enumerate(images):
    k = str(Path(s3_creds["key"]) / Path(image).name)  # "/" creates child path between pathlib.Path obj. 
                                                      # 'key' is bath-path like "user-199.../project-883349"
    # Add an object to a bucket
    s3_client.put_object(
      Bucket=s3_creds["bucket"], 
      Key=k, 
      Body=Path(image).read_bytes(),  # Path().read_byte() retur s binary object
      ACL="bucket-owner-full-control" # Access Control List
    )
    keys.append(k)
    pbar.update(i)

print(keys)


# Register images
ret_register = register_images(project_id, my_jwt, keys)
print(ret_register)


# Start processing
ret_start = start_processing(project_id, my_jwt)
print(ret_start)


# Check process status
print(get_project(project_id, my_jwt)['public_status'])
