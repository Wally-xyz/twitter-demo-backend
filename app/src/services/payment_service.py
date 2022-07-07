from sqlalchemy.orm import Session
import stripe

from app.src.config.logger_config import LoggerConfig
from app.src.config.parameter_store import Properties
from app.src.models.models import Payment, User
from app.src.models.typedefs.PaymentStatus import PaymentStatus
from app.src.services.media_service import MediaService
from app.src.services.user_service import UserService

logger = LoggerConfig(__name__).get()


class PaymentService:
    stripe.api_key = Properties.stripe_api_key

    @staticmethod
    def create_payment(db: Session, user_id: str) -> str:
        payment = Payment(user_id=user_id, status=PaymentStatus.PENDING)
        user = UserService.get(db, user_id)
        media = MediaService.get_most_recent(db, user)
        db.add(payment)
        db.commit()
        db.refresh(payment)
        success_url = Properties.frontend_url + f'/mint?success=True'
        cancel_url = Properties.frontend_url + f'/purchase?success=False'
        checkout_session = stripe.checkout.Session.create(
            customer_email=user.email,
            line_items=[
                {
                    'name': 'Wally NFT',
                    'quantity': 1,
                    'images': [media.s3_url()],
                    'amount': 4999,
                    'currency': 'usd'
                },
            ],
            allow_promotion_codes=True,
            mode='payment',
            success_url=success_url,
            cancel_url=success_url if user.admin else cancel_url,
        )
        # Figure it's good to save this just in case, not sure what other data we get?
        logger.info(checkout_session)
        payment.stripe_url = checkout_session.url
        payment.stripe_id = checkout_session.id
        payment.intent_id = checkout_session.payment_intent
        payment.amount_cents = checkout_session.amount_total
        db.commit()
        return checkout_session.url

    @staticmethod
    def create_payment_intent(db: Session, user_id: str) -> str:
        payment = Payment(user_id=user_id, status=PaymentStatus.PENDING)
        db.add(payment)
        db.commit()
        db.refresh(payment)
        checkout_session = stripe.PaymentIntent.create(
            amount=4999,
            currency='usd',
            automatic_payment_methods={
                'enabled': True,
            },
        )
        logger.info(checkout_session)
        payment.stripe_id = checkout_session.id
        payment.amount_cents = checkout_session.amount
        db.commit()
        return checkout_session

    @staticmethod
    def update(db: Session, user_id: str, payment_id: str, success: bool) -> Payment:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        result = stripe.PaymentIntent.retrieve(payment.intent_id)
        logger.info(result)
        if result.status == "succeeded":
            payment.intent_confirmed = True
        else:
            raise Exception("Unable to confirm payment")

        if payment.user_id != user_id:
            raise Exception("Unauthorized update")

        # TODO - Might be able to get rid of this
        if success:
            payment.status = PaymentStatus.SUCCESS
        else:
            payment.status = PaymentStatus.FAILURE

        db.commit()
        return payment

    @staticmethod
    def open_payment(db: Session, user: User) -> Payment:
        return db.query(Payment).filter(Payment.user == user
                                        and Payment.media is None
                                        and Payment.status == PaymentStatus.SUCCESS).first()

    @staticmethod
    def associate_media_with_payment(db: Session, payment: Payment, media_id: str) -> Payment:
        payment.media_id = media_id
        db.commit()
        db.refresh(payment)
        return payment


