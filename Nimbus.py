import tkinter as tk
from tkinter import filedialog
import hashlib
import boto3
import os
from tqdm import tqdm
import fade
import time
import configparser

configfile = "config.ini"

CRED = '\033[91m'
CGREEN = '\033[92m'
CITALICS = '\033[3m'
CEND = '\033[0m'

# Functions
def cls():
    os.system("cls")

def n():
    print("")

def readconfig():
    config.read(configfile)

def writeconfig():
    configfile = "config.ini"
    with open(configfile, "w") as configfile:
        config.write(configfile)

def upload():
    readconfig()
    bucket = config["Hosting Info"]["bucket"]
    pubkey = config["Hosting Info"]["pubkey"]
    privkey = config["Hosting Info"]["privkey"]
    s3 = boto3.client('s3', aws_access_key_id=pubkey,
                         aws_secret_access_key=privkey)
    
    cls()
    n()
    print("Please select your file / zip folder.")
    time.sleep(0.5)

    code = hashlib.sha256(os.urandom(1024)).hexdigest()[:6]

    # Open file dialog to select file
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()

    # Upload file to S3 with the original filename and filetype. Use the unique code as the key
    file_name = os.path.basename(file_path)

    # Get the file size to track progress
    file_size = os.path.getsize(file_path)

    # Create a tqdm progress bar
    with tqdm(total=file_size, unit='B', unit_scale=True, desc=f"Uploading {file_name}") as pbar:
        # Define a progress callback function to update the progress bar
        def progress_callback(bytes_transferred):
            pbar.update(bytes_transferred)

        # Upload file to S3 with the progress callback
        s3.upload_file(file_path, bucket, code, ExtraArgs={'Metadata': {'original_filename': file_name}}, Callback=progress_callback)
    
    cls()
    n()
    print(CGREEN + CITALICS + f"File uploaded to bucket {bucket}! Your code is {code}!" + CEND)
    main()

def download():
    readconfig()
    bucket = config["Hosting Info"]["bucket"]
    pubkey = config["Hosting Info"]["pubkey"]
    privkey = config["Hosting Info"]["privkey"]
    s3 = boto3.client('s3', aws_access_key_id=pubkey,
                         aws_secret_access_key=privkey)
    
    n()
    # Get the unique code from the user
    code = input("Enter the unique code: ")

    try:
        # Get the file's metadata to retrieve the original filename
        response = s3.head_object(Bucket=bucket, Key=code)
        file_name = response['Metadata']['original_filename']

        # Get the file size for the progress bar
        file_size = response['ContentLength']

        # Create a tqdm progress bar
        with tqdm(total=file_size, unit='B', unit_scale=True, desc=f"Downloading {file_name}") as pbar:
            # Define a progress callback function to update the progress bar
            def progress_callback(bytes_transferred):
                pbar.update(bytes_transferred)

            # Download the file from S3 with the progress callback
            s3.download_file(bucket, code, file_name, Callback=progress_callback)
        
        cls()
        print(CGREEN + CITALICS + f"File downloaded successfully! File saved as: {file_name}" + CEND)
        main()

    except Exception as e:
        cls()
        print(CRED + f"Error downloading file: {e}" + CEND)
        main()


# Pages
def main():
    n()
    title = fade.purplepink("███╗   ██╗██╗███╗   ███╗██████╗ ██╗   ██╗███████╗" + "\n" + "████╗  ██║██║████╗ ████║██╔══██╗██║   ██║██╔════╝" + "\n" + "██╔██╗ ██║██║██╔████╔██║██████╔╝██║   ██║███████╗" + "\n" + "██║╚██╗██║██║██║╚██╔╝██║██╔══██╗██║   ██║╚════██║" + "\n" + "██║ ╚████║██║██║ ╚═╝ ██║██████╔╝╚██████╔╝███████║" + "\n" + "╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝╚═════╝  ╚═════╝ ╚══════╝")
    print(title)
    print("by lioen (barker.rowan@sugarsalem.com)")
    n()
    print("[1.] Upload a File")
    print("[2.] Download a File")
    print("[3.] Settings")
    print("[4.] Exit")
    n()

    key = input()

    if key == '1':
        upload()

    elif key == '2':
        download()

    elif key == '3':
        settingsmain()

    elif key == '4':
        n()
        print("Thanks for using Nimbus! Exiting now...")
        time.sleep(1)
        cls()
        exit()

def customization():
    cls()
    main()

def changebucket():
    cls()
    n()
    bucketname = input("Enter your bucket name here: ")

    readconfig()
    if config.has_section("Hosting Info"):
        config.set("Hosting Info", "bucket", bucketname)

    else:
        config["Hosting Info"] = {"bucket": bucketname}
    writeconfig()

    host()

def changepubkey():
    cls()
    n()
    publicapikey = input("Enter it here: ")

    readconfig()
    if config.has_section("Hosting Info"):
        config.set("Hosting Info", "pubkey", publicapikey)

    else:
        config["Hosting Info"] = {"pubkey": publicapikey}
    writeconfig()

def changeprivkey():
    cls()
    n()
    privateapikey = input("Enter it here: ")

    readconfig()
    if config.has_section("Hosting Info"):
        config.set("Hosting Info", "privkey", privateapikey)

    else:
        config["Hosting Info"] = {"privkey": privateapikey}
    writeconfig()

def host():
    cls()
    n()
    print("Select what you'd like to change.")
    n()
    print("[1.] Bucket Name")
    print("[2.] Public Key")
    print("[3.] Private Key")
    print("[4.] Back")
    n()

    key = input()

    if key == '1':
        changebucket()

    elif key == '2':
        changepubkey()

    elif key == '3':
        changeprivkey()

    elif key == '4':
        settingsmain()

    else:
        host()
        
def alldone():
    cls()
    n()
    print("All done with first time setup! Sending you to the main menu now.")
    time.sleep(2)
    cls()
    main()

def hostprompt():
    cls()
    n()
    print("Are you planning on using the default location or a custom one?")
    n()
    print("[1.] Yes, I will use the defualt location.")
    print("[2.] No, I will use a custom location.")
    n()

    key = input()

    if key == '1':
        n()
        print("Okay! Setting things up for you!")

        readconfig()
        if config.has_section("Hosting Info"):
            config.set("Hosting Info", "bucket", "fost")

        else:
            config["Hosting Info"] = {"bucket": "fost"}
        writeconfig()
        readconfig()
        if config.has_section("Hosting Info"):
            config.set("Hosting Info", "pubkey", "")

        else:
            config["Hosting Info"] = {"pubkey": ""}
        writeconfig()
        readconfig()
        if config.has_section("Hosting Info"):
            config.set("Hosting Info", "privkey", "")

        else:
            config["Hosting Info"] = {"privkey": ""}
        writeconfig()

        cls()
        main()
    
    if key == '2':
        host()

def customizationprompt():
    cls()
    n()
    print("Would you like to Customize Nimbus?")
    n()
    print("[1.] Sure, I'll customize my client!")
    print("[2.] No, I'd like to keep the default looks.")
    n()

    key = input()

    if key == '1':
        print("Okay! Sending you to the customization menu now...")
        time.sleep(1)
        customization()
    
    if key == '2':
        n()
        print("Okay, no problem! you can always change your mind later.")
        time.sleep(1)
        alldone()

def hostinglocation():
    cls()
    n()
    print("Would you like to use the default file hosting location? (Recommended for beginners, but less secure due to API keys being public knowledge.)")
    n()
    print("[1.] Yes, I will use the defualt location.")
    print("[2.] No, I will use a custom location.")
    n()

    key = input()

    if key == '1':
        n()
        print("Wonderful! Setting things up...")
        time.sleep(1)
        readconfig()
        if config.has_section("Hosting Info"):
            config.set("Hosting Info", "bucket", "fost")

        else:
            config["Hosting Info"] = {"bucket": "fost"}
        if config.has_section("Hosting Info"):
            config.set("Hosting Info", "pubkey", "")

        else:
            config["Hosting Info"] = {"pubkey": ""}
        if config.has_section("Hosting Info"):
            config.set("Hosting Info", "privkey", "")

        else:
            config["Hosting Info"] = {"privkey": ""}
        writeconfig()
    
    elif key == '2':
        cls()
        n()
        print("Okay! First I'll need the name of the bucket.")
        n()
        bucketname = input("Enter it here: ")

        readconfig()
        if config.has_section("Hosting Info"):
            config.set("Hosting Info", "bucket", bucketname)

        else:
            config["Hosting Info"] = {"bucket": bucketname}

        n()
        print("Thanks! Dont Worry if you mistyped, you can always change it later.")
        n()
        print("Next, I'll need your public API key. If the bucket is not owned by you, then this key should be from an IAM user dedicated to you with specific permissions.")
        n()
        publicapikey = input("Enter it here: ")

        if config.has_section("Hosting Info"):
            config.set("Hosting Info", "pubkey", publicapikey)

        else:
            config["Hosting Info"] = {"pubkey": publicapikey}

        n()
        print("Thanks! Dont Worry if you mistyped, you can always change it later.")
        n()
        print("Next, I'll need your private API key. If the bucket is not owned by you, then this key should be from an IAM user dedicated to you with specific permissions.")
        n()
        privateapikey = input("Enter it here: ")

        if config.has_section("Hosting Info"):
            config.set("Hosting Info", "privkey", privateapikey)

        else:
            config["Hosting Info"] = {"privkey": privateapikey}
        writeconfig()
        
        n()
        print("Thanks! Remember, keep a backup of those keys, if you lose them or change any of this data later, it will be a headache to get them back.")
        time.sleep(2)

    else:
        hostinglocation()

    customizationprompt()
    
def firststartup():
    hostinglocation()

def settingsmain():
    cls()
    n()

    print("Select Configuration:")

    n()

    print("[1.] Customization")
    print("[2.] Bucket and Keys")
    print("[3.] Back")

    n()

    key = input()
    
    if key == '1':
        customization()

    if key == '2':
        hostprompt()
    
    if key == '3':
        cls()
        main()

# Initialization
config = configparser.ConfigParser()
configfile = "config.ini"

if os.path.exists(configfile):
    cls()
    main()
else:
    open(configfile, "w").close()
    cls()
    firststartup()
