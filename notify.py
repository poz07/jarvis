import os, requests
from dotenv import load_dotenv

load_dotenv()

def send_alert(text):
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendMessage",
            json={"chat_id": os.getenv("TELEGRAM_CHAT_ID"), "text": text},
            timeout=30,
        )
    except requests.RequestException:
        raise RuntimeError("Telegram request failed (network error)") from None
    if not r.ok:
        raise RuntimeError(f"Telegram returned HTTP {r.status_code}")

if __name__ == "__main__":
    send_alert("Jarvis online ✅")