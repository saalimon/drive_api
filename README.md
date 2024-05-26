# drive_api

This Python program is used to interact with Google Drive using the Google Drive API. It allows you to initialize a service, get a folder ID by its name, and list all files in a specific folder.

## Usage

1. **Import the necessary classes from the `drive_api` module:**

```python
from drive_api import ServiceAccountDrive
ServiceAccountDriveInstance = ServiceAccountDrive()
```

2. **Initialize the Google Drive service:**

```python
cred = "path_to_your_credentials_file.json"
service, credentials = ServiceAccountDriveInstance.initialize_drive_service(creds=cred)
```
In this step, replace `"path_to_your_credentials_file.json"` with the path to your Google Drive API credentials file. 

3. **Get the folder ID by its name:**

```python
folder_id = ServiceAccountDrive.get_folder_id_by_name("Folder Name")
```
Replace `"some doc name"` with the name of the folder you're interested in.

4. **List all files in a specific folder:**

```python
files = ServiceAccountDrive.list_files_in_folder(folder_id)
```
Replace `folder_id` with the folder ID you got in the previous step.
