import logging

from sqlalchemy.sql.expression import null

from app.src.config.database_config import Base
from app.src.models.helpers import generate_id
from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Table,
    DateTime,
    Boolean,
    func,
    Date,
    UniqueConstraint, Enum, Integer,
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


class Media(Base, CreatedUpdatedMixin):
    __tablename__ = "media"
    id = Column(String, default=lambda: generate_id("m"), primary_key=True, index=True, autoincrement=False)

    ipfs_hash = Column(String)
    pin_size = Column(Integer)
    filename = Column(String)
    key = Column(String)
    name = Column(String)
    description = Column(String)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    user = relationship("User")
