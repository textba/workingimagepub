import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def authenticate_drive(client_secrets_file, token_file):
    creds = None
    if os.path.exists(token_file):
        with open(token_file, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_file, "wb") as token:
            pickle.dump(creds, token)

    return build("drive", "v3", credentials=creds)


def upload_to_drive(file_path, title, description="", folder_id=None, client_secrets_file="client_secret.json", token_file="drive_token.pickle"):
    service = authenticate_drive(client_secrets_file, token_file)

    file_metadata = {"name": title, "description": description}
    if folder_id:
        file_metadata["parents"] = [folder_id]

    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields="id, webViewLink").execute()

    file_id = file.get("id")
    file_url = file.get("webViewLink")

    service.permissions().create(fileId=file_id, body={"type": "anyone", "role": "reader"}).execute()
    return file_url, file_id
