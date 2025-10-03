import flet as ft
import os.path
import webbrowser
import re
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import time

# --- Configuration ---
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.send"]
ALLOW_LIST_FILE = "allow_list.txt"

# --- Backend Functions ---
def authenticate():
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
    return creds

def get_gmail_service():
    creds = authenticate()
    return build("gmail", "v1", credentials=creds)

def find_emails_to_process(service, allow_list):
    results = service.users().messages().list(userId="me", labelIds=['INBOX'], q="").execute()
    messages = results.get("messages", [])
    emails_to_process = []
    if messages:
        for message in messages[:25]:
            msg = service.users().messages().get(userId="me", id=message["id"], format="metadata", metadataHeaders=["List-Unsubscribe", "Subject", "From"]).execute()
            headers = msg["payload"]["headers"]
            if list_unsubscribe_header := next((h for h in headers if h["name"] == "List-Unsubscribe"), None):
                sender_header = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
                if sender_email := extract_email(sender_header):
                    sender_domain = sender_email.split('@')[-1]
                    if sender_email in allow_list or sender_domain in allow_list:
                        continue
                subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
                mailto_link = get_unsubscribe_mailto(list_unsubscribe_header["value"])
                email_data = {"id": msg["id"], "sender": sender_header, "subject": subject, "mailto_link": mailto_link}
                emails_to_process.append(email_data)
    return emails_to_process

def send_unsubscribe_email(service, mailto_link):
    unsubscribe_email_address = mailto_link.split('?')[0]
    message = MIMEText('This is an automatic unsubscribe message.')
    message['to'] = unsubscribe_email_address
    message['subject'] = 'Unsubscribe'
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(userId='me', body={'raw': raw_message}).execute()

def extract_email(sender):
    match = re.search(r'<(.+?)>', sender)
    return match.group(1) if match else sender

def get_unsubscribe_mailto(header_value):
    match = re.search(r'<mailto:(.*?)>', header_value)
    return match.group(1) if match else None

def read_allow_list_file():
    if not os.path.exists(ALLOW_LIST_FILE): return []
    with open(ALLOW_LIST_FILE, "r") as f:
        return sorted([line.strip() for line in f if line.strip()])

def write_allow_list_file(entries):
    with open(ALLOW_LIST_FILE, "w") as f:
        for entry in sorted(set(entries)): f.write(entry + "\n")

# --- Flet UI Application ---
def main(page: ft.Page):
    page.title = "Unsubscriber"
    gmail_service = get_gmail_service()
    
    def update_ui_remove_card(card_to_remove):
        emails_view.controls.remove(card_to_remove)
        page.update()

    def unsubscribe_background_task(button, mailto_link, card):
        try:
            button.text = "Sending..."
            button.disabled = True
            page.update()
            send_unsubscribe_email(gmail_service, mailto_link)
            button.text = "Unsubscribed ✓"
            button.icon = ft.Icons.CHECK
            button.bgcolor = ft.Colors.GREEN_200
        except Exception as e:
            button.text = "Error"
            button.bgcolor = ft.Colors.RED_400
            print(f"Error during unsubscribe: {e}")
        finally:
            button.disabled = True
            page.update()

    def scan_button_clicked(e):
        progress_bar.visible = True
        scan_button.disabled = True
        emails_view.controls.clear()
        page.update()
        try:
            current_allow_list = [control.value for control in allow_list_view.controls]
            emails = find_emails_to_process(gmail_service, current_allow_list)
            
            progress_bar.visible = False
            scan_button.disabled = False
            if not emails:
                emails_view.controls.append(ft.Text("Scan complete. No new emails to process."))
            else:
                for email in emails:
                    card = ft.Card()
                    action_button = ft.ElevatedButton()
                    
                    if email['mailto_link']:
                        action_button.text = "Unsubscribe"
                        action_button.bgcolor = ft.Colors.RED_200
                        action_button.on_click = lambda _, b=action_button, m=email['mailto_link'], c=card: page.run_thread(unsubscribe_background_task, b, m, c)
                    else:
                        action_button.text = "Open to Unsubscribe"
                        action_button.on_click = lambda _, url=f"https://mail.google.com/mail/u/0/#inbox/{email['id']}": webbrowser.open_new_tab(url)
                    
                    card.content = ft.Container(padding=10, content=ft.Row(controls=[
                        ft.Column([
                            ft.Text(f"From: {email['sender']}", weight=ft.FontWeight.BOLD),
                            ft.Text(f"Subject: {email['subject']}"),
                        ], expand=True),
                        ft.ElevatedButton("Skip", data=card, on_click=lambda e: update_ui_remove_card(e.control.data)),
                        action_button,
                    ]))
                    emails_view.controls.append(card)
        except Exception as e:
            progress_bar.visible = False
            scan_button.disabled = False
            emails_view.controls.append(ft.Text(f"An error occurred during scan: {e}"))
        page.update()

    scan_button = ft.ElevatedButton("Scan for Emails", on_click=scan_button_clicked)
    progress_bar = ft.ProgressBar(width=400, visible=False)
    emails_view = ft.Column(spacing=10, scroll=ft.ScrollMode.ADAPTIVE, expand=True)

    def add_to_allow_list_clicked(e):
        new_entry = new_entry_field.value
        if new_entry and not any(isinstance(c, ft.Text) and c.value == new_entry for c in allow_list_view.controls):
            allow_list_view.controls.append(ft.Text(new_entry))
            new_entry_field.value = ""
            save_allow_list_clicked(e)
            page.update()

    def save_allow_list_clicked(e):
        current_entries = [control.value for control in allow_list_view.controls if isinstance(control, ft.Text)]
        write_allow_list_file(current_entries)
        page.snack_bar = ft.SnackBar(content=ft.Text("Allow list saved!"), open=True)
        page.update()

    new_entry_field = ft.TextField(label="Add new email or domain", expand=True)
    add_button = ft.ElevatedButton("Add", on_click=add_to_allow_list_clicked)
    save_button = ft.ElevatedButton("Save List", on_click=save_allow_list_clicked)
    allow_list_view = ft.ListView([ft.Text(entry) for entry in read_allow_list_file()], expand=True, spacing=5)

    page.add(
        ft.Text("📬 UNSUBSCRIBER", size=30, weight=ft.FontWeight.BOLD),
        ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(text="To Process", icon=ft.Icons.MAIL, content=ft.Container(content=ft.Column([
                    scan_button, progress_bar, ft.Divider(), ft.Container(content=emails_view, expand=True)
                ]), padding=10)),
                ft.Tab(text="Allow List", icon=ft.Icons.VERIFIED_USER_OUTLINED, content=ft.Container(content=ft.Column([
                    ft.Row([new_entry_field, add_button]), save_button, ft.Divider(), allow_list_view
                ]), padding=10, expand=True)),
            ], expand=True,
        ),
    )

if __name__ == "__main__":
    ft.app(target=main)