import os

import pandas as pd
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from googleapiclient import sample_tools
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

"""
os.environ['GCP_PROJECT'] 
os.environ['GCP_ACCOUNT']
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] 

"""


class ServiceAccountDrive:

    @staticmethod
    def initialize_drive_service():
        """
        Initializes the Google Drive service and returns the service object and credentials.

        Returns:
            service (googleapiclient.discovery.Resource): The Google Drive service object.
            credentials (google.auth.credentials.Credentials): The credentials object used for authentication.
        """
        # If modifying these scopes, delete the file token.json.
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/drive.file",
        ]

        credentials = service_account.Credentials.from_service_account_file(
            filename=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"), scopes=scope
        )
        service = build("drive", "v3", credentials=credentials)

        return service, credentials

    @staticmethod
    def get_folder_id_by_name(folder_name):
        """
        Gets the ID of a Google Drive folder by its name.

        Args:
            folder_name (str): The name of the Google Drive folder.

        Returns:
            folder_id (str): The ID of the Google Drive folder.
        """
        service, credentials = ServiceAccountDrive.initialize_drive_service()

        response = (
            service.files()
            .list(
                corpora="allDrives",
                q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
            )
            .execute()
        )

        folder_id = response.get("files")[0].get("id")

        return folder_id

    @staticmethod
    def upload_file_to_drive(file_path, folder_id):
        """
        Uploads a file to a Google Drive folder.

        Args:
            file_path (str): The path to the file to upload.
            folder_id (str): The ID of the Google Drive folder to upload the file to.
        """
        service, credentials = ServiceAccountDrive.initialize_drive_service()

        file_metadata = {"name": os.path.basename(file_path), "parents": [folder_id]}
        media = MediaFileUpload(file_path, resumable=True)
        file = (
            service.files()
            .create(
                body=file_metadata,
                media_body=media,
                fields="id",
                supportsAllDrives=True,
            )
            .execute()
        )

        print(f"File uploaded successfully. File ID: {file.get('id')}")

    @staticmethod
    def delete_file_from_drive(file_id):
        """
        Deletes a file from Google Drive.

        Args:
            file_id (str): The ID of the file to delete.
        """
        service, credentials = ServiceAccountDrive.initialize_drive_service()

        service.files().delete(fileId=file_id, supportsAllDrives=True).execute()

        print(f"File deleted successfully. File ID: {file_id}")

    @staticmethod
    def download_file_from_drive(file_id, file_path):
        """
        Downloads a file from Google Drive.

        Args:
            file_id (str): The ID of the file to download.
            file_path (str): The path to save the downloaded file.
        """
        service, credentials = ServiceAccountDrive.initialize_drive_service()

        request = service.files().get_media(fileId=file_id)
        fh = open(file_path, "wb")
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")

        print(f"File downloaded successfully. File path: {file_path}")
