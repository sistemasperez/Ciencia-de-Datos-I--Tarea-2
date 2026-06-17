import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def clean_and_encode_student_info(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia los nulos y genera columnas ordinales para la tabla StudentInfo_ordinal.
    
    Args:
        df (pd.DataFrame): DataFrame original de studentInfo.
        
    Returns:
        pd.DataFrame: DataFrame transformado.
    """
    logger.info("Transformando StudentInfo...")
    df_transformed = df.copy()
    
    # 1. Limpiar nulos de 'imd_band'
    if df_transformed['imd_band'].dtype.name == 'category':
        if 'Missing' not in df_transformed['imd_band'].cat.categories:
            df_transformed['imd_band'] = df_transformed['imd_band'].cat.add_categories('Missing')
    df_transformed['imd_band'] = df_transformed['imd_band'].fillna('Missing')
    
    # 2. Generar columnas ordinales numéricas
    genero_map = {'M': 0, 'F': 1}
    edad_map = {'0-35': 0, '35-55': 1, '55<=': 2} # Manejando '55<=' como viene en los datos a veces, asumiendo '55<' u otros
    # Si viene exactamente como '55<', ajustamos el mapa
    edad_map_exact = {'0-35': 0, '35-55': 1, '55<': 2, '55<=': 2}
    
    result_map = {'Fail': 0, 'Withdrawn': 1, 'Pass': 2, 'Distinction': 3}
    
    df_transformed['ordinal_genero'] = df_transformed['gender'].map(genero_map)
    df_transformed['ordinal_edad'] = df_transformed['age_band'].map(edad_map_exact)
    df_transformed['ordinal_finalResult'] = df_transformed['final_result'].map(result_map)
    
    logger.info("Transformación de StudentInfo completada.")
    return df_transformed

def build_student_vle_view(df_student_vle: pd.DataFrame, df_vle: pd.DataFrame) -> pd.DataFrame:
    """
    Une studentVle con vle y pivotea para crear la vista etl_view_student_level.
    
    Args:
        df_student_vle (pd.DataFrame): DataFrame de studentVle.
        df_vle (pd.DataFrame): DataFrame de vle.
        
    Returns:
        pd.DataFrame: DataFrame pivoteado y agregado.
    """
    logger.info("Transformando studentVle (creando etl_view_student_level)...")
    
    # Unir studentVle con vle para obtener el activity_type
    merged_df = pd.merge(df_student_vle, df_vle[['id_site', 'activity_type']], on='id_site', how='left')
    
    # Agrupar por estudiante y curso, pivotar
    # Primero agregamos los clicks sumados por día y estudiante para luego promediar, 
    # o directamente hacemos el pivot con la función de agregación especificada.
    # El requerimiento dice: "transformar las filas verticales de activity_type 
    # en columnas horizontales de promedios llamadas avg_sum_clicks_[activity_type] 
    # y contar los días únicos en total_n_days."
    
    # Calculamos primero el total de dias unicos por estudiante y curso (y modulo/presentacion)
    group_cols = ['id_student', 'code_module', 'code_presentation']
    
    days_df = merged_df.groupby(group_cols)['date'].nunique().reset_index(name='total_n_days')
    
    # Pivot de activity_type calculando el promedio de la suma de clicks.
    # Nota: la instrucción "promedios de suma de clicks" puede significar 
    # promedio de clicks por acceso, o promedios sobre los días. Usaremos mean().
    pivot_df = pd.pivot_table(
        merged_df,
        values='sum_click',
        index=group_cols,
        columns='activity_type',
        aggfunc='mean', # Promedio de clicks
        fill_value=0
    )
    
    # Renombrar columnas resultantes del pivot
    pivot_df.columns = [f'avg_sum_clicks_{col}' for col in pivot_df.columns]
    pivot_df = pivot_df.reset_index()
    
    # Unir dias totales con el pivot
    final_df = pd.merge(days_df, pivot_df, on=group_cols, how='inner')
    
    logger.info("Transformación de studentVle completada.")
    return final_df
