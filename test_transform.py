import pandas as pd
import numpy as np
import pytest
from transform import clean_and_encode_student_info

def test_clean_and_encode_student_info():
    """
    Prueba unitaria para verificar la limpieza y codificación ordinal 
    de la tabla StudentInfo.
    """
    # 1. Preparar datos simulados (Mock data)
    mock_data = {
        'id_student': [1, 2, 3, 4],
        'imd_band': ['0-10%', np.nan, '20-30%', np.nan],
        'gender': ['M', 'F', 'M', 'F'],
        'age_band': ['0-35', '35-55', '55<=', '0-35'],
        'final_result': ['Pass', 'Fail', 'Distinction', 'Withdrawn']
    }
    df_mock = pd.DataFrame(mock_data)
    
    # 2. Ejecutar la función a probar
    df_result = clean_and_encode_student_info(df_mock)
    
    # 3. Verificaciones (Assertions)
    
    # Verificar que los nulos en imd_band se reemplazaron por 'Missing'
    assert df_result['imd_band'].iloc[1] == 'Missing'
    assert df_result['imd_band'].iloc[3] == 'Missing'
    assert 'Missing' in df_result['imd_band'].values
    assert df_result['imd_band'].isnull().sum() == 0
    
    # Verificar codificación de género (M=0, F=1)
    assert df_result['ordinal_genero'].iloc[0] == 0.0 # M
    assert df_result['ordinal_genero'].iloc[1] == 1.0 # F
    
    # Verificar codificación de edad ('0-35'=0, '35-55'=1, '55<='=2)
    assert df_result['ordinal_edad'].iloc[0] == 0.0   # 0-35
    assert df_result['ordinal_edad'].iloc[1] == 1.0   # 35-55
    assert df_result['ordinal_edad'].iloc[2] == 2.0   # 55<=
    
    # Verificar codificación de resultado final ('Fail'=0, 'Withdrawn'=1, 'Pass'=2, 'Distinction'=3)
    assert df_result['ordinal_finalResult'].iloc[0] == 2.0 # Pass
    assert df_result['ordinal_finalResult'].iloc[1] == 0.0 # Fail
    assert df_result['ordinal_finalResult'].iloc[2] == 3.0 # Distinction
    assert df_result['ordinal_finalResult'].iloc[3] == 1.0 # Withdrawn

    print("Todas las pruebas pasaron exitosamente.")
