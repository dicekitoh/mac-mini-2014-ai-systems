#\!/usr/bin/env python3
import requests
import json
from datetime import datetime

# N8n API configuration
N8N_URL = 'http://localhost:5678'
API_KEY = '******b0p8'
HEADERS = {
    'X-N8N-API-KEY': API_KEY,
    'Content-Type': 'application/json'
}

# Create Gmail test workflow
workflow_data = {
    "name": f"Gmail Test Workflow - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    "active": False,
    "nodes": [
        {
            "parameters": {},
            "id": "manual_trigger",
            "name": "Manual Trigger",
            "type": "n8n-nodes-base.manualTrigger",
            "typeVersion": 1,
            "position": [250, 300]
        },
        {
            "parameters": {
                "resource": "message",
                "operation": "send",
                "subject": "N8n Gmail Test - {{\}}",
                "toList": ["itoh@thinksblog.com"],
                "message": "This is a test email sent from N8n workflow at {{\}}\n\nWorkflow executed successfully\!",
                "options": {}
            },
            "id": "gmail_send",
            "name": "Gmail",
            "type": "n8n-nodes-base.gmail",
            "typeVersion": 2,
            "position": [450, 300],
            "credentials": {
                "gmailOAuth2": {
                    "id": "gmail_oauth2_creds",
                    "name": "Gmail OAuth2"
                }
            }
        }
    ],
    "connections": {
        "Manual Trigger": {
            "main": [
                [
                    {
                        "node": "Gmail",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        }
    },
    "settings": {},
    "staticData": None,
    "pinData": {}
}

try:
    # Create the workflow
    response = requests.post(f'{N8N_URL}/api/v1/workflows', headers=HEADERS, json=workflow_data)
    
    if response.status_code in [200, 201]:
        workflow = response.json()
        print(f"✅ Workflow created successfully\!")
        print(f"   Workflow ID: {workflow.get('id')}")
        print(f"   Workflow Name: {workflow.get('name')}")
        print(f"\n📋 Workflow Details:")
        print(json.dumps(workflow, indent=2))
        
        # Save workflow ID for future use
        with open('gmail_workflow_id.txt', 'w') as f:
            f.write(str(workflow.get('id')))
        
    else:
        print(f"❌ Failed to create workflow")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")

# Check for existing credentials
print("\n🔍 Checking for existing Gmail credentials...")
try:
    # Note: The credentials endpoint might require different permissions
    # For now, we'll note that credentials need to be set up manually
    print("\n⚠️  Note: Gmail OAuth2 credentials need to be configured in N8n UI")
    print("   1. Open N8n UI: http://localhost:5678")
    print("   2. Go to Credentials")
    print("   3. Add new Gmail OAuth2 credentials")
    print("   4. Follow Google OAuth setup process")
except Exception as e:
    print(f"Could not check credentials: {str(e)}")
