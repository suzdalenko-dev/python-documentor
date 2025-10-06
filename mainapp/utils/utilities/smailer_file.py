import smtplib
from email.message import EmailMessage
import os
from mainapp.utils.utilities.funcions_file import get_keys

class SMailer:
    @staticmethod
    def send_email(to_emails, subject, html_content, file_path=None):
        documentor_email = get_keys("email.json")
        
        message_information = []
        for email_name in to_emails:
            try:
                msg = EmailMessage()
                msg['Subject'] = subject
                msg['From']    = documentor_email['USERNAME']
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
                with smtplib.SMTP_SSL(documentor_email['SMTP_SERVER'], documentor_email['SMTP_PORT']) as smtp:
                    smtp.login(documentor_email['USERNAME'], documentor_email['PASSWORD'])
                    smtp.send_message(msg)
                    message_information += [{'email': email_name, 'sent': 1, 'message': subject, 'file': str(file_path)}]
            except Exception as e:
                message_information += [{'email': email_name, 'sent': 0, 'message': subject, 'file': str(file_path), 'error': str(e)}]

        print(message_information)

        return message_information

