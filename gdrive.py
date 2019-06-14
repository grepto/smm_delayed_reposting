from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import pickle
import os.path


def get_drive_credentials():
    credentials = None
    if os.path.exists('gdrive_token.pickle'):
        with open('gdrive_token.pickle', 'rb') as token:
            credentials = pickle.load(token)
    if not credentials:
        gauth = GoogleAuth()
        gauth.LocalWebserverAuth()
        credentials = gauth
        with open('gdrive_token.pickle', 'wb') as token:
            pickle.dump(credentials, token)
    return credentials


def get_drive():
    credentials = get_drive_credentials()
    return GoogleDrive(credentials)


def get_file(file_id, mimetype=None):
    if file_id:
        drive = get_drive()
        file = drive.CreateFile({'id': file_id})
        file.FetchMetadata()
        file.GetContentFile(file['title'], mimetype)
        return file['title']


if __name__ == '__main__':
    pass
