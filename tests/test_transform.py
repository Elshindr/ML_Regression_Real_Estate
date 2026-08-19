import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ingestion.ORM import City, House, Type, Base
from ingestion.transform import (
    load_data,
    clean_data,
    build_cities,
    build_types,
    build_object,
    check_data,
)


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


def test_load_data_file_not_found():
    with pytest.raises(RuntimeError):
        load_data("cheminquinexiste/pas.json")


def test_colonne_manquante():

    df = pd.DataFrame(
        [
            {
                "city": "Paris",
                "property_type": "apartment",
                "surface": 65.5,
                "rooms": 3,
                "bedrooms": 2,
                "bathrooms": 1,
                "year_built": 1998,
            }
        ]
    )
    with pytest.raises(ValueError):
        check_data(df)


def test_champ_obligatoire_vide():
    df = pd.DataFrame(
        [
            {
                "city": "Paris",
                "property_type": "apartment",
                "surface": 65.5,
                "rooms": 3,
                "bedrooms": 2,
                "bathrooms": 1,
                "price": "Noeene",
                "year_built": 1998
            }
        ]
    )

    with pytest.raises(ValueError):
        check_data(df)


def test_no_duplicates():
    df = pd.DataFrame(
        [
            {
                "city": "Paris",
                "property_type": "apartment",
                "surface": 65.5,
                "rooms": 3,
                "bedrooms": 2,
                "bathrooms": 1,
                "price": 1,
                "year_built": 1998,
            },
            {
                "city": "Paris",
                "property_type": "apartment",
                "surface": 65.5,
                "rooms": 3,
                "bedrooms": 2,
                "bathrooms": 1,
                "price": 1,
                "year_built": 1998,
            },
        ]
    )

    df_no_dup = clean_data(df)

    assert len(df_no_dup) == 1
    
def test_build_object_rejects_invalid_row_and_continues():
    df_invalid = pd.DataFrame({
        "city": ["Lille", "Paris"],
        "property_type": ["appartement", "maison"],
        "surface": [50.0, "not_a_number"],  # ligne invalide
        "rooms": [3, 5],
        "bedrooms": [2, 3],
        "bathrooms": [1, 2],
        "price": [150000, 400000],
        "year_built": [2010, 1990],
    })

    lstCity, lstType, lstHouse = build_object(df_invalid)

    assert len(lstHouse) == 1


def test_build_object_types_are_correct():
    df = pd.DataFrame({
        "city": ["Lille", "Paris"],
        "property_type": ["appartement", "maison"],
        "surface": [50.0, 12], 
        "rooms": [3, 5],
        "bedrooms": [2, 3],
        "bathrooms": [1, 2],
        "price": [150000, 400000],
        "year_built": [2010, 1990],
    })
    
    lstCity, lstType, lstHouse = build_object(df)

    for house in lstHouse:
        assert isinstance(house.surface, float)
        assert isinstance(house.rooms, int)
        assert isinstance(house.bedrooms, int)
        assert isinstance(house.bathrooms, int)
        assert isinstance(house.price, int)
        assert isinstance(house.yearBuilt, int)
        assert isinstance(house, House)