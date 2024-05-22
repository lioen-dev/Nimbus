import tkinter as tk
from tkinter import filedialog
import hashlib
import boto3
import os

#color code variables
CITALIC = '\33[3m'
CBLINK = '\33[5m'
CGREEN  = '\33[32m'
CRED   = '\33[31m'
CEND = '\033[0m'


# Initialize S3 client
s3 = boto3.client('s3', aws_access_key_id='lmao',
                         aws_secret_access_key='heh you thought')

def upload_file():
    # Create a unique code
    code = hashlib.sha256(os.urandom(1024)).hexdigest()[:6]

    # Open file dialog to select file
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()

    # Upload file to S3 with the original filename and filetype. Use the unique code as the key
    file_name = os.path.basename(file_path)
    s3.upload_file(file_path, 'fost', code, ExtraArgs={'Metadata': {'original_filename': file_name}})
    print('\n')
    print(CBLINK + 'Please wait...' + CEND)
    print(CITALIC + CGREEN + f"File uploaded successfully! Your unique code is: {code}" + CEND)

def download_file():
    # Get the unique code from the user
    code = input("Enter the unique code: ")
    print(CBLINK + 'Please wait...' + CEND)

    # Download the file from S3 with the original filename and filetype
    try:
        response = s3.head_object(Bucket='fost', Key=code)
        file_name = response['Metadata']['original_filename']
        s3.download_file('fost', code, file_name)
        print(CGREEN + CITALIC + f"File downloaded successfully! File saved as: {file_name}" + CEND)

    except Exception as e:
        print(f"Error downloading file: {e}")

def main():
    while True:
        print('\n')
        print("1. Upload file")
        print("2. Download file")
        print("3. Exit")
        print('\n')
        choice = input("Enter your choice: ")

        if choice == "1":
            upload_file()
        elif choice == "2":
            download_file()
        elif choice == "3":
            break
        else:
            os.system('cls')
            print('\n')
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
