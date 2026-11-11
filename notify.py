# notify.py - Job Finder, step 3: email the top matches daily
import os, smtplib
from email.mime.text import MIMEText
from match import ranked

def build_email(jobs):
    rows = []
    for j in jobs:
        pay = f"${j['salary']:,}" if j["salary"] else "pay not listed"
        flag = " <i>(applied here before)</i>" if j["applied_before"] else ""
        rows.append(f"<p><b>{j['score']}/100</b> [{j['track']}] {j['company']}: "
                    f"<a href='{j['url']}'>{j['title']}</a><br>{j['location']} | {pay}{flag}</p>")
    return "<h2>Today's top job matches</h2>" + "".join(rows) if rows else "<p>No new matches today.</p>"

def send(html):
    me = os.environ["GMAIL_ADDRESS"]
    msg = MIMEText(html, "html")
    msg["Subject"], msg["From"], msg["To"] = "Job Finder: today's matches", me, me
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(me, os.environ["GMAIL_APP_PASSWORD"])
        s.send_message(msg)

if __name__ == "__main__":
    top = [j for j in ranked() if j["score"] >= 30][:15]
    send(build_email(top))
