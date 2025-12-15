#!/usr/bin/env python3
"""
Syncthing Device Setup Script
Adds Windows device and shares ocr_inbox folder
"""

import requests
import json
import sys
from typing import Dict, Any

# Configuration
SYNCTHING_HOST = "192.168.3.43"
SYNCTHING_PORT = "8384"
SYNCTHING_URL = f"http://{SYNCTHING_HOST}:{SYNCTHING_PORT}"

# Windows device details
WINDOWS_DEVICE_ID = "JTZ3JZN-C5IOROH-ZNNCZ4F-QISEFYR-GBFWOJ6-LJHJTYT-IEDABWV-VRJ3XQC"
WINDOWS_DEVICE_NAME = "Windows-PC"

# Folder details
FOLDER_ID = "ocr_inbox"
FOLDER_PATH = "/home/fujinosuke/ocr_inbox"
FOLDER_LABEL = "OCR Inbox"


def check_syncthing_status(api_key: str = "") -> bool:
    """Check if Syncthing is accessible"""
    headers = {"X-API-Key": api_key} if api_key else {}
    try:
        response = requests.get(f"{SYNCTHING_URL}/rest/system/ping", headers=headers, timeout=5)
        return response.status_code == 200
    except:
        return False


def get_config(api_key: str, endpoint: str) -> Dict[str, Any]:
    """Get configuration from Syncthing API"""
    headers = {"X-API-Key": api_key}
    response = requests.get(f"{SYNCTHING_URL}/rest/config/{endpoint}", headers=headers)
    response.raise_for_status()
    return response.json()


def add_device(api_key: str) -> bool:
    """Add the Windows device to Syncthing"""
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    device_config = {
        "deviceID": WINDOWS_DEVICE_ID,
        "name": WINDOWS_DEVICE_NAME,
        "addresses": ["dynamic"],
        "compression": "metadata",
        "introducer": False,
        "paused": False,
        "allowedNetworks": [],
        "autoAcceptFolders": False
    }
    
    try:
        # Check if device already exists
        devices = get_config(api_key, "devices")
        for device in devices:
            if device["deviceID"] == WINDOWS_DEVICE_ID:
                print(f"✓ Device '{WINDOWS_DEVICE_NAME}' already exists")
                return True
        
        # Add new device
        response = requests.post(
            f"{SYNCTHING_URL}/rest/config/devices",
            headers=headers,
            json=device_config
        )
        response.raise_for_status()
        print(f"✓ Successfully added device '{WINDOWS_DEVICE_NAME}'")
        return True
    except Exception as e:
        print(f"✗ Failed to add device: {e}")
        return False


def share_folder(api_key: str) -> bool:
    """Share the ocr_inbox folder with Windows device"""
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        # Get all folders
        folders = get_config(api_key, "folders")
        
        # Find our folder
        folder_exists = False
        for folder in folders:
            if folder["id"] == FOLDER_ID:
                folder_exists = True
                # Check if already shared with Windows device
                shared_with_windows = any(
                    device["deviceID"] == WINDOWS_DEVICE_ID 
                    for device in folder.get("devices", [])
                )
                
                if shared_with_windows:
                    print(f"✓ Folder '{FOLDER_ID}' is already shared with Windows device")
                    return True
                
                # Add Windows device to folder
                folder["devices"].append({
                    "deviceID": WINDOWS_DEVICE_ID,
                    "encryptionPassword": ""
                })
                
                # Update folder configuration
                response = requests.put(
                    f"{SYNCTHING_URL}/rest/config/folders/{FOLDER_ID}",
                    headers=headers,
                    json=folder
                )
                response.raise_for_status()
                print(f"✓ Successfully shared folder '{FOLDER_ID}' with Windows device")
                return True
        
        if not folder_exists:
            # Create new folder
            folder_config = {
                "id": FOLDER_ID,
                "label": FOLDER_LABEL,
                "path": FOLDER_PATH,
                "type": "sendreceive",
                "devices": [
                    {"deviceID": WINDOWS_DEVICE_ID, "encryptionPassword": ""}
                ],
                "rescanIntervalS": 3600,
                "fsWatcherEnabled": True,
                "fsWatcherDelayS": 10,
                "ignorePerms": False,
                "autoNormalize": True
            }
            
            response = requests.post(
                f"{SYNCTHING_URL}/rest/config/folders",
                headers=headers,
                json=folder_config
            )
            response.raise_for_status()
            print(f"✓ Successfully created and shared folder '{FOLDER_ID}'")
            return True
            
    except Exception as e:
        print(f"✗ Failed to share folder: {e}")
        return False


def restart_syncthing(api_key: str):
    """Restart Syncthing to apply changes"""
    headers = {"X-API-Key": api_key}
    try:
        response = requests.post(f"{SYNCTHING_URL}/rest/system/restart", headers=headers)
        response.raise_for_status()
        print("✓ Restarting Syncthing to apply changes...")
    except Exception as e:
        print(f"⚠ Could not restart Syncthing: {e}")
        print("  You may need to restart it manually")


def main():
    print("Syncthing Device Setup")
    print("=" * 50)
    print(f"Target: {SYNCTHING_URL}")
    print(f"Device ID: {WINDOWS_DEVICE_ID}")
    print(f"Folder: {FOLDER_ID} ({FOLDER_PATH})")
    print()
    
    # Check if Syncthing is accessible
    print("Checking Syncthing accessibility...")
    if not check_syncthing_status():
        print(f"✗ Cannot reach Syncthing at {SYNCTHING_URL}")
        print("  Please ensure Syncthing is running and accessible")
        sys.exit(1)
    print("✓ Syncthing is accessible")
    print()
    
    # Get API key
    print("To proceed, you need the Syncthing API key.")
    print()
    print("You can get it by:")
    print(f"1. SSH to {SYNCTHING_HOST} and run:")
    print("   cat ~/.config/syncthing/config.xml | grep -oP '(?<=<apikey>)[^<]+'")
    print()
    print(f"2. Open {SYNCTHING_URL} → Actions → Settings → GUI → API Key")
    print()
    
    api_key = input("Enter API key: ").strip()
    if not api_key:
        print("✗ API key is required!")
        sys.exit(1)
    
    # Verify API key
    if not check_syncthing_status(api_key):
        print("✗ Invalid API key or cannot connect to Syncthing")
        sys.exit(1)
    
    print()
    print("Setting up device and folder...")
    
    # Add device
    if not add_device(api_key):
        sys.exit(1)
    
    # Share folder
    if not share_folder(api_key):
        sys.exit(1)
    
    # Restart Syncthing
    restart_syncthing(api_key)
    
    print()
    print("✓ Setup complete!")
    print()
    print("Next steps on Windows:")
    print("1. Open Syncthing")
    print("2. Accept the connection from the Linux device when prompted")
    print("3. Accept the shared folder 'ocr_inbox' when prompted")
    print("4. Choose a local folder for synchronization")
    print()
    print(f"Monitor status at: {SYNCTHING_URL}")


if __name__ == "__main__":
    main()