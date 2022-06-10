'''
This is a demo script for uploading custom template file for processing option.
The detail of processing with a custom template is described in the following document.
https://developer.pix4d.com/cloud-api/index.html#section/1.-Standard-processing-with-PIX4Dmapper
'''

import os
import boto3    # for s3_client
import requests # for HTTP requests
from progressbar import ProgressBar
from random import randint  # for creating project id randomly
from pathlib import Path

##### Set your custom template filename (.tmpl) #####
CUSTOM_TEMPLATE = "my_custom_template.tmpl"
assert CUSTOM_TEMPLATE

# Set the environment variable for client id and password beforehand, or assign value directory.
PIX4D_CLIENT_ID = os.environ['PIX4D_CLIENT_ID']
PIX4D_CLIENT_SECRET = os.environ['PIX4D_CLIENT_SECRET']
assert PIX4D_CLIENT_ID
assert PIX4D_CLIENT_SECRET

CLOUD_URL = "https://cloud.pix4d.com" 
PROJECT_URL = f"{CLOUD_URL}/project/api/v3/projects"


def get_jwt(client_id, client_secret):
  query_params_dict = {
    "grant_type": "client_credentials",
    "client_id": client_id,
    "client_secret": client_secret,
    "token_format": "jwt",
  }
  query_params = "&".join([f"{k}={v}" for k, v in query_params_dict.items()])
  url = f"{CLOUD_URL}/oauth2/token/?{query_params}"
  resp = requests.post(url)
  resp.raise_for_status()
  return resp.json()["access_token"]


def headers(token):
  return {"Authorization": f"Bearer {token}"}


def create_project(name, token):
  url = f"{PROJECT_URL}/"
  resp = requests.post(url, json={"name": name}, headers=headers(token))
  resp.raise_for_status()
  return resp.json()


def project_s3_creds(project_id, token, share_token=None):  # share_token?
  url = f"{PROJECT_URL}/{project_id}/s3_credentials/"
  resp = requests.get(url, headers=headers(token), params=_get_params(share_token))
  resp.raise_for_status()
  return resp.json() 


def _get_params(share_token=None):
  params = {}
  if share_token is not None:
    params["shareToken"] = share_token
  return params


def project_s3_creds(project_id, token, share_token=None):
  url = f"{PROJECT_URL}/{project_id}/s3_credentials/"
  resp = requests.get(url, headers=headers(token), params=_get_params(share_token))
  resp.raise_for_status()
  return resp.json() 


def register_images(project_id, token, image_keys):
  url = f"{PROJECT_URL}/{project_id}/inputs/bulk_register/"
  resp = requests.post(
    url, headers=headers(token), json={"input_file_keys": image_keys}
  )
  resp.raise_for_status()
  return resp.json


def register_extra_file(project_id, token, file_key):
  url = f"{PROJECT_URL}/{project_id}/extras/"
  resp = requests.post(
    url, headers=headers(token), json={"file_key": file_key}
  )
  resp.raise_for_status()
  return resp.json


def start_processing(project_id, token, processing_options=None):
  url = f"{PROJECT_URL}/{project_id}/start_processing/"
  resp = requests.post(url, headers=headers(token), data=processing_options)
  resp.raise_for_status()
  return resp.json


# main -------------
def main():
  print("main started")

  # Get access token
  my_jwt = get_jwt(PIX4D_CLIENT_ID, PIX4D_CLIENT_SECRET)
  
  # Create project with a random project id
  project_id = create_project(f"demo {randint(0, 1000)}", my_jwt)['id']
  
  # Get AWS S3 credentials
  s3_creds = project_s3_creds(project_id, my_jwt)
  
  # Create service client at s3.
  s3_client = boto3.client("s3",
                            aws_access_key_id=s3_creds["access_key"],
                            aws_secret_access_key=s3_creds["secret_key"],
                            aws_session_token=s3_creds["session_token"])
  
  
  # Uploading imanges. "image" directory is supposed to be in the same directory as this script.
  keys = []
  images = list(Path("images/").glob("*.JPG"))

  with ProgressBar(max_value=len(images)) as pbar:
    for i, image in enumerate(images):
      k = str(Path(s3_creds["key"]) / Path(image).name)
      # Add an object to a bucket
      s3_client.put_object(
        Bucket=s3_creds["bucket"], 
        Key=k, 
        Body=Path(image).read_bytes(),
        ACL="bucket-owner-full-control"
      )
      keys.append(k)
      pbar.update(i)
  
  # Register images
  register_images(project_id, my_jwt, keys)

  # Upload your custom template to s3 bucket. "template" is supposed to be in the same directory as this script.
  template = CUSTOM_TEMPLATE
  custom_template_s3_key = str(Path(s3_creds["key"]) / Path(template).name)
  s3_client.put_object(
    Bucket=s3_creds["bucket"], 
    Key=custom_template_s3_key,
    Body=Path(template).read_bytes(),
    ACL="bucket-owner-full-control"
  )

  # Register your custom template as extra file
  register_extra_file(project_id, my_jwt, custom_template_s3_key)

  # Start processing with processing options
  processing_options = {
    "custom_template_s3_key": custom_template_s3_key,
    "custom_template_s3_bucket": s3_creds["bucket"]
  }

  start_processing(project_id, my_jwt, processing_options)


if __name__ == "__main__":
  main()
  print("main completed")
