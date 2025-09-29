import os.path
import webbrowser
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
ALLOW_LIST_FILE = "allow_list.txt"

def load_allow_list():
    """Loads the allow list from the specified file."""
    allow_list = set()
    if os.path.exists(ALLOW_LIST_FILE):
        with open(ALLOW_LIST_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    allow_list.add(line)
    return allow_list

def extract_email(sender):
    """Extracts the email address from a sender string."""
    match = re.search(r'<(.+?)>', sender)
    if match:
        return match.group(1)
    return sender

def main():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("gmail", "v1", credentials=creds)
        allow_list = load_allow_list()
        print(f"Loaded {len(allow_list)} sender(s) from allow list.")

        results = service.users().messages().list(userId="me", labelIds=['INBOX'], q="newer_than:30d").execute()
        messages = results.get("messages", [])

        if not messages:
            print("No recent messages found.")
        else:
            found_count = 0
            for message in messages:
                msg = service.users().messages().get(userId="me", id=message["id"], format="metadata", metadataHeaders=["List-Unsubscribe", "Subject", "From"]).execute()
                headers = msg["payload"]["headers"]
                list_unsubscribe_header = next((h for h in headers if h['name'] == 'List-Unsubscribe'), None)
                
                if list_unsubscribe_header:
                    sender_header = next(h["value"] for h in headers if h["name"] == "From")
                    sender_email = extract_email(sender_header)
                    sender_domain = sender_email.split('@')[-1]

                    if sender_email in allow_list or sender_domain in allow_list:
                        print(f"\n- Skipping allowed sender: {sender_email}")
                        continue

                    found_count += 1
                    subject = next(h["value"] for h in headers if h["name"] == "Subject")
                    message_id = msg['id']
                    
                    print(f"\n- From: {sender_header}")
                    print(f"  Subject: {subject}")
                    
                    while True:
                        choice = input("  -> Choose: (o)pen, (s)kip, (q)uit? ").lower()
                        if choice == 'o':
                            gmail_url = f"https://mail.google.com/mail/u/0/#inbox/{message_id}"
                            webbrowser.open_new_tab(gmail_url)
                            print(f"    Opening message in browser...")
                            break
                        elif choice == 's':
                            print("    Skipping...")
                            break
                        elif choice == 'q':
                            print("Quitting program.")
                            return
                        else:
                            print("    Invalid choice. Please try again.")
            
            if found_count == 0:
                print("No new emails with a 'List-Unsubscribe' header were found.")

    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()