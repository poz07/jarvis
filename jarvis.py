import imaplib, email, os, json, requests
from email.header import decode_header, make_header
from dotenv import load_dotenv
from notify import send_alert

load_dotenv()
MODEL = "llama3.2:3b"
STATE_FILE = "processed.json"
ALERT_LABELS = {"URGENT", "DEADLINE"}

def load_processed():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_processed(seen):
    with open(STATE_FILE, "w") as f:
        json.dump(seen[-500:], f)

def clean(h):
    return str(make_header(decode_header(h or "")))

def decode_part(part):
    payload = part.get_payload(decode=True) or b""
    try:
        return payload.decode(part.get_content_charset() or "utf-8", errors="replace")
    except LookupError:
        return payload.decode("utf-8", errors="replace")

def get_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and not part.get_filename():
                return decode_part(part)
        return ""
    return decode_part(msg)

def rule_based(subject):
    if "Μήνυμα εκπαιδευτή" in subject:
        return {"label": "URGENT", "reason": "Message from a course instructor"}
    if "CVE-" in subject:
        return {"label": "IGNORE", "reason": "IT admin security bulletin"}
    return None

def classify(sender, subject, body):
    prompt = f"""You sort emails for a university student. The emails are often in Greek.
Pick exactly one label:
URGENT: needs attention today or tomorrow (class or exam changes, messages from a course instructor, strikes or closures affecting classes, security alerts about the student's own account)
DEADLINE: has a future due date or registration deadline
INFO: useful but not time-sensitive (announcements, seminars, events)
IGNORE: ads, surveys, mass mailings with no action needed

Reply with JSON only: {{"label": "...", "reason": "one short sentence in English"}}

From: {sender}
Subject: {subject}
Body: {body[:1500]}"""
    r = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": MODEL, "prompt": prompt, "stream": False,
              "format": "json", "options": {"temperature": 0}},
        timeout=180,
    )
    r.raise_for_status()
    return json.loads(r.json()["response"])

seen = load_processed()
mail = imaplib.IMAP4_SSL(os.getenv("IMAP_SERVER"), 993)
mail.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASSWORD"))
mail.select("INBOX", readonly=True)
status, data = mail.search(None, "UNSEEN")
ids = data[0].split()[-10:]

for num in ids:
    try:
        status, msg_data = mail.fetch(num, "(BODY.PEEK[])")
        msg = email.message_from_bytes(msg_data[0][1])
        key = (msg["Message-ID"] or "").strip() or f"{msg['From']}|{msg['Subject']}|{msg['Date']}"
        if key in seen:
            continue
        sender, subject = clean(msg["From"]), clean(msg["Subject"])
        result = rule_based(subject) or classify(sender, subject, get_body(msg))
        label = result.get("label")
        print(f"[{label}] {subject[:70]}\n    {result.get('reason')}\n")
        if label in ALERT_LABELS:
            send_alert(f"{label}: {subject[:100]}\n{result.get('reason')}")
        seen.append(key)
        save_processed(seen)
    except Exception as e:
        print("Error on one email:", e)

mail.logout()