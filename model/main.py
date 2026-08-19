from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from ingestion.ORM import City, Type, House, Base
import os
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy import create_engine, text, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Engine
from sqlalchemy.orm import Session
import logging
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OrdinalEncoder, OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

load_dotenv()
host = os.getenv("MYSQL_HOST", "127.0.0.1")
user = os.getenv("MYSQL_USER")
pwd = os.getenv("MYSQL_PASSWORD")
db = os.getenv("MYSQL_DATABASE")
port = os.getenv("MYSQL_PORT", 3306)
logger = logging.getLogger(__name__)


def get_mysql_engine() -> Engine:
    return create_engine(f"mysql+mysqlconnector://{user}:{pwd}@{host}:{port}/{db}")


def check_connexion(engine: Engine) -> None:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except SQLAlchemyError as e:
        raise ConnectionError("Impossible de se connecter à la base.") from e


def get_datas_from_db(
    session: Session,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # textual_sql=text("SELECT idCommande, idClient, idTransporteur, poidsKg, distanceKm, nbArticle, statut, jourRetard, niveauRetard FROM commande ")
    # orm_sql = select(User).from_statement(textual_sql)
    stm = select(House, City.idCity, Type.idType).join(House.city).join(House.type)
    # result = session.execute(stm)
    df_house = pd.read_sql(stm, session.bind)

    logger.info(df_house.head())
    df_ville = pd.read_sql(select(City), session.bind)
    df_type = pd.read_sql(select(Type), session.bind)

    return df_house, df_ville, df_type


def train_model(df: pd.DataFrame):
    feats = df[["idCity", "idType", "surface", "rooms", "yearBuilt"]]
    target = df["price"]

    X_train, X_test, y_train, y_test = train_test_split(
        feats, target, test_size=0.2, random_state=42
    )

    cols_nums = ["surface", "rooms", "yearBuilt"]
    sc = StandardScaler()
    X_train_scaled = sc.fit_transform(X_train[cols_nums])
    X_test_scaled = sc.transform(X_test[cols_nums])

    cols_cat = ["idType", "idCity"]
    oe = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
    X_train_oe = oe.fit_transform(X_train[cols_cat])
    X_test_oe = oe.transform(X_test[cols_cat])

    ohe = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    X_train_ohe = ohe.fit_transform(X_train[cols_cat])
    X_test_ohe = ohe.transform(X_test[cols_cat])

    X_train_final = pd.concat(
        [
            pd.DataFrame(X_train_scaled, columns=sc.get_feature_names_out(cols_nums)),
            pd.DataFrame(X_train_oe, columns=oe.get_feature_names_out(cols_cat)),
            pd.DataFrame(X_train_ohe, columns=ohe.get_feature_names_out(cols_cat)),
        ],
        axis=1,
    )

    X_test_final = pd.concat(
        [
            pd.DataFrame(X_test_scaled, columns=sc.get_feature_names_out(cols_nums)),
            pd.DataFrame(X_test_oe, columns=oe.get_feature_names_out(cols_cat)),
            pd.DataFrame(X_test_ohe, columns=ohe.get_feature_names_out(cols_cat)),
        ],
        axis=1,
    )

    logger.info(X_train_final.head())
    print(X_train_final.head())

    features= ["surface", "yearBuilt", "rooms", "idCity", "idType"] 
    model = RandomForestRegressor(random_state=42)

    model.fit(X_train_final[features], y_train)

    y_pred = model.predict(X_test_final[features])
    mae = mean_absolute_error(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred) ** 0.5
    r2 = r2_score(y_test, y_pred)

    print("MAE :", mae)
    print("RMSE:", rmse)
    print("R²  :", r2)
    
    importance = pd.Series(
        model.feature_importances_, index=X_train_final[features].columns
    ).sort_values(ascending=False)

    print(importance)
    
    joblib.dump(model, './model/regression_model.pkl')


if __name__ == "__main__":

    engine = get_mysql_engine()
    check_connexion(engine)
    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    df_house, df_ville, df_type = get_datas_from_db(session)

    train_model(df_house)
