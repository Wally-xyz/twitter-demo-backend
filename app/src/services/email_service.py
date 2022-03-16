from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app.src.config.parameter_store import Properties
from app.src.models.models import User


class EmailService:

    @staticmethod
    def send_verification_code(user: User, code: str):
        message = Mail(
            from_email='hello@wallylabs.xyz',
            to_emails=user.email,
            subject='Verify your email address',
            html_content=f'Use the following code: <strong>{code}</strong>')
        sg = SendGridAPIClient(Properties.sendgrid_api_key)
        sg.send(message)

    @staticmethod
    def send_minted_email(user: User, tx_hash: str):
        message = Mail(
            from_email='hello@wallylabs.xyz',
            to_emails=user.email,
            subject='Your NFT has been minted',
            html_content=f'Congratulations, your NFT has been minted. View it on etherscan: '
                         f'https://etherscan.io/tx/{tx_hash}')
        sg = SendGridAPIClient(Properties.sendgrid_api_key)
        sg.send(message)
