This Python script monitors a specified directory for new or modified files and uploads them to a remote FTP server. It uses customizable rules for including or excluding files and is fully configurable via a config.ini file. The script is designed to run continuously, automatically detecting and uploading changes while retrying failed connections.

## Features

    Directory Monitoring: Monitors a specified directory for changes at regular intervals.
    File Upload: Automatically uploads new or modified files to an FTP server.
    Configurable Rules: Supports whitelist and blacklist rules for file filtering.
    Retry Logic: Retries FTP connections up to a specified number of times with a delay.
    User-Friendly: Fully customizable settings via a config.ini file.
    Colorful Console Output: Displays progress, errors, and status updates in a clean, colorful console.

## How It Works

    Initial Directory Scan:
        On startup, the script scans the specified directory to track existing files without uploading them.

    Change Detection:
        During subsequent scans, it detects new or modified files based on their last modification time.

    Uploading:
        Detected changes are added to an upload queue.
        Files are uploaded to the FTP server one at a time, with a delay between uploads to ensure files are fully written to disk.

    Retry Mechanism:
        If an FTP connection fails, the script retries up to the configured number of attempts with a delay between retries.

    Continuous Operation:
        After completing uploads, the script sleeps for the configured interval and repeats.

## Setup Instructions

### 1. Install Dependencies

Ensure Python is installed on your system. Install required modules using:

    pip install termcolor

### 2. Configure config.ini

Edit the provided config.ini file to match your setup:

    FTP Settings: Specify the FTP server IP, port, username, and password.
    Monitor Settings: Set the directory to monitor, scan interval, and upload delay.
    Rules: Define optional whitelist and blacklist rules for file filtering.

Example config.ini:

    [FTP]
    IP = 127.0.0.1
    Port = 21
    User = username
    Password = password

    [Monitor]
    Path = /path/to/monitor
    IntervalSeconds = 900
    UploadDelaySeconds = 8
    RetryAttempts = 5
    RetryDelaySeconds = 30

    [Rules]
    Blacklist = *.tmp,*.log
    Whitelist = *.html

### 3. Run the Script

Run the script from the command line:

    python auto-ftp-upload.py

## Usage Notes

    File Filtering: Whitelist rules have higher priority than blacklist rules. If a file matches both, it will be included based on the whitelist.
    Log Messages: The script provides status updates in the terminal using color-coded messages.
    Interrupting the Script: Use Ctrl+C to stop the script.

## Troubleshooting

    "Invalid literal for int()" Error:
        Ensure comments in the config.ini file are on separate lines.
    FTP Connection Issues:
        Check the FTP server credentials and ensure the server is accessible.
        The script retries failed connections automatically.
