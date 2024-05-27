import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload, MediaIoBaseDownload

"""
os.environ['GCP_PROJECT'] 
os.environ['GCP_ACCOUNT']
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] 

"""


class ServiceAccountDrive:

    @classmethod
    def initialize_drive_service(cls, initialize_type="cred_info", creds=None):
        """
        Initializes the Google Drive service and returns the service object and credentials.

        Args:
            initialize_type (str, optional): The type of initialization to use. Defaults to "cred_info".
            creds (str, optional): The credentials information. Required if initialize_type is "cred_info".

        Returns:
            service (googleapiclient.discovery.Resource): The Google Drive service object.
            credentials (google.auth.credentials.Credentials): The credentials object used for authentication.
        """
        # If modifying these scopes, delete the file token.json.
        cls.scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/drive.file",
        ]
        if initialize_type == "cred_info":
            if creds is None:
                print(
                    "Please specify the creds parameter for initialize_type='cred_info'"
                )
            else:
                cred_json = json.loads(creds)
                cls.credentials = service_account.Credentials.from_service_account_info(
                    cred_json, scopes=cls.scope
                )
        elif initialize_type == "service_account":
            cls.credentials = service_account.Credentials.from_service_account_file(
                filename=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
                scopes=cls.scope,
            )
        cls.service = build("drive", "v3", credentials=cls.credentials)

        return cls.service, cls.credentials

    @classmethod
    def get_folder_id_by_name(cls, folder_name):
        """
        Gets the ID of a Google Drive folder by its name.

        Args:
            folder_name (str): The name of the Google Drive folder.

        Returns:
            folder_id (str): The ID of the Google Drive folder.
        """
        if cls.service is None:
            print(
                "Please initialize the service first using initialize_drive_service() method."
            )
        response = (
            cls.service.files()
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

    @classmethod
    def upload_file_to_drive(
        cls, file_path, folder_id, file_metadata=None, io_base=False, mimetype=None
    ):
        """
        Uploads a file to a Google Drive folder.

        Args:
            file_path (str): The path to the file to upload.
            folder_id (str): The ID of the Google Drive folder to upload the file to.
            file_metadata (dict, optional): Additional metadata for the file (default: None).
            io_base (bool, optional): Whether to use MediaIoBaseUpload for uploading (default: False).
            mimetype (str, optional): The mimetype of the file (required if io_base=True).

        Raises:
            ValueError: If the service is not initialized.
            ValueError: If io_base=True but mimetype is not specified.

        Returns:
            str: The ID of the uploaded file.
        """
        if cls.service is None:
            raise ValueError(
                "Please initialize the service first using initialize_drive_service() method."
            )

        if file_metadata is None:
            file_metadata = {
                "name": os.path.basename(file_path),
                "parents": [folder_id],
            }

        if io_base and mimetype is not None:
            # Use MediaIoBaseUpload for large files
            media = MediaIoBaseUpload(
                file_path, mimetype=mimetype, resumable=True
            )  # e.g. mimetype='image/jpeg'
        elif io_base and mimetype is None:
            # Raise an error if mimetype is not specified
            raise ValueError("Please specify the mimetype parameter for io_base=True")
        else:
            # Use MediaFileUpload for small files and can access their path
            media = MediaFileUpload(file_path, resumable=True)

        file = (
            cls.service.files()
            .create(
                body=file_metadata,
                media_body=media,
                fields="id",
                supportsAllDrives=True,
            )
            .execute()
        )

        return file.get("id")

    @classmethod
    def delete_file_from_drive(cls, file_id):
        """
        Deletes a file from Google Drive.

        Args:
            file_id (str): The ID of the file to delete.
        """
        if cls.service is None:
            raise ValueError(
                "Please initialize the service first using initialize_drive_service() method."
            )
        cls.service.files().delete(fileId=file_id, supportsAllDrives=True).execute()

        print(f"File deleted successfully. File ID: {file_id}")

    @classmethod
    def download_file_from_drive(cls, file_id, file_path):
        """
        Downloads a file from Google Drive.

        Args:
            file_id (str): The ID of the file to download.
            file_path (str): The path to save the downloaded file.
        """
        if cls.service is None:
            raise ValueError(
                "Please initialize the service first using initialize_drive_service() method."
            )
        request = cls.service.files().get_media(fileId=file_id)
        fh = open(file_path, "wb")
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")

        print(f"File downloaded successfully. File path: {file_path}")

    @classmethod
    def list_folders_in_folder(cls, folder_id):
        """
        Lists all folders within a given folder.

        Args:
            folder_id (str): The ID of the folder to list folders from.

        Returns:
            None
        """
        if cls.service is None:
            raise ValueError(
                "Please initialize the service first using initialize_drive_service() method."
            )
        try:
            # List files and folders within the current folder

            results = (
                cls.service.files()
                .list(
                    corpora="allDrives",
                    q=f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.folder'",
                    fields="files(id, name)",
                    includeItemsFromAllDrives=True,
                    supportsAllDrives=True,
                )
                .execute()
            )

            # Process each folder
            for folder in results.get("files", []):
                folder_name = folder["name"]
                folder_id = folder["id"]
                # Print or process permissions for the folder
                print(f"Folder: {folder_name}, ID: {folder_id}")
                # Recursively list folders within this folder
                cls.list_folders_in_folder(folder_id)

        except Exception as e:
            print("An error occurred:", e)

    @classmethod
    def list_files_in_folder(cls, folder_id):
        """
        Lists the files in a given folder.

        Args:
            folder_id (str): The ID of the folder to list files from.

        Returns:
            None
        """
        if cls.service is None:
            raise ValueError(
                "Please initialize the service first using initialize_drive_service() method."
            )
        try:
            # List files and folders within the current folder
            results = (
                cls.service.files()
                .list(
                    corpora="allDrives",
                    q=f"'{folder_id}' in parents and mimeType!='application/vnd.google-apps.folder'",
                    fields="files(id, name)",
                    includeItemsFromAllDrives=True,
                    supportsAllDrives=True,
                )
                .execute()
            )

            # Process each file
            for file in results.get("files", []):
                file_name = file["name"]
                file_id = file["id"]
                # Print or process permissions for the file
                print(f"File: {file_name}, ID: {file_id}")

        except Exception as e:
            print("An error occurred:", e)
