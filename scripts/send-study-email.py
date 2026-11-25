import json, os, random, smtplib, html
from datetime import datetime, timezone
from email.message import EmailMessage

with open("data/day-01.json", encoding="utf-8") as f:
    bank = json.load(f)
if len(bank) < 10:
    raise SystemExit("Question bank must contain at least 10 questions")

questions = random.SystemRandom().sample(bank, 10)
now = datetime.now(timezone.utc).astimezone()
site = "https://narsing-s.github.io/station-master-success-2026/"
parts = [
    "<h2>Station Master Success 2026</h2>",
    f"<p>Your fresh bilingual practice set · {html.escape(now.strftime('%d %b %Y, %I:%M %p %Z'))}</p>",
    "<p>Try these questions before checking the answer key. Each correct answer is worth 1 mark. This email is for practice; it does not apply the exam's negative marking.</p>"
]
plain = ["Station Master Success 2026", "Fresh bilingual practice set", ""]
for i, q in enumerate(questions, 1):
    parts.append(f"<h3>Q{i}. {html.escape(q['q'])}</h3><ol type='A'>")
    plain.append(f"Q{i}. {q['q']}")
    for option in q["options"]:
        parts.append(f"<li>{html.escape(option)}</li>")
        plain.append(f"  - {option}")
    parts.append("</ol>")
    plain.append("")
parts.append("<hr><h2>Answer key and explanations</h2>")
plain.extend(["", "ANSWER KEY & EXPLANATIONS"])
for i, q in enumerate(questions, 1):
    indexes = q.get("answers", [q["answer"]])
    letters = ", ".join(chr(65 + n) for n in indexes)
    answer_text = ", ".join(q["options"][n] for n in indexes)
    why = q.get("why", "")
    parts.append(f"<p><b>Q{i}: {letters} — {html.escape(answer_text)}</b><br>{html.escape(why)}</p>")
    plain.append(f"Q{i}: {letters} — {answer_text}. {why}")
parts.append(f"<p><a href='{site}'>Open the study website and take a new randomized quiz</a></p>")
plain.extend(["", f"Open the study website: {site}", "Study in English + Telugu."])
msg = EmailMessage()
msg["Subject"] = f"Station Master 2026 — 10 fresh questions — {now.strftime('%d %b %Y %H:%M %Z')}"
msg["From"] = os.environ["STUDY_GMAIL_USER"]
msg["To"] = os.environ.get("STUDY_TO_EMAIL", os.environ["STUDY_GMAIL_USER"])
msg.set_content("\\n".join(plain))
msg.add_alternative("\\n".join(parts), subtype="html")
with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
    server.login(os.environ["STUDY_GMAIL_USER"], os.environ["STUDY_GMAIL_APP_PASSWORD"])
    server.send_message(msg)
print(f"Sent 10 questions to {msg['To']}")
