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


def headers(token):
  return {"Authorization": f"Bearer {token}"}


def create_project(name, token):
  print("create_project")
  url = f"{PROJECT_URL}/"
  resp = requests.post(url, json={"name": name}, headers=headers(token))
  resp.raise_for_status()   # if the response is not JSON format, it raises an error
  return resp.json()


def _get_params(share_token=None):
  params = {}
  if share_token is not None:
    params["shareToken"] = share_token
  return params


def project_s3_creds(project_id, token, share_token=None):  # share_token?
  print("project_s3_cred")
  url = f"{PROJECT_URL}/{project_id}/s3_credentials/"
  resp = requests.get(url, headers=headers(token), params=_get_params(share_token)) # 'params' is query string
  resp.raise_for_status()
  return resp.json() 


def register_images(project_id, token, image_keys):
  print("register_image")
  url = f"{PROJECT_URL}/{project_id}/inputs/bulk_register/"
  resp = requests.post(
    url, headers=headers(token), json={"input_file_keys": image_keys}
  )
  resp.raise_for_status()
  return resp.json


def start_processing(project_id, token):
  print("start_processing")
  url = f"{PROJECT_URL}/{project_id}/start_processing/"
  resp = requests.post(url, headers=headers(token))
  resp.raise_for_status()
  return resp.json


def get_project(project_id, token, share_token=None):
  print("get_project")
  url = f"{PROJECT_URL}/{project_id}/"
  resp = requests.get(url, headers=headers(token), params=_get_params(share_token))
  resp.raise_for_status()
  return resp.json()


def get_outputs(project_id, token, share_token=None):
  print("get_outputs")
  url = f"{PROJECT_URL}/{project_id}/outputs/"
  resp = requests.get(url, headers=headers(token), params=_get_params(share_token))
  resp.raise_for_status()
  return resp.json()


def get_s3_client(project_id, token, share_token=None):
  s3_creds = project_s3_creds(project_id, token, share_token)
  return boto3.client(
    "s3",
    aws_access_key_id=s3_creds["access_key"],
    aws_secret_access_key=s3_creds["secret_key"],
    aws_session_token=s3_creds["session_token"]
  )







