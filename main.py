import os
import logging
from ETL_Code.extract import extract_oulad_data
from ETL_Code.transform import clean_and_encode_student_info, build_student_vle_view
from ETL_Code.load import get_mysql_engine, get_sqlite_engine, load_data_to_mysql

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ETL_Main")

# --- CONFIGURACIÓN ---
# Directorio donde se encuentran los archivos CSV de OULAD
DATA_DIRECTORY = "./data" # Cambiar a la ruta real de los datos

# Límite de filas para pruebas (poner en None para cargar el archivo completo)
TEST_STUDENT_VLE_LIMIT = 50000 

# Configuración de base de datos Embebida (SQLite)
SQLITE_DB_PATH = "oulad_database.sqlite"

# (Opcional, guardado por si luego usamos MySQL)
# DB_USER = "tu_usuario"
# DB_PASSWORD = "tu_password"
# DB_HOST = "localhost"
# DB_PORT = "3306"
# DB_NAME = "oulad_db"

def run_etl_pipeline():
    logger.info("=== Iniciando Pipeline ETL OULAD ===")
    
    # 1. EXTRACT
    try:
        data = extract_oulad_data(DATA_DIRECTORY, student_vle_limit=TEST_STUDENT_VLE_LIMIT)
        df_student_info = data['studentInfo']
        df_student_vle = data['studentVle']
        df_vle = data['vle']
    except Exception as e:
        logger.error("Fallo la fase de extracción. Abortando ETL.", exc_info=True)
        return

    # 2. TRANSFORM
    try:
        df_student_info_ordinal = clean_and_encode_student_info(df_student_info)
        df_student_level_view = build_student_vle_view(df_student_vle, df_vle)
    except Exception as e:
        logger.error("Fallo la fase de transformación. Abortando ETL.", exc_info=True)
        return

    # 3. LOAD
    try:
        # Usamos SQLite como base de datos embebida
        engine = get_sqlite_engine(SQLITE_DB_PATH)
        
        # Cargar StudentInfo_ordinal
        load_data_to_mysql(
            df=df_student_info_ordinal, 
            table_name='StudentInfo_ordinal', 
            engine=engine, 
            if_exists='replace'
        )
        
        # Cargar etl_view_student_level
        load_data_to_mysql(
            df=df_student_level_view, 
            table_name='etl_view_student_level', 
            engine=engine, 
            if_exists='replace'
        )
    except Exception as e:
        logger.error("Fallo la fase de carga. Pipeline incompleto.")
        return

    logger.info("=== Pipeline ETL OULAD completado exitosamente ===")

if __name__ == "__main__":
    # Asegurarse de tener un directorio data de ejemplo o manejar la excepción
    # os.makedirs(DATA_DIRECTORY, exist_ok=True)
    run_etl_pipeline()
