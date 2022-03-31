from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app.src.config.parameter_store import Properties
from app.src.models.models import User, Media
from app.src.views.media_view import MediaView


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
            'url': Properties.frontend_url + f'/enter-code?code={code}&email={user.email}',
        }
        sg = SendGridAPIClient(Properties.sendgrid_api_key)
        sg.send(message)

    @staticmethod
    def send_mined_email(media: Media):
        message = Mail(
            from_email=('hello@wallylabs.xyz', 'Wally Labs'),
            to_emails=media.user.email)
        media_view = MediaView(media)
        message.reply_to = 'mayank@wallylabs.xyz'
        message.template_id = 'd-b52b1d6cefff4b41a0850eabdb82ef5e'
        message.dynamic_template_data = {
            'etherscan_url': media_view.etherscan_url,
            'img_url': media_view.s3_url,
            'opensea_url':  media_view.opensea_url,
            'url': Properties.frontend_url + f'?step=5'
        }
        sg = SendGridAPIClient(Properties.sendgrid_api_key)
        sg.send(message)
