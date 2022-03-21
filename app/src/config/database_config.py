import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.src.config.logger_config import LoggerConfig
from app.src.config.parameter_store import RelationalDB

logger = LoggerConfig(__name__).get()

# NOTE - https://dataschool.com/learn-sql/how-to-start-a-postgresql-server-on-mac-os-x/ - I used the postgres App
USER = RelationalDB.user("wally_api_user")
PASSWORD = RelationalDB.password("password")
HOST = RelationalDB.host("localhost")
PORT = RelationalDB.port("5432")
NAME = RelationalDB.name("wally_api")

SQLALCHEMY_DATABASE_URL = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}"

# Set this as an override for Heroku, since they may change the username/passwords without us knowing
if os.environ.get("DATABASE_URL"):
    SQLALCHEMY_DATABASE_URL = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)
    logger.info(SQLALCHEMY_DATABASE_URL)

engine = create_engine(url=SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency in the controllers
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
