from app.src.config.database_config import Base
from app.src.models.helpers import generate_id
from app.src.models.typedefs.PaymentStatus import PaymentStatus
from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    DateTime,
    Boolean,
    func,
    Enum,
    Integer,
)
from sqlalchemy.orm import relationship


class CreatedUpdatedMixin(object):
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )


class ABI(Base, CreatedUpdatedMixin):
    __tablename__ = "abi"
    id = Column(String, default=lambda: generate_id("abi"), primary_key=True, index=True, autoincrement=False)
    data = Column(String)
    contract_id = Column(String)
    default_metadata_hash = Column(String)
    address = Column(String)


class User(Base, CreatedUpdatedMixin):
    __tablename__ = "users"
    id = Column(String, default=lambda: generate_id("u"), primary_key=True, index=True, autoincrement=False)
    username = Column(String)  # Currently unused
    address = Column(String)
    private_key = Column(String)
    email = Column(String, index=True, unique=True)
    verified = Column(Boolean, default=False)
    verification_code = Column(String)
    admin = Column(Boolean, default=False)


class Payment(Base, CreatedUpdatedMixin):
    __tablename__ = "payments"
    id = Column(String, default=lambda: generate_id("pymt"), primary_key=True, index=True, autoincrement=False)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    user = relationship("User")
    status = Column(Enum(PaymentStatus))  # NOTE(john) - This is stored as a varchar under the hood
    media_id = Column(String, ForeignKey("media.id"), index=True)
    media = relationship("Media")
    stripe_url = Column(String)
    stripe_id = Column(String)
    intent_id = Column(String)
    intent_confirmed = Column(Boolean, default=False)
    amount_cents = Column(Integer)


class Media(Base, CreatedUpdatedMixin):
    __tablename__ = "media"
    id = Column(String, default=lambda: generate_id("m"), primary_key=True, index=True, autoincrement=False)

    json_ipfs_hash = Column(String)
    media_ipfs_hash = Column(String)
    ipfs_image_url = Column(String)
    filename = Column(String)
    s3_key = Column(String)
    name = Column(String)
    description = Column(String)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    user = relationship("User")

    # TODO - Break out the NFT Data into it's own table that is referencing media?
    txn_hash = Column(String)
    is_confirmed = Column(Boolean, default=False)
    nonce = Column(String)
    token_id = Column(Integer)
    address = Column(String)
