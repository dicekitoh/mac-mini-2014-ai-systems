# Syncthing Device Addition Guide

## Windows Device Information
- **Device ID**: `JTZ3JZN-C5IOROH-ZNNCZ4F-QISEFYR-GBFWOJ6-LJHJTYT-IEDABWV-VRJ3XQC`
- **Suggested Name**: Windows-PC

## Step-by-Step Instructions

### 1. Access Syncthing Web GUI
Open your web browser and go to: `http://192.168.3.43:8384`

### 2. Add the Windows Device
1. Click on **"Actions"** → **"Show ID"** to see your Linux device ID (save this for Windows side)
2. Click on **"Add Remote Device"** button
3. In the dialog that appears:
   - **Device ID**: `JTZ3JZN-C5IOROH-ZNNCZ4F-QISEFYR-GBFWOJ6-LJHJTYT-IEDABWV-VRJ3XQC`
   - **Device Name**: Windows-PC (or any name you prefer)
   - **Introducer**: Leave unchecked
   - **Auto Accept**: You can check this if you want to automatically accept folders shared from Windows
   - **Addresses**: Leave as "dynamic" (Syncthing will find the device automatically)
4. Click **"Save"**

### 3. Share the ocr_inbox Folder
1. Find the folder in the Syncthing interface (it should be listed if already configured)
   - If not visible, click **"Add Folder"**
   - **Folder ID**: ocr_inbox
   - **Folder Path**: `/home/fujinosuke/ocr_inbox`
2. Click on the folder or use **"Edit"** option
3. Go to the **"Sharing"** tab
4. Check the box next to **"Windows-PC"** (or whatever name you gave the device)
5. Set permissions:
   - Check **"Send & Receive"** for full read/write access
6. Click **"Save"**

### 4. On Windows Side
When you open Syncthing on Windows, you should see:
1. A notification about the new device trying to connect
2. Accept the connection
3. Accept the shared folder when prompted
4. Choose a local folder path for synchronization

### 5. Verify Connection
After both devices have accepted each other:
- The device status should show "Connected" in green
- The folder should show "Up to Date" when synchronized
- Files placed in `/home/fujinosuke/ocr_inbox` on Linux will appear in the Windows folder
- Files placed in the Windows folder will appear in `/home/fujinosuke/ocr_inbox` on Linux

## API Alternative (Advanced)

If you prefer to use the API, you'll need the API key. Here's how to get it and use it:

### Get API Key
```bash
# SSH to the machine and get the API key
ssh fujinosuke@192.168.3.43
cat ~/.config/syncthing/config.xml | grep -A 1 apikey
```

### Add Device via API
```bash
# Example curl command (replace YOUR_API_KEY with actual key)
curl -X POST -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "deviceID": "JTZ3JZN-C5IOROH-ZNNCZ4F-QISEFYR-GBFWOJ6-LJHJTYT-IEDABWV-VRJ3XQC",
    "name": "Windows-PC",
    "addresses": ["dynamic"],
    "compression": "metadata",
    "introducer": false,
    "paused": false,
    "allowedNetworks": [],
    "autoAcceptFolders": false
  }' \
  http://192.168.3.43:8384/rest/config/devices
```

### Share Folder via API
```bash
# Get current folder config
curl -X GET -H "X-API-Key: YOUR_API_KEY" \
  http://192.168.3.43:8384/rest/config/folders/ocr_inbox

# Update with new device (modify the JSON response to add the device)
```

## Troubleshooting

### If devices don't connect:
1. Check firewall settings on both machines
2. Ensure both devices are on the same network or have internet access
3. Default Syncthing ports: 22000 (sync) and 21027 (discovery)

### If folder doesn't sync:
1. Check folder permissions on Linux: `ls -la /home/fujinosuke/ocr_inbox`
2. Ensure the folder exists and fujinosuke user has read/write access
3. Check Syncthing logs in the web GUI under "Actions" → "Logs"

## Security Note
- The device IDs act as authentication
- All data is encrypted during transfer
- Consider setting up GUI authentication if the web interface is exposed