"""
Módulo de Análisis Avanzado para Tesis de Deserción.

Este script cruza los datos demográficos (StudentInfo_ordinal) con los datos
de comportamiento (etl_view_student_level) para encontrar correlaciones más
profundas entre la interacción en la plataforma y la deserción estudiantil.
"""
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def run_eda_tesis():
    print("=== EDA Avanzado para Tesis: Análisis de Deserción ===")
    
    # Conexión a la base de datos (sube un nivel)
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'oulad_database.sqlite')
    print(f"Conectando a SQLite: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        
        # 1. Cargar datos demográficos y de resultados
        df_info = pd.read_sql_query("SELECT * FROM StudentInfo_ordinal", conn)
        
        # 2. Cargar datos de comportamiento (interacciones en el VLE)
        df_vle = pd.read_sql_query("SELECT * FROM etl_view_student_level", conn)
        
        conn.close()
    except Exception as e:
        print(f"Error al leer la base de datos: {e}")
        return

    print(f"Datos Demográficos cargados: {df_info.shape[0]} registros.")
    print(f"Datos de Comportamiento cargados: {df_vle.shape[0]} registros.")

    # 3. Cruzar ambas tablas
    # Unimos por estudiante, módulo y presentación para asegurar que cruzamos exactamente
    # el comportamiento de un estudiante en un curso específico con su resultado final.
    print("Cruzando datos (Demografía + Comportamiento)...")
    df_master = pd.merge(
        df_info, 
        df_vle, 
        on=['id_student', 'code_module', 'code_presentation'], 
        how='inner' # Inner para quedarnos solo con estudiantes que tienen datos en ambas tablas
    )
    
    print(f"Cruce exitoso. El nuevo Dataset Maestro tiene {df_master.shape[0]} registros y {df_master.shape[1]} columnas.")
    
    # 4. Análisis de Correlación
    # Seleccionamos variables numéricas, incluyendo las nuevas de clics
    cols_numericas = df_master.select_dtypes(include=['number', 'float64', 'int64']).columns
    
    # Opcional: Para evitar una matriz gigantesca e ilegible, filtramos columnas clave para la tesis.
    # Eliminamos el id_student que no aporta a la correlación.
    cols_a_ignorar = ['id_student', 'id_student_x', 'id_student_y']
    cols_relevantes = [col for col in cols_numericas if col not in cols_a_ignorar]

    df_corr = df_master[cols_relevantes]

    # --- FIGURA 1: Matriz de Correlación Extendida ---
    sns.set_theme(style="whitegrid")
    
    # Ajustamos el tamaño porque ahora habrá muchas más columnas
    plt.figure("Matriz de Correlación Tesis", figsize=(14, 12))
    
    corr = df_corr.corr(method='spearman')
    
    # Dibujamos el mapa de calor con los valores numéricos (annot=True)
    # Reducimos el tamaño de la fuente (annot_kws) para que los números quepan en las celdas
    sns.heatmap(corr, annot=True, annot_kws={"size": 7}, cmap='RdYlBu', fmt=".2f", cbar=True)
    plt.title('Matriz de Correlación (Demografía + Comportamiento)', fontsize=16)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # --- FIGURA 2: Impacto del comportamiento en la Deserción (Boxplot) ---
    # Queremos ver si 'total_n_days' (días totales de interacción) afecta el resultado final
    plt.figure("Días de Interacción vs Resultado", figsize=(10, 6))
    if 'total_n_days' in df_master.columns and 'ordinal_finalResult' in df_master.columns:
        sns.boxplot(x='ordinal_finalResult', y='total_n_days', data=df_master, palette="Set3")
        plt.title('Días Totales de Interacción vs Resultado Final')
        plt.xlabel('Resultado Final (Ordinal: 0=Fail, 1=Withdrawn, 2=Pass, 3=Distinction)')
        plt.ylabel('Días Totales Interactuados')
    plt.tight_layout()

    # --- FIGURA 3: Clics vs Resultados (Scatter) ---
    # Un gráfico de dispersión para observar si más clics en foros o contenido general reduce la deserción.
    # Buscaremos una columna generada dinámicamente como avg_sum_clicks_forumng o similar.
    # Si no sabemos exactamente cuáles existen, buscamos una que contenga 'oucontent' o 'forumng'
    col_content = next((col for col in df_master.columns if 'oucontent' in col.lower()), None)
    
    if col_content:
        plt.figure("Clics en Contenido vs Días Activos", figsize=(10, 6))
        sns.scatterplot(
            x='total_n_days', 
            y=col_content, 
            hue='final_result', # Usamos el categórico original para que la leyenda sea más clara
            data=df_master, 
            palette='coolwarm', 
            alpha=0.6
        )
        plt.title(f'Interacción: Días Totales vs {col_content}')
        plt.xlabel('Días Totales Interactuados')
        plt.ylabel(f'Promedio de Clics ({col_content})')
    plt.tight_layout()

    print("\n--- GRÁFICOS GENERADOS ---")
    print("Se abrirán las ventanas con los gráficos ampliados para tu tesis.")
    print("Presta mucha atención al gráfico de Boxplot de 'Días Totales vs Resultado Final'.")
    plt.show()

if __name__ == "__main__":
    run_eda_tesis()
