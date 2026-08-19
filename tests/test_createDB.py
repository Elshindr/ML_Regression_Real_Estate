import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ingestion.ORM import City, House, Type, Base

from ingestion.createDB import insert_db, check_connection
from sqlalchemy.exc import SQLAlchemyError,IntegrityError


@pytest.fixture
def engine():
    eng = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)


@pytest.fixture
def session(engine):
    Session = sessionmaker(bind=engine)
    s = Session()
    yield s
    s.close()


def test_mauvaise_connexion():
    engine = create_engine("sqlite:////chemin/inexistant.db")
    with pytest.raises(ConnectionError):
        check_connection(engine)


def test_champ_obligatoire_vide(session):
    house = House(
                idCity= 1,
                idType= 1
    )
    lstHouse:list[House]=[]
    
    lstHouse.append(house)
    
    with pytest.raises(IntegrityError):
       insert_db(lstValues=lstHouse, session=session)


def test_city_mauvais_type(session):
    city = City(
                idCity= 1,
                name= None
    )
    lstcity:list[City]=[]
    
    lstcity.append(city)
    with pytest.raises(SQLAlchemyError):
        insert_db(lstValues=lstcity, session=session)


def test_duplicate_id_raises_integrity_error(session):
    """Deux villes avec le même idCity doivent violer la contrainte de clé primaire."""
    session.add(City(idCity=1, name="Lyon"))
    session.commit()

    session.add(City(idCity=1, name="Paris"))  # même idCity

    with pytest.raises(IntegrityError):
        session.commit()


def test_duplicate_name_raises_integrity_error(session):
    """Deux villes avec le même name doivent violer la contrainte unique=True."""
    session.add(City(idCity=1, name="Lyon"))
    session.commit()

    session.add(City(idCity=2, name="Lyon"))  # même name

    with pytest.raises(IntegrityError):
        session.commit()

def test_city_duplicate_name_raises(session):
    """name est unique=True, donc un doublon doit lever une erreur."""
    session.add(City(idCity=1, name="Lille"))
    session.commit()

    duplicate = City(idCity=2, name="Lille")
    with pytest.raises(SQLAlchemyError):
        insert_db(lstValues=[duplicate], session=session)
        
def test_duplicates_type(session):

    type_one = Type(idType=1, name="app")
    type_dup_id = Type(idType=1, name="house")
    type_dup_name = Type(idType=12, name="app")

    session.add(type_one)
    session.commit()
    
    session.add(type_dup_id)
    session.add(type_dup_name)
    

    with pytest.raises(IntegrityError):
        session.commit()
