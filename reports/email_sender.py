import os
import sys
import smtplib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import date
from dotenv import load_dotenv

load_dotenv()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
MANAGER_EMAIL = os.getenv("MANAGER_EMAIL")

def send_report(pdf_path, target_date=None):
    if target_date is None:
        target_date = date.today()

    subject = f"Doorstep Lagos Daily Operations Report for ({target_date.strftime('%d %B %Y')})"

    body = f"""Good evening Sir/Ma,

Attached is the Daily operations report for Doorstep Lagos, {target_date.strftime('%A, %d %B %Y')}.

It covers the operations overview and delivery success rate, revenue and fuel cost with gross profit, zone performance and traffic impact, and the fleet performance breakdown.
Generated automatically at end of every working day.

Doorstep Lagos Pipeline
"""

    msg = MIMEMultipart()
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = MANAGER_EMAIL
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))
    with open(pdf_path, "rb") as f:
        attachment = MIMEBase("application", "octet-stream")
        attachment.set_payload(f.read())
        encoders.encode_base64(attachment)
        attachment.add_header(
            "Content-Disposition",
            f"attachment; filename=doorstep_lagos_report_{target_date}.pdf"
        )
        msg.attach(attachment)

 # the part that sends the email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, MANAGER_EMAIL, msg.as_string())

    print(f"Report emailed to {MANAGER_EMAIL}")


if __name__ == "__main__":
    from reports.report_builder import build_report
    pdf_path = build_report()
    if pdf_path:
        send_report(pdf_path)