from contextlib import contextmanager
from typing import Dict

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.src.config.parameter_store import RelationalDB

# NOTE - https://dataschool.com/learn-sql/how-to-start-a-postgresql-server-on-mac-os-x/ - I used the postgres App
USER = RelationalDB.user("wally_api_user")
PASSWORD = RelationalDB.password("password")
HOST = RelationalDB.host("localhost")
PORT = RelationalDB.port("5432")
NAME = RelationalDB.name("wally_api")

SQLALCHEMY_DATABASE_URL = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}"
engine = create_engine(url=SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency in all of the controllers
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# @contextmanager
# def session_scope(session_args: Dict = None):
#     """Provide a transactional scope around a series of operations."""
#     if not session_args:
#         session = SessionLocal()
#     else:
#         user = session_args.get("user", USER)
#         password = session_args.get("password", PASSWORD)
#         host = session_args.get("host", HOST)
#         port = session_args.get("post", PORT)
#         name = session_args.get("name", NAME)
#
#         session = sessionmaker(
#             autocommit=False,
#             autoflush=False,
#             bind=create_engine(
#                 f"postgresql://{user}:{password}@{host}:{port}/{name}"
#             )
#         )()
#     try:
#         yield session
#         session.commit()
#     except:
#         session.rollback()
#         raise
#     finally:
#         session.close()
