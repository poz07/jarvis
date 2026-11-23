import os, requests
from dotenv import load_dotenv

load_dotenv()
url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/getUpdates"
r = requests.get(url, timeout=30)
data = r.json()
print("HTTP status:", r.status_code)
print("ok:", data.get("ok"), "| description:", data.get("description"))
print("messages found:", len(data.get("result", [])))
for u in data.get("result", []):
    chat = u.get("message", {}).get("chat", {})
    print("chat id:", chat.get("id"), "| name:", chat.get("first_name"))