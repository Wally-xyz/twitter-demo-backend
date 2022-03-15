from sqlalchemy.orm import Session
import stripe

from app.src.config.logger_config import LoggerConfig
from app.src.config.parameter_store import Properties
from app.src.models.models import Payment
from app.src.models.typedefs.PaymentStatus import PaymentStatus

logger = LoggerConfig(__name__).get()


class PaymentService:
    stripe.api_key = Properties.stripe_api_key

    # Payment
    @staticmethod
    def create_payment(db: Session, user_id: str) -> str:
        payment = Payment(user_id=user_id, status=PaymentStatus.PENDING)
        db.add(payment)
        db.commit()
        db.refresh(payment)
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': 'price_1KdEBBBRQJlh59702ERTzDWh',
                    # TODO - Calculate on demand? Pull from parameter store?
                    'quantity': 1,
                },
            ],
            mode='payment',
            # It seems like this should redirect to a FE url?
            # Which then pings our backend with additional information...?
            success_url=Properties.base_domain + f'/payments/{payment.id}/record?success=True',
            cancel_url=Properties.base_domain + f'/payments/{payment.id}/record?success=False',
        )
        # Figure it's good to save this just in case, not sure what other data we get?
        logger.info(checkout_session)
        payment.stripe_url = checkout_session.url
        payment.stripe_id = checkout_session.id
        payment.amount_cents = checkout_session.amount_total
        db.commit()
        return checkout_session.url

    # Update Payment
    # Payment
    @staticmethod
    def update(db: Session, user_id: str, payment_id: str, success: bool) -> Payment:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if payment.user_id != user_id:
            raise Exception("Unauthorized update")
        if success:
            payment.status = PaymentStatus.SUCCESS
        else:
            payment.status = PaymentStatus.FAILURE
        db.commit()
        return payment
