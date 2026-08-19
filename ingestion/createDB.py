from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from .ORM import City, Type, House, Base
import os
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Engine
from sqlalchemy.orm import Session

load_dotenv(Path(".env"))

host = os.getenv("MYSQL_HOST", "127.0.0.1")
user = os.getenv("MYSQL_USER")
pwd = os.getenv("MYSQL_PASSWORD")
db = os.getenv("MYSQL_DATABASE")
port = os.getenv("MYSQL_PORT", 3306)


def get_mysql_engine()-> Engine:
    return create_engine(f"mysql+mysqlconnector://{user}:{pwd}@{host}:{port}/{db}")


def check_connection(engine: Engine) -> None:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except SQLAlchemyError as e:
        raise ConnectionError("Impossible de se connecter à la base.") from e


def clean_db(engine: Engine) -> None :
    # Creation de l'architecture de la db
    try:
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
    except Exception as e:
        print(f"Erreur lors de la creation de la db:{str(e)}")


def insert_db(lstValues: list[City | Type | House], session: Session) -> None:
    try:
        session.add_all(lstValues)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise
    except SQLAlchemyError:
        session.rollback()
        raise
