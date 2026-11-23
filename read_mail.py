import imaplib, email, os
from email.header import decode_header, make_header
from dotenv import load_dotenv

load_dotenv()
server = os.getenv("IMAP_SERVER")
user = os.getenv("EMAIL_USER")
password = os.getenv("EMAIL_PASSWORD")

try:
    mail = imaplib.IMAP4_SSL(server, 993)
    mail.login(user, password)
    mail.select("INBOX", readonly=True)  # readonly: nothing gets marked as read
    status, data = mail.search(None, "UNSEEN")
    ids = data[0].split()[-10:]  # last 10 unread
    for num in ids:
        status, msg_data = mail.fetch(num, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)])")
        msg = email.message_from_bytes(msg_data[0][1])
        subject = str(make_header(decode_header(msg["Subject"] or "")))
        sender = str(make_header(decode_header(msg["From"] or "")))
        print(sender, "|", subject)
    mail.logout()
except Exception as e:
    print("Error:", e)