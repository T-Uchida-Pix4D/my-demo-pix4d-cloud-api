import os
import boto3
from progressbar import ProgressBar
from random import randint
from pathlib import Path, PurePosixPath
from common.pix4d_libs import get_jwt, create_project, project_s3_creds, register_image, start_processing, get_project

PIX4D_CLIENT_ID = os.environ['PIX4D_CLIENT_ID']
PIX4D_CLIENT_SECRET = os.environ['PIX4D_CLIENT_SECRET']
assert PIX4D_CLIENT_ID
assert PIX4D_CLIENT_SECRET

print(get_jwt(PIX4D_CLIENT_ID, PIX4D_CLIENT_SECRET))
