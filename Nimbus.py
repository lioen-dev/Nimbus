import easygui
import hashlib
import boto3
import os
import time
from tqdm import tqdm
import keyboard

# Color codes
CBLINK = '\033[5m'
CRED = '\033[91m'
CGREEN = '\033[92m'
CITALICS = '\033[3m'
CUNDERLINE = '\033[4m'
CEND = '\033[0m'

print('\n')

print(CITALICS + CGREEN + "███╗   ██╗██╗███╗   ███╗██████╗ ██╗   ██╗███████╗" + CEND)
print(CITALICS + CGREEN + "████╗  ██║██║████╗ ████║██╔══██╗██║   ██║██╔════╝" + CEND)
print(CITALICS + CGREEN + "██╔██╗ ██║██║██╔████╔██║██████╔╝██║   ██║███████╗" + CEND)
print(CITALICS + CGREEN + "██║╚██╗██║██║██║╚██╔╝██║██╔══██╗██║   ██║╚════██║" + CEND)
print(CITALICS + CGREEN + "██║ ╚████║██║██║ ╚═╝ ██║██████╔╝╚██████╔╝███████║" + CEND)
print(CITALICS + CGREEN + "╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝╚═════╝  ╚═════╝ ╚══════╝" + CEND)

# Initialize S3 client
s3 = boto3.client('s3', aws_access_key_id='',
                         aws_secret_access_key='')

def upload_file():
    os.system("cls")
    print("Please select your file / zip folder.")
    time.sleep(1)
# Create a unique code
    code = hashlib.sha256(os.urandom(1024)).hexdigest()[:6]

    # Use EasyGUI to open file dialog and select file
    file_path = easygui.fileopenbox(title="Select a file to upload")
    if not file_path:
        print(CRED + CITALICS + "No file selected. Upload cancelled." + CEND)
        return

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
        print(" [1.] Upload file")
        print(" [2.] Download file")
        print(" [3.] Exit")
        print('\n')
        print(" Enter your choice: ")
        choice = keyboard.read_event().name

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
