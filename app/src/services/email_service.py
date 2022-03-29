from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app.src.config.parameter_store import Properties
from app.src.models.models import User


class EmailService:

    @staticmethod
    def send_verification_code(user: User, code: str):
        message = Mail(
            from_email=('hello@wallylabs.xyz', 'Wally Labs'),
            to_emails=user.email)
        message.reply_to = 'mayank@wallylabs.xyz'
        message.template_id = 'd-ec91b40826a54c2d9d324da8341461fb'
        message.dynamic_template_data = {
            'code': code,
            'email': user.email,
            'url': Properties.frontend_url + f'?code={code}&email={user.email}',
        }
        sg = SendGridAPIClient(Properties.sendgrid_api_key)
        sg.send(message)

    @staticmethod
    def send_mined_email(user: User, tx_hash: str):
        message = Mail(
            from_email=('hello@wallylabs.xyz', 'Wally Labs'),
            to_emails=user.email)
        message.reply_to = 'mayank@wallylabs.xyz'
        message.template_id = 'd-b52b1d6cefff4b41a0850eabdb82ef5e'
        message.dynamic_template_data = {
            'etherscan_url': f'https://etherscan.io/tx/{tx_hash}',
            'img_url': 'https://www.wallylabs.xyz/logo.png',
            'opensea_url': 'https://testnets.opensea.io/collection/wally',
            'url': Properties.frontend_url + f'?step=5'
        }
        sg = SendGridAPIClient(Properties.sendgrid_api_key)
        sg.send(message)
