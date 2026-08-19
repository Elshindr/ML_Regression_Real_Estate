import pandas as pd
import numpy as np
from .ORM import City, Type, House, Base
import logging
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

def load_data(path: str = "./data/price_raw.json") -> pd.DataFrame:
    try:
        return pd.read_json(path)
    except (FileNotFoundError, ValueError) as e:
        raise RuntimeError(f"Échec du chargement de {path}") from e


def check_data(df: pd.DataFrame) -> pd.DataFrame:
    try:
        
        required_columns = [
            "city",
            "property_type",
            "surface",
            "rooms",
            "bedrooms",
            "bathrooms",
            "price",
            "year_built"
        ]

        # check colonne manqute
        missing = set(required_columns) - set(df.columns)
        if missing:
            raise ValueError(f"Colonnes manquantes : {missing}")

        if df[required_columns].isnull().any().any():
            raise ValueError("Le CSV contient des valeurs obligatoires manquantes.")
        
        if df.duplicated().any():
            raise ValueError("dupliqué dans le CSV")
        
        # check type
        df["surface"] = pd.to_numeric(df["surface"], errors="raise")
        df["rooms"] = pd.to_numeric(df["rooms"], errors="raise").astype(int)
        df["bedrooms"] = pd.to_numeric(df["bedrooms"], errors="raise").astype(int)
        df["bathrooms"] = pd.to_numeric(df["bathrooms"], errors="raise").astype(int)
        df["price"] = pd.to_numeric(df["price"], errors="raise").astype(int)
        df["year_built"] = pd.to_numeric(df["year_built"], errors="raise").astype(int)
  
        return df
    except Exception as e:
        raise


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    try:
        # Valeurs manquantes
        df["city"] = df.city.apply(lambda v: "unk" if pd.isna(v) else v)
        df["property_type"] = df.property_type.apply(
            lambda v: "unk" if pd.isna(v) else v
        )
        df.surface = df.surface.fillna(df.surface.mean())

        df.bedrooms = df.bedrooms.apply(lambda v: 1 if pd.isna(v) else v)
        df.rooms = df[["rooms", "bedrooms", "bathrooms"]].apply(
            lambda row: (
                1 + row["bedrooms"] + row["bathrooms"]
                if pd.isna(row["rooms"])
                else row["rooms"]
            ),
            axis=1,
        )

        df = df.drop_duplicates()

        # outliers
        surf_outliers = (df["surface"] > 1000) | (df["surface"] < 0)
        moyenne_valide = df.loc[~surf_outliers, "surface"].mean()
        df.loc[surf_outliers, "surface"] = moyenne_valide

        room_outliers = (df["rooms"] > 15) | (df["rooms"] < 0)
        df.loc[room_outliers, "rooms"] = 15

        bed_outliers = df["bedrooms"] > 15
        df.loc[bed_outliers, "bedrooms"] = 15

        bat_outliers = df["bathrooms"] > 10
        df.loc[bat_outliers, "bathrooms"] = 10

        return df
    except Exception as e:
        raise e


def transform_data(df: pd.DataFrame) -> tuple[dict[str, City], dict[str, Type], list[House]]:
    
    try:
        lstCity: dict[str, City] = {}
        lstHouse: list[House] = []
        lstType: dict[str, Type] = {}

        for i, row in df.iterrows():

            # city
            nameCity = row["city"]
            city = lstCity.get(nameCity)
            if city is None:
                city = City(idCity=len(lstCity) + 1, name=nameCity)
                lstCity[nameCity] = city
                
            # Type
            nameType = row["property_type"]
            type_ = lstType.get(nameType)
            if type_ is None:
                type_ = Type(idType=len(lstType) + 1, name=nameType)
                lstType[nameType] = type_

            # House
            surface = float(row["surface"])
            rooms = int(row["rooms"])
            bedrooms = int(row["bedrooms"])
            bathrooms = int(row["bathrooms"])
            price = int(row["price"])
            year = int(row["year_built"])
            house = House(
                idCity=city.idCity,
                idType=type_.idType,
                surface=surface,
                rooms=rooms,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                price=price,
                yearBuilt=year
            )
            lstHouse.append(house)
            
        return lstCity, lstType, lstHouse
    
    except Exception as e:
        raise


def build_cities(df: pd.DataFrame) -> dict[str, City]:
    cities = df["city"].unique()
    return {name: City(name=name) for i, name in enumerate(cities)}


def build_types(df: pd.DataFrame) -> dict[str, Type]:
    types = df["property_type"].unique()
    return {name: Type(name=name) for i, name in enumerate(types)}


def build_object(df: pd.DataFrame) -> tuple[dict[str, City], dict[str, Type], list[House]]:
    lstCity = build_cities(df)
    lstType = build_types(df)
    lstHouse :list[House] = []
    
    
    for idx, row in df.iterrows():
        try:
            house = House(
                city=lstCity[row["city"]],  
                type=lstType[row["property_type"]],
                surface=float(row["surface"]),
                rooms=int(row["rooms"]),
                bedrooms=int(row["bedrooms"]),
                bathrooms=int(row["bathrooms"]),
                price=int(row["price"]),
                yearBuilt=int(row["year_built"]),
            )
            lstHouse.append(house)

        except (ValueError, TypeError, KeyError) as e:
            logger.warning(f"Ligne {idx} ignorée : {e}, {row.to_dict()}")
            continue

    
    return lstCity, lstType, lstHouse

