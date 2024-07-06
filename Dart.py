import tkinter as tk
from tkinter import filedialog
import hashlib
import boto3
import os
from tqdm import tqdm
import time

# Network check
try:
    urllib.request.urlopen('http://www.google.com')
except urllib.error.URLError:
    print("You need internet to use the application.")
    time.sleep(1)
    sys.exit(1)

# Color codes
CBLINK = '\033[5m'
CRED = '\033[91m'
CGREEN = '\033[92m'
CITALICS = '\033[3m'
CUNDERLINE = '\033[4m'
CEND = '\033[0m'

print('\n')
print(CITALICS + CUNDERLINE + CGREEN + "Welcome to Dart!" + CEND)

# Initialize S3 client
s3 = boto3.client('s3', aws_access_key_id='',
                         aws_secret_access_key='')

def upload_file():
    # Create a unique code
    code = hashlib.sha256(os.urandom(1024)).hexdigest()[:6]

    # Open file dialog to select file
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()

    # Upload file to S3 with the original filename and filetype. Use the unique code as the key
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    progress_bar = tqdm(total=file_size, unit='B', unit_scale=True, desc=' Uploading', leave=False)

    def progress_callback(bytes_uploaded):
        progress_bar.update(bytes_uploaded - progress_bar.n)

    s3.upload_file(file_path, 'fost', code, ExtraArgs={'Metadata': {'original_filename': file_name}}, Callback=progress_callback)
    progress_bar.close()
    print('\n')
    print(CGREEN + CITALICS + f"File uploaded successfully! Your unique code is: {code}." + CEND)


def download_file():
    # Get the unique code from the user
    code = input(" Enter the unique code: ")
    print(CBLINK + ' Please wait...' + CEND)

    # Download the file from S3 with 
    # the original filename and filetype
    try:
        response = s3.head_object(Bucket='fost', Key=code)
        file_name = response['Metadata']['original_filename']
        file_size = int(response['ContentLength'])
        progress_bar = tqdm(total=file_size, unit='B', unit_scale=True, desc=' Downloading', leave=False)

        def progress_callback(bytes_downloaded):
            progress_bar.update(bytes_downloaded - progress_bar.n)

        s3.download_file('fost', code, file_name, Callback=progress_callback)
        progress_bar.close()
        print(CGREEN + CITALICS + f"File downloaded successfully! File saved as: {file_name}" + CEND)

    except Exception as e:
        print(CRED + CUNDERLINE + f"Error downloading file: {e}" + CEND)

def main():
    while True:
        print('\n')
        print(" 1. Upload file")
        print(" 2. Download file")
        print(" 3. Exit")
        print('\n')
        choice = input(" Enter your choice: ")

        if choice == "1":
            upload_file()
        elif choice == "2":
            download_file()
        elif choice == "3":
            break
        else:
            os.system('cls')
            print('\n')
            print(CRED + CUNDERLINE + "Invalid choice. Please try again." + CEND)

if __name__ == "__main__":
    main()
