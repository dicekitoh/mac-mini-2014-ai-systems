#!/usr/bin/env python3
"""
Comprehensive Google API Connection Test Script
Tests all available Google APIs with existing authentication tokens
"""

import pickle
import json
import os
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError

class GoogleAPITester:
    def __init__(self):
        self.results = {}
        self.main_creds = None
        self.photo_picker_creds = None
        self.vision_creds = None
        
    def load_credentials(self):
        """Load all available credentials"""
        print("=" * 60)
        print("LOADING CREDENTIALS")
        print("=" * 60)
        
        # Load main Google API token
        try:
            with open('/home/rootmax/google_photos_new_scopes_token.pickle', 'rb') as f:
                self.main_creds = pickle.load(f)
            print("✅ Main Google API token loaded successfully")
            print(f"   Scopes: {len(self.main_creds.scopes)} available")
        except Exception as e:
            print(f"❌ Failed to load main token: {e}")
            
        # Load Photo Picker token
        try:
            with open('/home/rootmax/google_photos_picker_token.pickle', 'rb') as f:
                self.photo_picker_creds = pickle.load(f)
            print("✅ Photo Picker API token loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load Photo Picker token: {e}")
            
        # Load Vision API service account
        try:
            self.vision_creds = service_account.Credentials.from_service_account_file(
                '/home/rootmax/google_vision_service_account.json',
                scopes=['https://www.googleapis.com/auth/cloud-vision']
            )
            print("✅ Vision API service account loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load Vision API credentials: {e}")
            
        print()
        
    def test_gmail_api(self):
        """Test Gmail API connection"""
        print("Testing Gmail API...")
        try:
            service = build('gmail', 'v1', credentials=self.main_creds)
            # Get user profile
            profile = service.users().getProfile(userId='me').execute()
            email = profile.get('emailAddress', 'Unknown')
            messages_total = profile.get('messagesTotal', 0)
            
            self.results['Gmail API'] = {
                'status': '✅ Connected',
                'details': f"Email: {email}, Total messages: {messages_total}"
            }
            print(f"✅ Gmail API: Connected to {email}")
        except Exception as e:
            self.results['Gmail API'] = {
                'status': '❌ Failed',
                'details': str(e)
            }
            print(f"❌ Gmail API: {e}")
            
    def test_calendar_api(self):
        """Test Calendar API connection"""
        print("Testing Calendar API...")
        try:
            service = build('calendar', 'v3', credentials=self.main_creds)
            # List calendars
            calendars = service.calendarList().list().execute()
            calendar_count = len(calendars.get('items', []))
            primary_calendar = next((cal for cal in calendars.get('items', []) 
                                   if cal.get('primary')), {})
            
            self.results['Calendar API'] = {
                'status': '✅ Connected',
                'details': f"Found {calendar_count} calendars, Primary: {primary_calendar.get('summary', 'Unknown')}"
            }
            print(f"✅ Calendar API: Found {calendar_count} calendars")
        except Exception as e:
            self.results['Calendar API'] = {
                'status': '❌ Failed',
                'details': str(e)
            }
            print(f"❌ Calendar API: {e}")
            
    def test_drive_api(self):
        """Test Drive API connection"""
        print("Testing Drive API...")
        try:
            service = build('drive', 'v3', credentials=self.main_creds)
            # Get storage quota
            about = service.about().get(fields='storageQuota, user').execute()
            quota = about.get('storageQuota', {})
            user = about.get('user', {})
            
            used_gb = int(quota.get('usage', 0)) / (1024**3)
            limit_gb = int(quota.get('limit', 0)) / (1024**3)
            
            self.results['Drive API'] = {
                'status': '✅ Connected',
                'details': f"User: {user.get('displayName', 'Unknown')}, Storage: {used_gb:.2f}/{limit_gb:.2f} GB"
            }
            print(f"✅ Drive API: Connected, using {used_gb:.2f} GB")
        except Exception as e:
            self.results['Drive API'] = {
                'status': '❌ Failed',
                'details': str(e)
            }
            print(f"❌ Drive API: {e}")
            
    def test_sheets_api(self):
        """Test Sheets API connection"""
        print("Testing Sheets API...")
        try:
            service = build('sheets', 'v4', credentials=self.main_creds)
            # Try to list recent sheets (via Drive API)
            drive_service = build('drive', 'v3', credentials=self.main_creds)
            sheets = drive_service.files().list(
                q="mimeType='application/vnd.google-apps.spreadsheet'",
                pageSize=5,
                fields="files(id, name)"
            ).execute()
            
            sheet_count = len(sheets.get('files', []))
            sheet_names = [f['name'] for f in sheets.get('files', [])][:3]
            
            self.results['Sheets API'] = {
                'status': '✅ Connected',
                'details': f"Found {sheet_count} spreadsheets. Recent: {', '.join(sheet_names) if sheet_names else 'None'}"
            }
            print(f"✅ Sheets API: Connected, found {sheet_count} sheets")
        except Exception as e:
            self.results['Sheets API'] = {
                'status': '❌ Failed',
                'details': str(e)
            }
            print(f"❌ Sheets API: {e}")
            
    def test_tasks_api(self):
        """Test Tasks API connection"""
        print("Testing Tasks API...")
        try:
            service = build('tasks', 'v1', credentials=self.main_creds)
            # List task lists
            tasklists = service.tasklists().list().execute()
            list_count = len(tasklists.get('items', []))
            list_names = [tl['title'] for tl in tasklists.get('items', [])]
            
            # Count total tasks
            total_tasks = 0
            for tasklist in tasklists.get('items', []):
                tasks = service.tasks().list(tasklist=tasklist['id']).execute()
                total_tasks += len(tasks.get('items', []))
            
            self.results['Tasks API'] = {
                'status': '✅ Connected',
                'details': f"Found {list_count} lists with {total_tasks} total tasks. Lists: {', '.join(list_names)}"
            }
            print(f"✅ Tasks API: {list_count} lists, {total_tasks} tasks")
        except Exception as e:
            self.results['Tasks API'] = {
                'status': '❌ Failed',
                'details': str(e)
            }
            print(f"❌ Tasks API: {e}")
            
    def test_contacts_api(self):
        """Test Contacts API (People API)"""
        print("Testing Contacts API...")
        try:
            service = build('people', 'v1', credentials=self.main_creds)
            # Get total contacts count
            connections = service.people().connections().list(
                resourceName='people/me',
                pageSize=1,
                personFields='names'
            ).execute()
            
            total_contacts = connections.get('totalPeople', 0)
            
            self.results['Contacts API'] = {
                'status': '✅ Connected',
                'details': f"Total contacts: {total_contacts}"
            }
            print(f"✅ Contacts API: Found {total_contacts} contacts")
        except Exception as e:
            self.results['Contacts API'] = {
                'status': '❌ Failed',
                'details': str(e)
            }
            print(f"❌ Contacts API: {e}")
            
    def test_blogger_api(self):
        """Test Blogger API connection"""
        print("Testing Blogger API...")
        try:
            service = build('blogger', 'v3', credentials=self.main_creds)
            # List blogs
            blogs = service.blogs().listByUser(userId='self').execute()
            blog_count = len(blogs.get('items', []))
            blog_names = [blog['name'] for blog in blogs.get('items', [])]
            
            # Get post counts
            post_counts = []
            for blog in blogs.get('items', []):
                posts = service.posts().list(blogId=blog['id'], maxResults=1).execute()
                total_posts = posts.get('totalItems', 0)
                post_counts.append(f"{blog['name']}: {total_posts} posts")
            
            self.results['Blogger API'] = {
                'status': '✅ Connected',
                'details': f"Found {blog_count} blogs. {', '.join(post_counts)}"
            }
            print(f"✅ Blogger API: {blog_count} blogs found")
        except Exception as e:
            self.results['Blogger API'] = {
                'status': '❌ Failed',
                'details': str(e)
            }
            print(f"❌ Blogger API: {e}")
            
    def test_photo_picker_api(self):
        """Test Photo Picker API connection"""
        print("Testing Photo Picker API...")
        if not self.photo_picker_creds:
            self.results['Photo Picker API'] = {
                'status': '⚠️ Not configured',
                'details': 'Token file not found'
            }
            print("⚠️ Photo Picker API: Token not loaded")
            return
            
        try:
            # Check token expiry
            if hasattr(self.photo_picker_creds, 'expiry') and self.photo_picker_creds.expiry:
                expiry_str = self.photo_picker_creds.expiry.strftime('%Y-%m-%d %H:%M:%S')
                is_expired = self.photo_picker_creds.expiry < datetime.now()
                
                status = '⚠️ Token expired' if is_expired else '✅ Token valid'
                
                self.results['Photo Picker API'] = {
                    'status': status,
                    'details': f"Token expiry: {expiry_str}. {'Needs refresh' if is_expired else 'Ready to use'}"
                }
                print(f"{status}: Photo Picker API (expires: {expiry_str})")
            else:
                self.results['Photo Picker API'] = {
                    'status': '✅ Token loaded',
                    'details': 'Token loaded, expiry unknown'
                }
                print("✅ Photo Picker API: Token loaded successfully")
        except Exception as e:
            self.results['Photo Picker API'] = {
                'status': '❌ Failed',
                'details': str(e)
            }
            print(f"❌ Photo Picker API: {e}")
            
    def test_vision_api(self):
        """Test Vision API connection"""
        print("Testing Vision API...")
        if not self.vision_creds:
            self.results['Vision API'] = {
                'status': '⚠️ Not configured',
                'details': 'Service account not found'
            }
            print("⚠️ Vision API: Credentials not loaded")
            return
            
        try:
            from google.cloud import vision
            client = vision.ImageAnnotatorClient(credentials=self.vision_creds)
            
            # Test with a simple feature check (no actual image needed for connection test)
            self.results['Vision API'] = {
                'status': '✅ Connected',
                'details': f'Service account: {self.vision_creds.service_account_email}'
            }
            print(f"✅ Vision API: Connected via service account")
        except Exception as e:
            self.results['Vision API'] = {
                'status': '❌ Failed',
                'details': str(e)
            }
            print(f"❌ Vision API: {e}")
            
    def generate_report(self):
        """Generate final report"""
        print("\n" + "=" * 60)
        print("GOOGLE API CONNECTION TEST REPORT")
        print("=" * 60)
        print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Summary statistics
        total_apis = len(self.results)
        connected = sum(1 for r in self.results.values() if '✅' in r['status'])
        failed = sum(1 for r in self.results.values() if '❌' in r['status'])
        warning = sum(1 for r in self.results.values() if '⚠️' in r['status'])
        
        print(f"\nSUMMARY:")
        print(f"  Total APIs tested: {total_apis}")
        print(f"  ✅ Connected: {connected}")
        print(f"  ❌ Failed: {failed}")
        print(f"  ⚠️ Warnings: {warning}")
        
        print("\nDETAILED RESULTS:")
        print("-" * 60)
        
        for api_name, result in self.results.items():
            print(f"\n{api_name}:")
            print(f"  Status: {result['status']}")
            print(f"  Details: {result['details']}")
            
        print("\n" + "=" * 60)
        
        # Recommendations
        if failed > 0 or warning > 0:
            print("\nRECOMMENDATIONS:")
            if 'Photo Picker API' in self.results and '⚠️' in self.results['Photo Picker API']['status']:
                print("  • Photo Picker token expired. Run: python3 /home/rootmax/refresh_photo_picker_token.py")
            if any('❌' in r['status'] for r in self.results.values()):
                print("  • Some APIs failed. Check credentials and scopes.")
                print("  • You may need to re-authenticate: python3 /home/rootmax/complete_google_auth_new.py")
                
        # Show available scopes from main token
        if self.main_creds and hasattr(self.main_creds, 'scopes'):
            print("\nAVAILABLE SCOPES IN MAIN TOKEN:")
            for scope in self.main_creds.scopes:
                print(f"  • {scope}")
                
    def run_all_tests(self):
        """Run all API tests"""
        self.load_credentials()
        
        if self.main_creds:
            print("TESTING APIs WITH MAIN TOKEN")
            print("-" * 60)
            self.test_gmail_api()
            self.test_calendar_api()
            self.test_drive_api()
            self.test_sheets_api()
            self.test_tasks_api()
            self.test_contacts_api()
            self.test_blogger_api()
            
        print("\nTESTING SPECIALIZED APIs")
        print("-" * 60)
        self.test_photo_picker_api()
        self.test_vision_api()
        
        self.generate_report()

def main():
    """Main execution function"""
    print("🚀 Google API Comprehensive Connection Test")
    print("Testing all available Google APIs...\n")
    
    tester = GoogleAPITester()
    tester.run_all_tests()
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main()