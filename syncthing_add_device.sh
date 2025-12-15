#!/bin/bash

# Syncthing device addition script
# Usage: ./syncthing_add_device.sh

SYNCTHING_HOST="192.168.3.43"
SYNCTHING_PORT="8384"
DEVICE_ID="JTZ3JZN-C5IOROH-ZNNCZ4F-QISEFYR-GBFWOJ6-LJHJTYT-IEDABWV-VRJ3XQC"
DEVICE_NAME="Windows-PC"
FOLDER_ID="ocr_inbox"
FOLDER_PATH="/home/fujinosuke/ocr_inbox"

echo "Syncthing Device Addition Script"
echo "================================"
echo ""
echo "This script will help you add the Windows device to Syncthing"
echo ""

# Check if we can reach Syncthing
echo "Checking Syncthing availability..."
if curl -s -f "http://${SYNCTHING_HOST}:${SYNCTHING_PORT}/rest/system/ping" > /dev/null 2>&1; then
    echo "✓ Syncthing is reachable at http://${SYNCTHING_HOST}:${SYNCTHING_PORT}"
else
    echo "✗ Cannot reach Syncthing at http://${SYNCTHING_HOST}:${SYNCTHING_PORT}"
    echo "  Please ensure Syncthing is running and accessible"
    exit 1
fi

echo ""
echo "To complete the setup, you'll need the API key from Syncthing."
echo ""
echo "Option 1: Get it via SSH"
echo "-------------------------"
echo "ssh fujinosuke@${SYNCTHING_HOST}"
echo "cat ~/.config/syncthing/config.xml | grep -A 1 apikey | grep -v '<gui' | sed 's/.*<apikey>//;s/<\/apikey>//' | tr -d ' '"
echo ""
echo "Option 2: Get it from Web GUI"
echo "------------------------------"
echo "1. Open http://${SYNCTHING_HOST}:${SYNCTHING_PORT} in your browser"
echo "2. Go to Actions → Settings → GUI"
echo "3. Copy the API Key"
echo ""
read -p "Enter the API key: " API_KEY

if [ -z "$API_KEY" ]; then
    echo "API key is required!"
    exit 1
fi

echo ""
echo "Adding device..."

# Add the device
RESPONSE=$(curl -s -X POST -H "X-API-Key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"deviceID\": \"${DEVICE_ID}\",
    \"name\": \"${DEVICE_NAME}\",
    \"addresses\": [\"dynamic\"],
    \"compression\": \"metadata\",
    \"introducer\": false,
    \"paused\": false,
    \"allowedNetworks\": [],
    \"autoAcceptFolders\": false
  }" \
  "http://${SYNCTHING_HOST}:${SYNCTHING_PORT}/rest/config/devices")

if [ $? -eq 0 ]; then
    echo "✓ Device added successfully"
else
    echo "✗ Failed to add device"
    echo "Response: $RESPONSE"
fi

echo ""
echo "Configuring folder sharing..."

# Get current folder configuration
FOLDER_CONFIG=$(curl -s -X GET -H "X-API-Key: ${API_KEY}" \
  "http://${SYNCTHING_HOST}:${SYNCTHING_PORT}/rest/config/folders" | \
  jq ".[] | select(.id == \"${FOLDER_ID}\")")

if [ -z "$FOLDER_CONFIG" ]; then
    echo "Folder ${FOLDER_ID} not found. Creating it..."
    
    # Create new folder
    curl -s -X POST -H "X-API-Key: ${API_KEY}" \
      -H "Content-Type: application/json" \
      -d "{
        \"id\": \"${FOLDER_ID}\",
        \"label\": \"OCR Inbox\",
        \"path\": \"${FOLDER_PATH}\",
        \"type\": \"sendreceive\",
        \"devices\": [
          {\"deviceID\": \"${DEVICE_ID}\", \"encryptionPassword\": \"\"}
        ],
        \"rescanIntervalS\": 3600,
        \"fsWatcherEnabled\": true,
        \"fsWatcherDelayS\": 10,
        \"ignorePerms\": false,
        \"autoNormalize\": true
      }" \
      "http://${SYNCTHING_HOST}:${SYNCTHING_PORT}/rest/config/folders"
else
    echo "Updating existing folder configuration..."
    
    # Update folder to include the new device
    UPDATED_CONFIG=$(echo "$FOLDER_CONFIG" | jq ".devices += [{\"deviceID\": \"${DEVICE_ID}\", \"encryptionPassword\": \"\"}]")
    
    curl -s -X PUT -H "X-API-Key: ${API_KEY}" \
      -H "Content-Type: application/json" \
      -d "$UPDATED_CONFIG" \
      "http://${SYNCTHING_HOST}:${SYNCTHING_PORT}/rest/config/folders/${FOLDER_ID}"
fi

echo ""
echo "Restarting Syncthing to apply changes..."
curl -s -X POST -H "X-API-Key: ${API_KEY}" \
  "http://${SYNCTHING_HOST}:${SYNCTHING_PORT}/rest/system/restart"

echo ""
echo "✓ Configuration complete!"
echo ""
echo "Next steps:"
echo "1. On your Windows machine, accept the connection from the Linux device"
echo "2. Accept the shared folder '${FOLDER_ID}'"
echo "3. Files will sync between ${FOLDER_PATH} (Linux) and your chosen Windows folder"
echo ""
echo "You can monitor the status at: http://${SYNCTHING_HOST}:${SYNCTHING_PORT}"