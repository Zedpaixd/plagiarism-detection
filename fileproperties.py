import os
import zipfile
import rarfile
from datetime import datetime, timedelta
from collections import defaultdict

class FileProperties:
    def __init__(self, path):
        self.path = path
        self.files = {}
        for file_name in os.listdir(self.path):
            stat = os.stat(os.path.join(self.path, file_name))
            self.files[file_name] = [
                stat.st_atime,
                stat.st_mtime,
                stat.st_birthtime
            ]
        self.extract_homeworks()   # uncomment this line to extract archives

    
    def debugprint(self):
        import pprint
        print(f"file: [last_accessed, last_modified, created]")
        pprint.pprint(self.files)

    def extract_homeworks(self):
        # delete every folder in the directory
        for file_name in os.listdir(self.path):
            full_path = os.path.join(self.path, file_name)
            if os.path.isdir(full_path):
                import shutil
                shutil.rmtree(full_path)
        
        """Unzips or unrars every single file in the directory into its own folder."""
        for file_name in os.listdir(self.path):
            full_path = os.path.join(self.path, file_name)

            if os.path.isdir(full_path):
                continue
            
            # create a folder named after the archive
            base_name, ext = os.path.splitext(file_name)
            extract_path = os.path.join(self.path, base_name)
            
            # handle .zip files
            if ext.lower() == ".zip":
                with zipfile.ZipFile(full_path, 'r') as zip_ref:
                    os.makedirs(extract_path, exist_ok=True)
                    zip_ref.extractall(extract_path)

            # handle .rar files
            elif ext.lower() == ".rar":
                with rarfile.RarFile(full_path, 'r') as rar_ref:
                    os.makedirs(extract_path, exist_ok=True)
                    rar_ref.extractall(extract_path)

    def _file_nighly_modified_files(self, delta_minutes=5):
        """
        Groups files in subfolders (not the main folder) by last edited times within a given delta.
        """
        subfolder_files = []

        # traverse the directory tree but skip the root folder files
        for root, dirs, files in os.walk(self.path):
            # skip root folder
            if root == self.path:
                continue

            for file_name in files:
                full_path = os.path.join(root, file_name)
                try:
                    stat = os.stat(full_path)
                    creation_time = getattr(stat, 'st_mtime', stat.st_mtime)
                    subfolder_files.append((full_path, datetime.fromtimestamp(creation_time)))
                except AttributeError:
                    print(f"Could not retrieve edit time time for {file_name}")

        # dictionary to group files by similar last editing times
        grouped_files = defaultdict(list)
        delta = timedelta(minutes=delta_minutes)

        for file_path, creation_time in subfolder_files:
            matched = False
            for key_time in grouped_files.keys():
                if abs((key_time - creation_time).total_seconds()) <= delta.total_seconds():
                    grouped_files[key_time].append(file_path)
                    matched = True
                    break
            if not matched:
                grouped_files[creation_time].append(file_path)

        # filter out groups with less than 2 files and return them as a list of lists
        return [files for files in grouped_files.values() if len(files) > 1]

    def copy_paste_plagiarism(self, delta_minutes=5):
        i = 1
        for entry in self._file_nighly_modified_files(delta_minutes):
            print(f"Case of possible plagirism no. {i}")
            i+=1
            for file in entry:
                print(file)