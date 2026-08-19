from sqlalchemy.orm import sessionmaker

from .createDB import check_connection, clean_db, get_mysql_engine, insert_db
from .transform import clean_data, load_data, build_object, check_data
import logging

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    
    df = load_data()
    engine = get_mysql_engine()

    try:
            check_connection(engine)
    except ConnectionError as e:
            print(f"Erreur : {e}")
            raise
    
    if df is not None :
        df_clean = clean_data(df)
        df_clean = check_data(df_clean)
        session_maker = sessionmaker(bind=engine)
        session = session_maker()
        lstCity, lstType, lstHouse = build_object(df_clean)
        
        clean_db(engine)
        
        insert_db(lstCity.values(), session)
        insert_db(lstType.values(), session)
        insert_db(lstHouse, session)