

# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail



class EmailService:


    def send_verification_code(self, email, code):
        message = Mail(
            from_email='from_email@example.com',
            to_emails=email,
            subject='Verify your email address',
            html_content=f'Use the following code: <strong>{code}</strong>')
        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e.message)


