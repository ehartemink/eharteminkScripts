from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from time import sleep
import os
from tqdm import tqdm


# Unknowns:
#   * What happens when you try to create a directory that already exists?
#   * What happens when you try to overwrite an existing file?

class GoogleDriveWriter:

    FOLDER_TYPE = 'application/vnd.google-apps.folder'

    def __init__(self):
        gauth = GoogleAuth()
        gauth.CommandLineAuth()
        self.drive = GoogleDrive(gauth)

    def _ls(self, folder_id):
        file_list = self.drive.ListFile(
            {'q': f"'{folder_id}' in parents and trashed=false"}
        ).GetList()
        return {f['title']: f['id'] for f in file_list}

    def create_folder(self, local_path, remote_path, folder_name):
        parent_id = self.get_folder_id_from_path(remote_path)
        file_metadata = {
            'title': folder_name,
            'mimeType': self.FOLDER_TYPE
        }
        if parent_id is not None:
            file_metadata['parents'] = [{'id': parent_id}]

        folder = self.drive.CreateFile(file_metadata)
        folder.Upload()

    def create_file(self, local_path, remote_path):
        parent_id = self.get_folder_id_from_path(remote_path)
        f = self.drive.CreateFile(
            {'parents': [{'id': parent_id}]}
        )
        f.SetContentFile(local_path)
        f['title'] = local_path.split(sep="/")[-1]
        f.Upload()

    def ls(self, remote_path):
        folder_id = self.get_folder_id_from_path(remote_path)
        return self._ls(folder_id)


    def get_folder_id_from_path(self, remote_path):
        folders =  remote_path.split("/")

        ls_results = self._ls("root")
        for folder in folders:
            folder_id = ls_results[folder]
            ls_results = self._ls(folder_id)
        return folder_id


def driver_code(local_parent_path, remote_parent_path):
    # local_parent_path: '/media/william/PhotoAlbumW'
    # remote_path: 'PhotoAlbumW'
    google_drive_writer = GoogleDriveWriter()
    list_os_walk = list(os.walk(local_parent_path))
    for i, (local_path, local_folders, filenames) in enumerate(list_os_walk):
        print(f"Iteration {i}/{len(list_os_walk)}")
        # local_path: '/media/william/PhotoAlbumW/'
        # local_folders: ['1990andBefore', '1991']
        # filenames: ['README Photo Album.docx', '._README Photo Album.docx']

        if len(local_path) > len(local_parent_path) + 1:
            remote_path = remote_parent_path + "/" + local_path[len(local_parent_path)+1:]
        else:
            remote_path = remote_parent_path
        # remote_path: 'PhotoAlbumW'

        remote_folders_and_files = google_drive_writer.ls(remote_path)
        for folder in local_folders:
            if folder not in remote_folders_and_files:
                try:
                    google_drive_writer.create_folder(local_path, remote_path, folder)
                    sleep(0.1)
                except:
                    print(f"Creation of folder {folder} failed")
        for filename in filenames:
            if filename not in remote_folders_and_files and filename[0] != ".":
                try:
                    google_drive_writer.create_file(f"{local_path}/{filename}", remote_path)
                    sleep(0.1)
                except:
                    print(f"Creation of file {filename} failed")

driver_code('/media/william/PhotoAlbumW', 'PhotoAlbumW')



# gauth = GoogleAuth()
# drive = GoogleDrive(gauth)
# target_directory = ""
#
# upload_file_list = ['1.jpg', '2.jpg']
# for upload_file in upload_file_list:
#     gfile = drive.CreateFile({'parents': [{'id': '1pzschX3uMbxU0lB5WZ6IlEEeAUE8MZ-t'}]})
#     # Read file and set it as the content of this instance.
#     gfile.SetContentFile(upload_file)
#     gfile.Upload() # Upload the file.
#

