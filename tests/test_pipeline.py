import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ingestion.ORM import City, House, Type, Base
from ingestion.transform import build_object, check_data
from ingestion.createDB import insert_db
from sqlalchemy.exc import IntegrityError


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


def test_poids_mauvais_type():
    df = pd.DataFrame(
        [
            {
                "commande_id": "CMD-001",
                "client_id": "CLI-001",
                "ville_livraison": "Paris",
                "date_commande": "2025-01-01",
                "date_livraison_prevue": "2025-01-02",
                "date_livraison_reelle": "2025-01-03",
                "poids_kg": "ABC",
                "transporteur": "DHL",
                "distance_km": 20,
                "nb_articles": 2,
                "statut": "livre",
                "nb_jour_retard": 0,
                "niveau_retard": "aucun",
            }
        ]
    )

    with pytest.raises(Exception):
        check_data(df)


def test_pipeline_valide(session):
    df = pd.DataFrame(
        [
            {
                "city": "Paris",
                "property_type": "apartment",
                "surface": 65.5,
                "rooms": 3,
                "bedrooms": 2,
                "bathrooms": 1,
                "price": 420000,
                "year_built": 1998,
            }
        ]
    )

    lstCity, lstType, lstHouse = build_object(df, session)
            
    insert_db(lstCity.values(), session)
    insert_db(lstType.values(), session)
    insert_db(lstHouse, session)


    ville__ = lstCity.get("Lyon")
    assert ville__.idVille == 1
    assert ville__.name == "Lyon"

    assert session.query(City).count() == 1
    assert session.query(Type).count() == 1
    assert session.query(House).count() == 1

    ville = session.query(City).first()
    assert ville.idVille == 1
    assert ville.name == "Lyon"

    type_ = session.query(Type).first()
    assert type_.idTransporteur == 1
    assert type_.name == "ColisExpress"

    house = session.query(House).first()
    assert house.idVille == 1
    assert house.idType == 1
    assert isinstance(house.rooms, int)
    assert isinstance(house.surface, float)