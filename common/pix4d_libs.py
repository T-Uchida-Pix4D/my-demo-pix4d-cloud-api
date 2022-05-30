import boto3    # AWS sdk
import requests   # HTTP request

CLOUD_URL = "https://cloud.pix4d.com"   # It redirects to demo page if you are not logged in.
PROJECT_URL = f"{CLOUD_URL}/project/api/v3/projects"    # shows Django REST framework if you don't provide credentials.


def get_jwt(client_id, client_secret):
  print("get_jwt")
  query_params_dict = {
    "grant_type": "client_credentials",
    "client_id": client_id,
    "client_secret": client_secret,
    "token_format": "jwt",
  }
  query_params = "&".join([f"{k}={v}" for k, v in query_params_dict.items()])
  url = f"{CLOUD_URL}/oauth2/token/?{query_params}"
  resp = requests.post(url)
  resp.raise_for_status()     #exception if there is error response
  return resp.json()["access_token"]


def create_project():
  print("create_project")


def project_s3_creds():
  print("project_s3_cred")


def register_image():
  print("register_image")


def start_processing():
  print("start_processing")


def get_project():
  print("get_project")
