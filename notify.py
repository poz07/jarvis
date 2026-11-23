import os, requests
from dotenv import load_dotenv

load_dotenv()

def send_alert(text):
    r = requests.post(
        f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendMessage",
        json={"chat_id": os.getenv("TELEGRAM_CHAT_ID"), "text": text},
        timeout=30,
    )
    r.raise_for_status()

if __name__ == "__main__":
    send_alert("Jarvis online ✅")