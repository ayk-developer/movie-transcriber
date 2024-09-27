# this program will loop and watch the files in a given dir. If there is any new files,
#it will call a function. if not, it will just sleep and run at a time again

import json
import os
import time
from pikpak_file_translator import *

folder_to_watch = "/home/opc/PIKPAK/to_sub"

converted_files_path = "converted_files.json"
converted_files = set()

files_to_convert = []

def load_converted_files():
    """
    Load the set of scanned files from the JSON file.
    """
    global converted_files
    if os.path.exists(converted_files_path):
        with open(converted_files_path, 'r') as f:
            converted_files = set(json.load(f))
        print(f"Loaded {len(converted_files)} scanned files from {converted_files_path}")

def save_converted_files():
    """
    Save the set of scanned files to the JSON file.
    """
    with open(converted_files_path, 'w') as f:
        json.dump(list(converted_files), f)
    print(f"Saved {len(converted_files)} scanned files to {converted_files_path}")

def scan_folder(folder_to_watch):
    """
    Scan the folder and subfolders for new mp4 files and add them to the queue.
    """
    for root, dirs, files in os.walk(folder_to_watch):
        for file in files:
            if file.endswith('.mp4'):
                file_path = os.path.join(root, file)
                # Check if the file is already in the queue or processed
                if file_path not in converted_files and file_path not in files_to_convert:
                    print(f"New MP4 file detected: {file_path}")
                    files_to_convert.append(file_path)


def daemon():
    load_converted_files()
    while True:
        scan_folder(folder_to_watch)
        if(len(files_to_convert)>0):
            file_to_convert =files_to_convert[0]
            # convert file here
            translate(file_to_convert)
            converted_files.add(file_to_convert)
            save_converted_files()
            files_to_convert.pop(0)
            print(file_to_convert," converted")
        time.sleep(10)

if __name__ == "__main__":
    daemon()

