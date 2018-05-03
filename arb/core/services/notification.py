import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from twilio.rest import Client
from arb import TWILIO_ACCOUNT
from arb import TWILIO_TOKEN


class Notification:
    def __init__(self):
        self.twilio = Client(TWILIO_ACCOUNT, TWILIO_TOKEN)

    def send_email(self, recipient, subject, body):
        from_addr = "ycoin23@gmail.com"
        to_addr = recipient
        msg = MIMEMultipart()
        msg['From'] = from_addr
        msg['To'] = to_addr
        msg['Subject'] = subject

        body = body
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login("ycoin23@gmail.com", "Yash1234567890")
        text = msg.as_string()
        server.sendmail(from_addr, to_addr, text)

    def send_text(self, recipient, msg):
        message = self.twilio.messages.create(to=recipient, from_="+18582391611", body=msg)
        print message