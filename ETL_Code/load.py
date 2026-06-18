import pandas as pd
from sqlalchemy import create_engine
import logging

logger = logging.getLogger(__name__)

def get_mysql_engine(user: str, password: str, host: str, port: str, database: str):
    """
    Crea una conexión de SQLAlchemy a MySQL usando pymysql.
    """
    connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    return create_engine(connection_string)

def get_sqlite_engine(db_path: str):
    """
    Crea una conexión de SQLAlchemy a SQLite (base de datos embebida).
    """
    connection_string = f"sqlite:///{db_path}"
    return create_engine(connection_string)

def load_data_to_mysql(df: pd.DataFrame, table_name: str, engine, if_exists: str = 'replace'):
    """
    Inserta un DataFrame en una tabla de MySQL usando SQLAlchemy.
    
    Args:
        df (pd.DataFrame): Los datos a insertar.
        table_name (str): El nombre de la tabla destino.
        engine: El motor de SQLAlchemy.
        if_exists (str): Qué hacer si la tabla ya existe ('fail', 'replace', 'append').
    """
    logger.info(f"Cargando datos en la tabla {table_name} (if_exists='{if_exists}')...")
    
    try:
        # Añadido chunksize=10000 para no agotar la RAM al insertar
        df.to_sql(name=table_name, con=engine, if_exists=if_exists, index=False, chunksize=10000)
        logger.info(f"Carga en {table_name} completada exitosamente. Filas insertadas: {len(df)}")
    except Exception as e:
        logger.error(f"Error al cargar en la tabla {table_name}: {str(e)}")
        raise
