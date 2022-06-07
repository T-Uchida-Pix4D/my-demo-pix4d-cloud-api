import os
import boto3
from pathlib import Path
from IPython.display import Image
from common.pix4d_libs import get_jwt, get_outputs, project_s3_creds, get_s3_client
import json

PIX4D_CLIENT_ID = os.environ['PIX4D_CLIENT_ID']
PIX4D_CLIENT_SECRET = os.environ['PIX4D_CLIENT_SECRET']
assert PIX4D_CLIENT_ID
assert PIX4D_CLIENT_SECRET


# Get access token
my_jwt = get_jwt(PIX4D_CLIENT_ID, PIX4D_CLIENT_SECRET)


# Demo data from https://cloud.pix4d.com/dataset/256164/map?shareToken=97a07d231fbc47b1b105d6cc7bcab0a4
project_id = 256164


# You can access your own projects without a share token
project_share_token = "97a07d231fbc47b1b105d6cc7bcab0a4"


# Get project data
outputs = get_outputs(project_id, my_jwt, share_token=project_share_token)
print(json.dumps(outputs, indent=4))


# What is ortho_thumb? ortho_thumb not listed in API doc. Can there be more than one ortho_thumb in outputs data?
# https://developer.pix4d.com/cloud-api/index.html#tag/How-to-retrieve-inputs-outputs-and-reports
ortho_thumb = [i for i in outputs['outputs'] if i['result_type'] == 'ortho' and i['output_type'] == 'ortho_thumb']
if ortho_thumb:
  ortho_thumb = ortho_thumb[0]
else:
  print('Failed to find ortho')


# Get aws s3 credentials
s3_creds = project_s3_creds(project_id, my_jwt, share_token=project_share_token)


# Get s3 object
s3_client = get_s3_client(project_id, my_jwt, share_token=project_share_token)


# Get ortho thumbnail
local_file_name = 'ortho_thumb.png'
s3_client.download_file(ortho_thumb['s3_bucket'], ortho_thumb['s3_key'], local_file_name)


# Display thumnail image
Image(local_file_name)
