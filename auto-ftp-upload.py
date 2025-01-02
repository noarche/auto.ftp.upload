import os
import time
import ftplib
import configparser
from pathlib import Path
from fnmatch import fnmatch
from termcolor import cprint
from collections import deque

# Load configuration
config = configparser.ConfigParser()
config.read("config.ini")

# Configuration sections
ftp_config = config["FTP"]
monitor_config = config["Monitor"]
blacklist = config["Rules"].get("Blacklist", "").split(",")
whitelist = config["Rules"].get("Whitelist", "").split(",")

# FTP Credentials
ftp_ip = ftp_config["IP"]
ftp_port = int(ftp_config["Port"])
ftp_user = ftp_config["User"]
ftp_password = ftp_config["Password"]

# Monitor settings from config.ini
monitor_path = monitor_config["Path"]
interval = int(monitor_config["IntervalSeconds"])
upload_delay = int(monitor_config["UploadDelaySeconds"])
retry_attempts = int(monitor_config["RetryAttempts"])
retry_delay = int(monitor_config["RetryDelaySeconds"])


# Track seen files and changes
seen_files = {}
upload_queue = deque()

def file_should_upload(file_path):
    """Determine if a file should be uploaded based on whitelist and blacklist rules."""
    file_name = os.path.basename(file_path)
    if whitelist:
        if not any(fnmatch(file_name, pattern.strip()) for pattern in whitelist):
            return False
    if blacklist:
        if any(fnmatch(file_name, pattern.strip()) for pattern in blacklist):
            return False
    return True

def upload_file(ftp, local_path, remote_path):
    """Upload a file to the FTP server."""
    with open(local_path, "rb") as file:
        ftp.storbinary(f"STOR {remote_path}", file)
        cprint(f"Uploaded: {local_path} -> {remote_path}", "green")

def connect_to_ftp():
    """Attempt to connect to the FTP server with retries."""
    attempts = 0
    while attempts < retry_attempts:
        try:
            ftp = ftplib.FTP()
            ftp.connect(ftp_ip, ftp_port)
            ftp.login(ftp_user, ftp_password)
            cprint("Connected to FTP server.", "blue")
            return ftp
        except Exception as e:
            attempts += 1
            cprint(f"Connection failed (attempt {attempts}/{retry_attempts}): {e}", "red")
            if attempts < retry_attempts:
                cprint(f"Retrying in {retry_delay} seconds...", "yellow")
                time.sleep(retry_delay)
    raise ConnectionError("Failed to connect to FTP server after multiple attempts.")

def main():
    cprint("Starting FTP Monitor Script...", "cyan", attrs=["bold"])
    
    # Initial scan to populate seen files
    cprint("Performing initial directory scan...", "magenta")
    for root, _, files in os.walk(monitor_path):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, monitor_path)
            if file_should_upload(file_path):
                seen_files[relative_path] = os.path.getmtime(file_path)

    cprint("Monitoring for changes...", "cyan")
    
    while True:
        try:
            # Detect changes and populate the upload queue
            current_files = {}
            for root, _, files in os.walk(monitor_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, monitor_path)
                    
                    if not file_should_upload(file_path):
                        continue

                    last_modified = os.path.getmtime(file_path)
                    current_files[relative_path] = last_modified
                    
                    # Check for new or modified files
                    if relative_path not in seen_files or seen_files[relative_path] < last_modified:
                        upload_queue.append((file_path, relative_path))
            
            # Update seen files
            seen_files.update(current_files)

            # Process the upload queue
            if upload_queue:
                cprint("Changes detected, starting uploads...", "cyan")
                ftp = connect_to_ftp()
                while upload_queue:
                    local_path, remote_path = upload_queue.popleft()
                    try:
                        upload_file(ftp, local_path, remote_path)
                        time.sleep(upload_delay)
                    except Exception as e:
                        cprint(f"Failed to upload {local_path}: {e}", "red")
                ftp.quit()
            else:
                cprint("No changes detected.", "cyan")

        except Exception as e:
            cprint(f"Error: {e}", "red")

        cprint(f"Sleeping for {interval} seconds...", "yellow")
        time.sleep(interval)

if __name__ == "__main__":
    main()
