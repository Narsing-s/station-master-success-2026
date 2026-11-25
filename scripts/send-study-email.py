import hashlib
import html
import json
import os
import random
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

QUESTION_COUNT = 100
STATE_FILE = Path(".email-state/sent-question-ids.json")
SITE = "https://narsing-s.github.io/station-master-success-2026/"


def make_question(subject, question, options, answer, why):
    key = hashlib.sha256(question.encode("utf-8")).hexdigest()[:20]
    return {
        "id": key,
        "subject": subject,
        "q": question,
        "options": [str(x) for x in options],
        "answer": answer,
        "why": why,
    }


def generated_questions():
    bank = []

    # Arithmetic: broad, deterministic practice pool with exact answers.
    for a in range(12, 52):
        for b in range(13, 43):
            value = a + b
            opts = [value, value + 2, value - 3, value + 5]
            bank.append(make_question(
                "Mathematics",
                f"Calculate: {a} + {b} = ? / లెక్కించండి: {a} + {b} = ?",
                opts, 0,
                f"{a} + {b} = {value}. / {a} + {b} = {value}."
            ))

            if a > b:
                value = a - b
                opts = [value, value + 2, value + 4, max(0, value - 3)]
                bank.append(make_question(
                    "Mathematics",
                    f"Calculate: {a} − {b} = ? / లెక్కించండి: {a} − {b} = ?",
                    opts, 0,
                    f"{a} − {b} = {value}. / {a} − {b} = {value}."
                ))

    for a in range(3, 22):
        for b in range(3, 22):
            value = a * b
            opts = [value, value + a, value - b, value + 10]
            bank.append(make_question(
                "Mathematics",
                f"Calculate: {a} × {b} = ? / గుణించండి: {a} × {b} = ?",
                opts, 0,
                f"{a} × {b} = {value}. / {a} × {b} = {value}."
            ))

    for divisor in range(2, 16):
        for quotient in range(6, 36):
            dividend = divisor * quotient
            opts = [quotient, quotient + 2, quotient - 1, quotient + 5]
            bank.append(make_question(
                "Mathematics",
                f"Calculate: {dividend} ÷ {divisor} = ? / భాగించండి: {dividend} ÷ {divisor} = ?",
                opts, 0,
                f"{dividend} ÷ {divisor} = {quotient}, because {divisor} × {quotient} = {dividend}. / {dividend} ÷ {divisor} = {quotient}."
            ))

    for base in range(100, 1100, 25):
        for pct in (5, 10, 15, 20, 25, 30, 40, 50, 60, 75):
            value = base * pct // 100
            opts = [value, value + 5, max(0, value - 5), value + 10]
            bank.append(make_question(
                "Mathematics",
                f"What is {pct}% of {base}? / {base} లో {pct}% ఎంత?",
                opts, 0,
                f"{pct}% of {base} = ({pct}/100) × {base} = {value}. / {base} లో {pct}% = {value}."
            ))

    # Number-series reasoning.
    for start in range(2, 42):
        for step in range(2, 13):
            value = start + 4 * step
            opts = [value, value + step, value - 1, value + 2 * step]
            bank.append(make_question(
                "Reasoning",
                f"Find the next number: {start}, {start + step}, {start + 2*step}, {start + 3*step}, ? / తదుపరి సంఖ్యను కనుగొనండి.",
                opts, 0,
                f"The sequence increases by {step} each time, so the next number is {value}. / ప్రతి సారి {step} చొప్పున పెరుగుతుంది; తదుపరి సంఖ్య {value}."
            ))

    for start in range(2, 22):
        for multiplier in (2, 3):
            values = [start, start * multiplier, start * multiplier**2, start * multiplier**3]
            answer = start * multiplier**4
            opts = [answer, answer + start, answer - multiplier, answer * 2]
            bank.append(make_question(
                "Reasoning",
                f"Find the next number: {values[0]}, {values[1]}, {values[2]}, {values[3]}, ? / తదుపరి సంఖ్య ఏది?",
                opts, 0,
                f"Each term is multiplied by {multiplier}; {values[3]} × {multiplier} = {answer}. / ప్రతి పదాన్ని {multiplier} తో గుణిస్తారు; సమాధానం {answer}."
            ))

    # Stable general-awareness and science questions, bilingual stems.
    facts = [
        ("Basic Science", "What is the SI unit of electric current? / విద్యుత్ ప్రవాహం SI ప్రమాణం ఏది?", ["Ampere", "Volt", "Ohm", "Watt"], 0, "Electric current is measured in amperes (A). / విద్యుత్ ప్రవాహాన్ని ఆంపియర్‌లో కొలుస్తారు."),
        ("Basic Science", "Which gas do plants absorb during photosynthesis? / కిరణజన్య సంయోగక్రియలో మొక్కలు ఏ వాయువును గ్రహిస్తాయి?", ["Carbon dioxide", "Oxygen", "Nitrogen", "Hydrogen"], 0, "Plants absorb carbon dioxide during photosynthesis. / కిరణజన్య సంయోగక్రియలో మొక్కలు కార్బన్ డయాక్సైడ్‌ను గ్రహిస్తాయి."),
        ("Basic Science", "Which planet is known as the Red Planet? / ఎర్ర గ్రహం అని ఏ గ్రహాన్ని పిలుస్తారు?", ["Mars", "Venus", "Jupiter", "Mercury"], 0, "Iron oxide on its surface gives Mars its reddish appearance. / అంగారక గ్రహ ఉపరితలంలోని ఐరన్ ఆక్సైడ్ దానికి ఎరుపు రంగును ఇస్తుంది."),
        ("Basic Science", "What is the chemical formula of water? / నీటి రసాయన సూత్రం ఏమిటి?", ["H₂O", "CO₂", "NaCl", "O₂"], 0, "A water molecule contains two hydrogen atoms and one oxygen atom. / నీటి అణువులో రెండు హైడ్రోజన్, ఒక ఆక్సిజన్ పరమాణువులు ఉంటాయి."),
        ("Basic Science", "Which part of the human body pumps blood? / మానవ శరీరంలో రక్తాన్ని పంప్ చేసే అవయవం ఏది?", ["Heart", "Lungs", "Kidney", "Liver"], 0, "The heart pumps blood through the circulatory system. / గుండె రక్త ప్రసరణ వ్యవస్థలో రక్తాన్ని పంపుతుంది."),
        ("Basic Science", "At sea level, water boils at approximately what temperature? / సముద్ర మట్టంలో నీరు సుమారు ఏ ఉష్ణోగ్రత వద్ద మరిగుతుంది?", ["100°C", "0°C", "50°C", "150°C"], 0, "At standard atmospheric pressure, water boils at 100°C. / సాధారణ వాతావరణ పీడనంలో నీరు 100°C వద్ద మరిగుతుంది."),
        ("Basic Science", "Which vitamin is produced in the skin with sunlight exposure? / సూర్యకాంతి వల్ల చర్మంలో ఉత్పత్తి అయ్యే విటమిన్ ఏది?", ["Vitamin D", "Vitamin C", "Vitamin B12", "Vitamin K"], 0, "Sunlight enables the skin to synthesize vitamin D. / సూర్యకాంతి చర్మంలో విటమిన్ D తయారీకి సహాయపడుతుంది."),
        ("Basic Science", "What is the SI unit of frequency? / ఆవర్తనానికి SI ప్రమాణం ఏది?", ["Hertz", "Newton", "Joule", "Pascal"], 0, "Frequency is measured in hertz (Hz). / ఆవర్తనాన్ని హెర్ట్జ్‌లో కొలుస్తారు."),
        ("Basic Science", "Which organ is primarily responsible for filtering blood and producing urine? / రక్తాన్ని వడపోసి మూత్రాన్ని తయారు చేసే ప్రధాన అవయవం ఏది?", ["Kidney", "Stomach", "Lungs", "Pancreas"], 0, "The kidneys filter blood and produce urine. / మూత్రపిండాలు రక్తాన్ని వడపోసి మూత్రాన్ని తయారు చేస్తాయి."),
        ("Basic Science", "Which force keeps planets in orbit around the Sun? / గ్రహాలను సూర్యుని చుట్టూ కక్ష్యలో ఉంచే బలం ఏది?", ["Gravity", "Friction", "Magnetism", "Buoyancy"], 0, "The Sun's gravitational attraction keeps planets in orbit. / సూర్యుని గురుత్వాకర్షణ గ్రహాలను కక్ష్యలో ఉంచుతుంది."),
        ("General Awareness", "What is the capital of India? / భారతదేశ రాజధాని ఏది?", ["New Delhi", "Mumbai", "Kolkata", "Chennai"], 0, "New Delhi is the capital of India. / న్యూఢిల్లీ భారతదేశ రాజధాని."),
        ("General Awareness", "Which is the national animal of India? / భారతదేశ జాతీయ జంతువు ఏది?", ["Bengal tiger", "Asiatic lion", "Elephant", "Leopard"], 0, "The Bengal tiger is India's national animal. / బెంగాల్ పులి భారతదేశ జాతీయ జంతువు."),
        ("General Awareness", "Which is the national aquatic animal of India? / భారతదేశ జాతీయ జలచర జంతువు ఏది?", ["Ganges river dolphin", "Blue whale", "Sea turtle", "Crocodile"], 0, "The Ganges river dolphin is India's national aquatic animal. / గంగా నది డాల్ఫిన్ భారతదేశ జాతీయ జలచర జంతువు."),
        ("General Awareness", "The Constitution of India came into effect on which date? / భారత రాజ్యాంగం ఎప్పుడు అమల్లోకి వచ్చింది?", ["26 January 1950", "15 August 1947", "26 November 1949", "2 October 1950"], 0, "The Constitution came into effect on 26 January 1950. / భారత రాజ్యాంగం 26 జనవరి 1950న అమల్లోకి వచ్చింది."),
        ("General Awareness", "Who was the chairman of the Drafting Committee of the Indian Constitution? / భారత రాజ్యాంగ ముసాయిదా కమిటీ అధ్యక్షుడు ఎవరు?", ["B. R. Ambedkar", "Rajendra Prasad", "Jawaharlal Nehru", "Sardar Patel"], 0, "Dr. B. R. Ambedkar chaired the Drafting Committee. / డా. బి.ఆర్. అంబేద్కర్ ముసాయిదా కమిటీకి అధ్యక్షత వహించారు."),
        ("General Awareness", "Which is the largest Indian state by area? / విస్తీర్ణం ప్రకారం భారతదేశంలో అతిపెద్ద రాష్ట్రం ఏది?", ["Rajasthan", "Madhya Pradesh", "Maharashtra", "Uttar Pradesh"], 0, "Rajasthan is the largest state by area. / విస్తీర్ణం ప్రకారం రాజస్థాన్ అతిపెద్ద రాష్ట్రం."),
        ("General Awareness", "Which river is often called the 'Sorrow of Bihar'? / 'బీహార్ దుఃఖదాయిని' అని ఏ నదిని పిలుస్తారు?", ["Kosi", "Godavari", "Narmada", "Tapi"], 0, "The Kosi is known as the Sorrow of Bihar because of its historic floods. / వరదల కారణంగా కోసి నదిని బీహార్ దుఃఖదాయిని అంటారు."),
        ("General Awareness", "Where is the headquarters of the Reserve Bank of India? / భారతీయ రిజర్వ్ బ్యాంక్ ప్రధాన కార్యాలయం ఎక్కడ ఉంది?", ["Mumbai", "New Delhi", "Hyderabad", "Kolkata"], 0, "The RBI headquarters is in Mumbai. / RBI ప్రధాన కార్యాలయం ముంబైలో ఉంది."),
        ("General Awareness", "Which institution conducts recruitment for many non-gazetted railway posts? / అనేక నాన్-గెజిటెడ్ రైల్వే ఉద్యోగాల నియామకాన్ని నిర్వహించే సంస్థ ఏది?", ["Railway Recruitment Boards", "UPSC", "SSC only", "State Public Service Commission"], 0, "Railway Recruitment Boards conduct recruitment for notified railway posts. / ప్రకటించిన రైల్వే పోస్టులకు రైల్వే రిక్రూట్‌మెంట్ బోర్డులు నియామకాలు నిర్వహిస్తాయి."),
        ("General Awareness", "What does the abbreviation RRB stand for in railway recruitment? / రైల్వే నియామకాల్లో RRB పూర్తి రూపం ఏమిటి?", ["Railway Recruitment Board", "Railway Regulation Bureau", "Regional Rail Branch", "Railway Reservation Board"], 0, "RRB stands for Railway Recruitment Board. / RRB అంటే Railway Recruitment Board."),
        ("General Awareness", "Which gauge is commonly used by Indian Railways on its main routes? / భారతీయ రైల్వే ప్రధాన మార్గాల్లో సాధారణంగా ఉపయోగించే గేజ్ ఏది?", ["Broad gauge", "Metre gauge", "Narrow gauge", "Standard gauge"], 0, "Indian Railways predominantly uses broad gauge on its main network. / భారతీయ రైల్వే ప్రధాన నెట్‌వర్క్‌లో ఎక్కువగా బ్రాడ్ గేజ్ ఉపయోగిస్తుంది."),
    ]
    for subject, q, options, answer, why in facts:
        bank.append(make_question(subject, q, options, answer, why))

    return bank


def load_bank():
    with open("data/day-01.json", encoding="utf-8") as f:
        original = json.load(f)
    # Keep original question records, and add a large deterministic pool of fresh practice items.
    combined = original + generated_questions()
    unique = {}
    for q in combined:
        qid = str(q.get("id") or hashlib.sha256(q["q"].encode("utf-8")).hexdigest()[:20])
        q["id"] = qid
        unique[qid] = q
    return list(unique.values())


def load_used_ids():
    try:
        return set(json.loads(STATE_FILE.read_text(encoding="utf-8")))
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        return set()


def save_used_ids(ids):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(sorted(ids), ensure_ascii=False, indent=2), encoding="utf-8")


def answer_indexes(q):
    return q["answers"] if "answers" in q else [q["answer"]]


def answer_label(q):
    indexes = answer_indexes(q)
    letters = ", ".join(chr(65 + n) for n in indexes)
    answer_text = ", ".join(q["options"][n] for n in indexes)
    return letters, answer_text


def main():
    bank = load_bank()
    if len(bank) < QUESTION_COUNT:
        raise SystemExit(f"Question pool has only {len(bank)} unique questions; at least {QUESTION_COUNT} are required.")

    used = load_used_ids()
    available = [q for q in bank if q["id"] not in used]
    cycle_reset = False
    if len(available) < QUESTION_COUNT:
        used = set()
        available = bank[:]
        cycle_reset = True

    questions = random.SystemRandom().sample(available, QUESTION_COUNT)
    used.update(q["id"] for q in questions)

    now = datetime.now(timezone.utc).astimezone()
    stamp = now.strftime("%d %b %Y, %I:%M %p %Z")
    parts = [
        "<!doctype html><html><body style='margin:0;background:#f3f6fb;font-family:Arial,sans-serif;color:#182230'>",
        "<div style='max-width:760px;margin:20px auto;background:#fff;border:1px solid #dce3ee;border-radius:14px;overflow:hidden'>",
        "<div style='background:#173b67;color:#fff;padding:24px'><h1 style='margin:0'>Station Master Success 2026</h1><p style='margin:8px 0 0'>100-question bilingual practice paper · English + తెలుగు</p></div>",
        f"<div style='padding:22px'><p><b>Practice set:</b> {html.escape(stamp)}</p>",
        "<p><b>Instructions:</b> Attempt all 100 questions first. Each question carries 1 mark. Check the answer key and explanation section only after completing the paper. This practice paper does not apply an official negative-marking scheme.</p>",
        "<p><b>Sections:</b> Mathematics · Reasoning · Basic Science · General Awareness · Railway Awareness</p>",
        "<hr style='border:0;border-top:1px solid #dce3ee'>",
    ]
    plain = [
        "STATION MASTER SUCCESS 2026",
        "100-QUESTION BILINGUAL PRACTICE PAPER — ENGLISH + TELUGU",
        f"Practice set: {stamp}",
        "Instructions: Attempt all questions first. Each question carries 1 mark. Answer key and explanations are after Question 100.",
        "This practice paper does not apply an official negative-marking scheme.",
        "",
    ]

    for i, q in enumerate(questions, 1):
        subject = q.get("subject", "Practice")
        parts.append(
            f"<section style='padding:12px 0;border-bottom:1px solid #e8edf4'>"
            f"<div style='font-size:12px;color:#52657c;font-weight:bold'>{html.escape(subject.upper())} · QUESTION {i:03d}</div>"
            f"<h3 style='font-size:16px;line-height:1.5;margin:8px 0'>{html.escape(q['q'])}</h3><ol type='A' style='padding-left:24px;line-height:1.7'>"
        )
        plain.append(f"Q{i:03d}. [{subject}] {q['q']}")
        for option_index, option in enumerate(q["options"]):
            parts.append(f"<li style='padding:2px 0'>{html.escape(str(option))}</li>")
            plain.append(f"    {chr(65 + option_index)}. {option}")
        parts.append("</ol></section>")
        plain.append("")

    parts.append("<div style='background:#eef4fb;padding:16px;margin-top:22px;border-radius:10px'><h2 style='margin:0'>Answer key & explanations / సమాధానాలు మరియు వివరణలు</h2></div>")
    plain.extend(["", "ANSWER KEY & EXPLANATIONS / సమాధానాలు మరియు వివరణలు", ""])
    for i, q in enumerate(questions, 1):
        letters, answer_text = answer_label(q)
        why = q.get("why", "Review the relevant concept and verify the calculation.")
        parts.append(
            f"<div style='padding:12px 0;border-bottom:1px solid #e8edf4'>"
            f"<p style='margin:0 0 5px'><b>Q{i:03d}. {html.escape(letters)} — {html.escape(answer_text)}</b></p>"
            f"<p style='margin:0;color:#34465d;line-height:1.55'>{html.escape(why)}</p></div>"
        )
        plain.append(f"Q{i:03d}. {letters} — {answer_text}")
        plain.append(f"Explanation / వివరణ: {why}")
        plain.append("")

    parts.append(f"<p style='margin-top:24px'><a href='{SITE}' style='display:inline-block;background:#173b67;color:#fff;text-decoration:none;padding:12px 18px;border-radius:8px'>Open the interactive study website / వెబ్‌సైట్‌లో క్విజ్ రాయండి</a></p>")
    parts.append("<p style='font-size:12px;color:#64748b'>Study consistently. Review every incorrect answer before the next practice set.</p></div></div></body></html>")
    plain.extend(["", f"Interactive quiz website: {SITE}", "Study in English + Telugu."])

    msg = EmailMessage()
    msg["Subject"] = f"Station Master 2026 — 100-question practice paper — {now.strftime('%d %b %Y %H:%M %Z')}"
    msg["From"] = os.environ["STUDY_GMAIL_USER"]
    msg["To"] = os.environ.get("STUDY_TO_EMAIL", os.environ["STUDY_GMAIL_USER"])
    msg.set_content("\n".join(plain))
    msg.add_alternative("\n".join(parts), subtype="html")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
        server.login(os.environ["STUDY_GMAIL_USER"], os.environ["STUDY_GMAIL_APP_PASSWORD"])
        server.send_message(msg)

    save_used_ids(used)
    print(f"Sent {QUESTION_COUNT} questions to {msg['To']}. Pool size: {len(bank)}. Fresh questions remaining this cycle: {len(bank) - len(used)}.")
    if cycle_reset:
        print("The unique-question pool was exhausted; a new cycle has started.")


if __name__ == "__main__":
    main()
