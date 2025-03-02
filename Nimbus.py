import os
import subprocess
import time
import re
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import configparser
import hashlib
import boto3
from botocore.exceptions import NoCredentialsError
import pyperclip
from tqdm import tqdm

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

config = configparser.ConfigParser()
config.read("config.ini")
if not config.has_section("OPTIONS"):
    config.add_section("OPTIONS")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

def n():
    print("\n")

def cls():
    os.system("cls")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

def strip_ansi(text):
    return re.sub(r"\033\[[0-9;]*m", "", text)  

def print_centered(text):
    for line in text.splitlines():
        visible_length = len(strip_ansi(line))  
        padding = max(0, os.get_terminal_size().columns // 2 - visible_length // 2)
        print(" " * padding + line)

def print_title():
    nimbus = ""
    red = 40

    title = """
──────────────────────⋆ ⋅ ☆ ⋅ ⋆──────────────────────

███╗   ██╗██╗███╗   ███╗██████╗ ██╗   ██╗███████╗
████╗  ██║██║████╗ ████║██╔══██╗██║   ██║██╔════╝
██╔██╗ ██║██║██╔████╔██║██████╔╝██║   ██║███████╗
██║╚██╗██║██║██║╚██╔╝██║██╔══██╗██║   ██║╚════██║
██║ ╚████║██║██║ ╚═╝ ██║██████╔╝╚██████╔╝███████║
╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝╚═════╝  ╚═════╝ ╚══════╝

──────────────────────⋆ ⋅ ☆ ⋅ ⋆──────────────────────
    """

    for line in title.splitlines():
        nimbus += (f"\033[38;2;{red};0;220m{line}\033[0m\n")
        if red < 255:
            red += 15
            if red > 255:
                red = 255
    
    print_centered(nimbus)

def init():
    cls()
    print_title()
    
    print_centered("\033[5mLogging in...\033[0m")

    try:
        subprocess.check_call(["ping", "-n", "1", "8.8.8.8"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        loggedin = True
    except subprocess.CalledProcessError:
        loggedin = False
        print_centered("\033[91mFailed to log in, are you connected to Wi-Fi?\033[0m")
        input()

    if loggedin == True:
        global user_uuid, username, ip

        ip = subprocess.check_output("ipconfig", shell=True).decode().split("IPv4 Address")[1].split(":")[1].strip().split("\r")[0]

        user_uuid = get_hwid()[:6]

        username = os.getlogin()
        identifier = f"{username} - {user_uuid}"

        print_centered(f"\033[92mLogged in successfully as {identifier}!\033[0m")
        time.sleep(2)
        main()

def main():
    while True:
        cls()
        print_title()

        print_centered("\033[38;2;255;0;220mby lioen (barker.rowan@sugarsalem.com)\033[0m")
        n()
        n()
        print_centered("[1.] Upload a File                           [2.] Download a File")
        n()
        print_centered("[3.] Settings                                           [4.] Exit")
        n()
        print_centered("─" * (os.get_terminal_size().columns - 3))
        n()
        choice = input("    > ")

        if choice.isdigit():
            choice = int(choice)
            if choice == 1:
                upload_file()
            elif choice == 2:
                download_file()
            elif choice == 3:
                settings()
            elif choice == 4:
                exit()
            else:
                print_centered("\033[91mInvalid choice. Please select a valid option.\033[0m")
                time.sleep(2)
        else:
            print_centered("\033[91mInvalid input. Please enter a number.\033[0m")
            time.sleep(2)

def upload_file():
    print_centered("\033[38;2;173;216;230mPlease select the File/Folder you would like to upload.\033[0m")
    filepath = askopenfilename()  

    if filepath:
        print_centered(f"\033[5mUploading file: {filepath}\033[0m")
        n()
        code = hashlib.sha256(os.urandom(1024)).hexdigest()[:7]
        bucket = config.get("OPTIONS", "bucket")
        pubkey = config.get("OPTIONS", "pubkey")
        privkey = config.get("OPTIONS", "privkey")

        s3 = boto3.client('s3', aws_access_key_id=pubkey, aws_secret_access_key=privkey)

        try:
            file_name = os.path.basename(filepath)
            file_size = os.path.getsize(filepath)
        
            with tqdm(total=file_size, unit='B', unit_scale=True, desc=f"   Uploading {file_name}") as pbar:
                def progress_callback(bytes_transferred):
                    pbar.update(bytes_transferred)

                s3.upload_file(filepath, bucket, code, Callback=progress_callback, ExtraArgs={
                    'Metadata': {
                        'filename': os.path.basename(filepath),
                        'identifier': f"{username} - {user_uuid}"
                    },
                    'Tagging': f"IP={ip}&Motherboard={mb}&Disk={disk}"
                })

            n()
            print_centered(f"\033[92mFile uploaded successfully with code: {code}. It has also been copied to your clipboard.\033[0m")
            pyperclip.copy(code)
        except FileNotFoundError:
            print_centered("\033[91mThe file was not found.\033[0m")
        except NoCredentialsError:
            print_centered("\033[91mCredentials not available.\033[0m")
        except Exception as e:
            print_centered(f"\033[91mAn error occurred: {str(e)}\033[0m")

        time.sleep(5)
    else:
        print_centered("No file selected.")
        time.sleep(2)

def download_file():
    print_centered("\033[38;2;173;216;230mPlease enter the code of the file you would like to download.\033[0m")
    code = input("    > ")

    if code:
        bucket = config.get("OPTIONS", "bucket")
        pubkey = config.get("OPTIONS", "pubkey")
        privkey = config.get("OPTIONS", "privkey")

        s3 = boto3.client('s3', aws_access_key_id=pubkey, aws_secret_access_key=privkey)

        try:
            response = s3.head_object(Bucket=bucket, Key=code)
            if 'Metadata' in response:
                original_filename = response['Metadata']['filename']
                identifier = response['Metadata']['identifier']
                file_size = response['ContentLength']
                print_centered(f"\033[38;2;173;216;230mFile found: {original_filename} ({file_size} bytes) uploaded by {identifier}.\033[0m")
                n()
                print_centered("\033[38;2;173;216;230mWould you like to download this file?\033[0m")
                n()
                print_centered("[1.] Yes                                            [2.] No")
                n()
                choice = input("    > ")
                if choice.isdigit():
                    choice = int(choice)
                    if choice == 1:
                        pass
                    elif choice == 2:
                        return
                    else:
                        print_centered("\033[91mInvalid choice. Please select a valid option.\033[0m")
                        time.sleep(2)
                        return
                else:
                    print_centered("\033[91mInvalid input. Please enter a number.\033[0m")
                    time.sleep(2)
                    return
            else:
                print_centered("\033[91mNo file found with the provided code.\033[0m")
                time.sleep(2)
                return
        except Exception as e:
            print_centered(f"\033[91mNimbus couldn't find a file matching that code.\033[0m")
            time.sleep(2)
            return

        n()

        try:
            with tqdm(total=file_size, unit='B', unit_scale=True, desc=f"   Downloading {original_filename}") as pbar:
                def progress_callback(bytes_transferred):
                    pbar.update(bytes_transferred)

                s3.download_file(bucket, code, original_filename, Callback=progress_callback)
            
            n()
            print_centered(f"\033[92mFile downloaded successfully as {original_filename}.\033[0m")
        except FileNotFoundError:
            print_centered("\033[91mThe file was not found.\033[0m")
        except NoCredentialsError:
            print_centered("\033[91mCredentials not available.\033[0m")
        except Exception as e:
            print_centered(f"\033[91mAn error occurred: {str(e)}\033[0m")

        time.sleep(5)
    else:
        print_centered("\033[91mInvalid input. Please enter a valid code.\033[0m")
        time.sleep(2)

def settings():
    while True:
        cls()
        print_title()
        print_centered("Settings")
        n()
        print_centered("[1.] Change bucket                           [2.] Change Private Key")
        n()
        print_centered("[3.] Change Public Key                         [4.] Reset to Default")
        n()
        print_centered("[5.] Exit")
        n()
        print_centered("─" * (os.get_terminal_size().columns - 3))
        n()
        choice = input("    > ")

        if choice.isdigit():
            choice = int(choice)
            if choice == 1:
                change_bucket()
            elif choice == 2:
                change_privkey()
            elif choice == 3:
                change_pubkey()
            elif choice == 4:
                reset_to_default()
            elif choice == 5:
                return
            else:
                print_centered("\033[91mInvalid choice. Please select a valid option.\033[0m")
                time.sleep(2)
        else:
            print_centered("\033[91mInvalid input. Please enter a number.\033[0m")
            time.sleep(2)

def change_bucket():
    if not config.has_section("OPTIONS"):
        config.add_section("OPTIONS")
    n()
    print_centered("What bucket would you like to use? ")
    n()
    bucket = input("Type Here:").strip()
    if bucket:
        config.set("OPTIONS", "bucket", bucket)
        save_config()
    else:
        print_centered("\033[91mInvalid input. Please enter a valid bucket name.\033[0m")
        time.sleep(2)

def change_privkey():
    if not config.has_section("OPTIONS"):
        config.add_section("OPTIONS")
    n()
    print_centered("Enter your Private Key below ")
    n()
    privkey = input("Type Here:").strip()
    if privkey:
        config.set("OPTIONS", "privkey", privkey)
        save_config()
    else:
        print_centered("\033[91mInvalid input. Please enter a valid private key.\033[0m")
        time.sleep(2)

def change_pubkey():
    if not config.has_section("OPTIONS"):
        config.add_section("OPTIONS")
    n()
    print_centered("Enter your Public Key below ")
    n()
    pubkey = input("Type Here:").strip()
    if pubkey:
        config.set("OPTIONS", "pubkey", pubkey)
        save_config()
    else:
        print_centered("\033[91mInvalid input. Please enter a valid public key.\033[0m")
        time.sleep(2)

def reset_to_default():
    if not config.has_section("OPTIONS"):
        config.add_section("OPTIONS")
    config["OPTIONS"] = {
        "pubkey": "",
        "privkey": "",
        "bucket": ""
    }
    save_config()
    print_centered("Configuration reset to default values.")
    time.sleep(2)

def save_config():
    with open("config.ini", "w") as configfile:
        config.write(configfile)
    print_centered("Settings updated successfully.")
    time.sleep(2)

def get_hwid():
    try:
        global mb, disk
        mb = subprocess.check_output("wmic csproduct get uuid", shell=True).decode().split("\n")[1].strip()
        disk = subprocess.check_output("wmic diskdrive get serialnumber", shell=True).decode().split("\n")[1].strip()
        output = f"{mb}{disk}"
        return output
    except Exception as e:
        return "UNKNOWN"
    
def startup():
    config = configparser.ConfigParser()
    config_file = "config.ini"

    if os.path.exists(config_file):
        config.read(config_file)
        if (config.has_section("OPTIONS") and 
            config.has_option("OPTIONS", "pubkey") and config.get("OPTIONS", "pubkey") and
            config.has_option("OPTIONS", "privkey") and config.get("OPTIONS", "privkey") and
            config.has_option("OPTIONS", "bucket") and config.get("OPTIONS", "bucket")):
            init()
        else:
            global haspubkey, hasprivkey, hasbucket

            haspubkey = config.has_option("OPTIONS", "pubkey")
            hasprivkey = config.has_option("OPTIONS", "privkey")
            hasbucket = config.has_option("OPTIONS", "bucket")

            corruptedconfig()
    else:
        config["OPTIONS"] = {
            "pubkey": "",
            "privkey": "",
            "bucket": ""
        }
        with open(config_file, "w") as configfile:
            config.write(configfile)
        firststartup()

def firststartup():
    print_title()
    n()
    print_centered("Welcome to Nimbus! Let's get you set up.")
    print_centered("Press any key to continue...")
    input()
    cls()

    print_title()
    n()

    print_centered("Would you like to use the default bucket, or set a custom one?")
    n()

    print_centered("[1.] Default bucket (Recommended)    [2.] Custom bucket")
    n()

    while True:
        choice = input("    > ")
        if choice.isdigit():
            choice = int(choice)
            if choice == 1:
                print_centered("Perfect! Setting things up...")
                time.sleep(1)
                config["OPTIONS"] = {
                    "pubkey": "",
                    "privkey": "",
                    "bucket": ""
                }
                with open("config.ini", "w") as configfile:
                    config.write(configfile)
                print_centered("Configuration set to default values.")
                time.sleep(2)
                init()
                break
            elif choice == 2:
                print_centered("Alright! Taking you to the configuration menu...")
                time.sleep(1)
                customdata()
                break
            else:
                print_centered("\033[91mInvalid choice. Please select a valid option.\033[0m")
                time.sleep(2)
        else:
            print_centered("\033[91mInvalid input. Please enter a number.\033[0m")
            time.sleep(2)

def customdata():
    cls()
    print_title()
    if not config.has_section("OPTIONS"):
        config.add_section("OPTIONS")
    print_title()
    n()
    print_centered("What bucket would you like to use? ")
    n()
    bucket = input("Type Here:").strip()
    if bucket:
        config.set("OPTIONS", "bucket", bucket)
    else:
        print_centered("\033[91mInvalid input. Please enter a valid bucket name.\033[0m")
        time.sleep(2)
        customdata()
        return

    n()
    print_centered("Please enter your Public Key.")
    n()
    pubkey = input().strip()
    if pubkey:
        config.set("OPTIONS", "pubkey", pubkey)
    else:
        print_centered("\033[91mInvalid input. Please enter a valid public key.\033[0m")
        time.sleep(2)
        customdata()
        return

    n()
    print_centered("Please enter your Private Key.")
    n()
    privkey = input().strip()
    if privkey:
        config.set("OPTIONS", "privkey", privkey)
    else:
        print_centered("\033[91mInvalid input. Please enter a valid private key.\033[0m")
        time.sleep(2)
        customdata()
        return

    with open("config.ini", "w") as configfile:
        config.write(configfile)

    n()
    print_centered("Configuration finished! Press any key to go to the main menu...")
    input()
    init()

def corruptedconfig():
    cls()
    print_title()
    n()
    print_centered("It looks like something's off with your settings. Let's fix that!")
    n()
    print_centered("Press any key to continue...")
    input()
    cls()
    print_title()
    config.read("config.ini")

    if not config.has_section("OPTIONS"):
        config.add_section("OPTIONS")

    if not config.has_option("OPTIONS", "bucket") or not config.get("OPTIONS", "bucket"):
        n()
        print_centered("What bucket would you like to use? ")
        n()
        bucket = input("Type Here:").strip()
        if bucket:
            config.set("OPTIONS", "bucket", bucket)
        else:
            print_centered("\033[91mInvalid input. Please enter a valid bucket name.\033[0m")
            time.sleep(2)
            corruptedconfig()
            return

    if not config.has_option("OPTIONS", "pubkey") or not config.get("OPTIONS", "pubkey"):
        n()
        print_centered("Please enter your Public Key.")
        n()
        pubkey = input().strip()
        if pubkey:
            config.set("OPTIONS", "pubkey", pubkey)
        else:
            print_centered("\033[91mInvalid input. Please enter a valid public key.\033[0m")
            time.sleep(2)
            corruptedconfig()
            return
    
    if not config.has_option("OPTIONS", "privkey") or not config.get("OPTIONS", "privkey"):
        n()
        print_centered("Please enter your Private Key.")
        n()
        privkey = input().strip()
        if privkey:
            config.set("OPTIONS", "privkey", privkey)
        else:
            print_centered("\033[91mInvalid input. Please enter a valid private key.\033[0m")
            time.sleep(2)
            corruptedconfig()
            return

    with open("config.ini", "w") as configfile:
        config.write(configfile)

    n()
    print_centered("Configuration updated successfully.")
    time.sleep(2)
    main()

cls()

startup()
