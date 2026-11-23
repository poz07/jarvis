import requests, json

def classify(email_text):
    prompt = f"""You sort university emails for a student. Pick exactly one label:
URGENT: needs attention today or tomorrow (schedule or exam changes, cancelled classes, security alerts)
DEADLINE: has a due date in the future (assignments, registrations, forms)
INFO: useful but not time-sensitive (announcements, newsletters)
IGNORE: spam, ads, mass mailings with no action needed

Examples:
"Lecture cancelled tomorrow" -> URGENT
"Submit your project by 5 December" -> DEADLINE
"New library opening hours" -> INFO
"50% off pizza for students" -> IGNORE

Reply with JSON only: {{"label": "...", "reason": "one short sentence"}}

Email:
{email_text}"""
    r = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama3.2:3b", "prompt": prompt, "stream": False,
              "format": "json", "options": {"temperature": 0}},
        timeout=120,
    )
    r.raise_for_status()
    return json.loads(r.json()["response"])

tests = [
    "Subject: Exam moved to Monday 9am\nFrom: secretary@uth.gr\nBody: The databases exam has been moved.",
    "Subject: Assignment 3 due 5 December\nFrom: prof@uth.gr\nBody: Please upload on eClass.",
    "Subject: Newsletter November\nFrom: info@uth.gr\nBody: Events this month.",
    "Subject: WIN a free phone!!!\nFrom: promo@randomsite.com\nBody: Click here.",
]

for t in tests:
    print(t.split("\n")[0], "->", classify(t))