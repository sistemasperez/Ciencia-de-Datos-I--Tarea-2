import pandas as pd
from typing import Dict
import os
import logging

logger = logging.getLogger(__name__)

def extract_oulad_data(data_dir: str, student_vle_limit: int = None) -> Dict[str, pd.DataFrame]:
    """
    Extrae los archivos CSV del dataset OULAD y los carga en DataFrames de Pandas.
    
    Args:
        data_dir (str): La ruta al directorio que contiene los archivos CSV de OULAD.
        student_vle_limit (int, opcional): Límite de filas a cargar solo para el archivo pesado studentVle.csv.
        
    Returns:
        Dict[str, pd.DataFrame]: Un diccionario donde las llaves son los nombres 
                                 de las tablas y los valores son los DataFrames.
    """
    logger.info(f"Iniciando extracción de datos desde {data_dir}")
    
    files_to_load = ['studentInfo.csv', 'studentVle.csv', 'vle.csv']
    dataframes = {}
    
    for file_name in files_to_load:
        file_path = os.path.join(data_dir, file_name)
        table_name = file_name.replace('.csv', '')
        
        try:
            logger.info(f"Cargando {file_name}...")
            
            # Optimización de memoria: Especificar tipos de datos para reducir uso de RAM
            # Especialmente útil para el archivo pesado studentVle.csv
            dtypes = {}
            if file_name == 'studentVle.csv':
                dtypes = {
                    'code_module': 'category',
                    'code_presentation': 'category',
                    'id_student': 'int32',
                    'id_site': 'int32',
                    'date': 'int16',
                    'sum_click': 'int16'
                }
            elif file_name == 'studentInfo.csv':
                dtypes = {
                    'code_module': 'category',
                    'code_presentation': 'category',
                    'id_student': 'int32',
                    'gender': 'category',
                    'region': 'category',
                    'highest_education': 'category',
                    'imd_band': 'category',
                    'age_band': 'category',
                    'num_of_prev_attempts': 'int8',
                    'studied_credits': 'int16',
                    'disability': 'category',
                    'final_result': 'category'
                }
            elif file_name == 'vle.csv':
                dtypes = {
                    'id_site': 'int32',
                    'code_module': 'category',
                    'code_presentation': 'category',
                    'activity_type': 'category',
                    'week_from': 'float32', # Tiene nulos, por eso float
                    'week_to': 'float32'
                }

            # Aplicar límite de filas solo si es el archivo pesado y se configuró un límite
            nrows = student_vle_limit if file_name == 'studentVle.csv' else None

            # na_values=['?'] es crucial porque OULAD a veces usa '?' en lugar de nulos vacíos
            dataframes[table_name] = pd.read_csv(file_path, dtype=dtypes, nrows=nrows, na_values=['?'])
            logger.info(f"{file_name} cargado con éxito. Forma: {dataframes[table_name].shape}")
        except FileNotFoundError:
            logger.error(f"Archivo no encontrado: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error al cargar {file_path}: {str(e)}")
            raise
            
    return dataframes
