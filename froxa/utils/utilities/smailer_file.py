import smtplib
from email.message import EmailMessage
import os

class SMailer:
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT   = 465
    USERNAME    = 'avisos@froxa.com'
    PASSWORD    = 'pygh eogx hskj ezaw'

    @staticmethod
    def send_email(to_emails, subject, html_content, file_path=None):
        message_information = []
        for email_name in to_emails:
            try:
                msg = EmailMessage()
                msg['Subject'] = subject
                msg['From']    = SMailer.USERNAME
                msg['To']      = email_name

                # Add content
                msg.set_content('This is a fallback plain-text message.')
                msg.add_alternative(html_content, subtype='html')

                # Add attachment (if provided)
                if file_path and os.path.isfile(file_path):
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                        file_name = os.path.basename(file_path)
                        msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

                # Send email
                with smtplib.SMTP_SSL(SMailer.SMTP_SERVER, SMailer.SMTP_PORT) as smtp:
                    smtp.login(SMailer.USERNAME, SMailer.PASSWORD)
                    smtp.send_message(msg)
                    message_information += [{'email': email_name, 'sent': 1, 'message': subject, 'file': str(file_path)}]
            except Exception:
                message_information += [{'email': email_name, 'sent': 0, 'message': subject, 'file': str(file_path)}]

        return message_information

