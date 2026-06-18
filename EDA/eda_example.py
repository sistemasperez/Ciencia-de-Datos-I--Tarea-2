"""
Módulo de Análisis Exploratorio de Datos (EDA) Básico.

Este script sirve como ejemplo para el equipo sobre cómo generar gráficos
estadísticos básicos (Correlación, Boxplot, Histograma y Dispersión) usando 
los datos demográficos de los estudiantes (StudentInfo_ordinal).
"""
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def run_eda():
    print("=== Iniciando Análisis Exploratorio de Datos (EDA) ===")
    
    # 1. Conectar a la base de datos (subiendo un nivel desde la carpeta EDA)
    db_path = os.path.join(os.path.dirname(__file__), '..', 'oulad_database.sqlite')
    print(f"Conectando a la base de datos: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        # Cargar los datos de la tabla ordinal que creaste en el ETL
        df = pd.read_sql_query("SELECT * FROM StudentInfo_ordinal", conn)
        conn.close()
    except Exception as e:
        print(f"Error al conectar o leer la base de datos: {e}")
        return

    print(f"Datos cargados exitosamente: {df.shape[0]} filas y {df.shape[1]} columnas.")
    
    # Configurar el estilo visual de seaborn
    sns.set_theme(style="whitegrid")
    
    # Seleccionar solo variables numéricas para la correlación
    cols_numericas = df.select_dtypes(include=['number', 'float64', 'int64']).columns
    
    # --- FIGURA 1: Matriz de Correlación ---
    print("Generando Matriz de Correlación...")
    plt.figure("Matriz de Correlación", figsize=(10, 8))
    # Usamos spearman ya que tienes variables ordinales
    corr = df[cols_numericas].corr(method='spearman')
    sns.heatmap(corr, annot=True, cmap='viridis', fmt=".2f", cbar=True)
    plt.title('Matriz de Correlación (Spearman)')
    plt.tight_layout()

    # --- FIGURA 2: Boxplot (Caja y Bigotes) ---
    print("Generando Boxplot...")
    plt.figure("Boxplot", figsize=(10, 6))
    # Relacionamos el resultado final ordinal con los créditos estudiados
    if 'ordinal_finalResult' in df.columns and 'studied_credits' in df.columns:
        sns.boxplot(x='ordinal_finalResult', y='studied_credits', data=df, palette="Set2")
        plt.title('Boxplot: Créditos Estudiados por Resultado Final (Ordinal)')
        plt.xlabel('Resultado Final (Ordinal)')
        plt.ylabel('Créditos Estudiados')
    plt.tight_layout()

    # --- FIGURA 3: Campana de Gauss (Histograma con curva de densidad KDE) ---
    print("Generando Campana de Gauss / Distribución...")
    plt.figure("Distribución Normal", figsize=(10, 6))
    if 'studied_credits' in df.columns:
        # kde=True dibuja la curva de densidad (Campana)
        sns.histplot(df['studied_credits'], kde=True, color='royalblue', bins=30)
        plt.title('Distribución de Créditos Estudiados (Campana de Gauss)')
        plt.xlabel('Créditos Estudiados')
        plt.ylabel('Frecuencia')
    plt.tight_layout()

    # --- FIGURA 4: Gráfico de Dispersión (Scatter Plot) ---
    print("Generando Gráfico de Dispersión...")
    plt.figure("Dispersión", figsize=(10, 6))
    if 'num_of_prev_attempts' in df.columns and 'studied_credits' in df.columns:
        # Añadimos un poco de 'jitter' (ruido) visual si los datos están muy solapados
        sns.scatterplot(x='num_of_prev_attempts', y='studied_credits', 
                        hue='ordinal_finalResult', data=df, palette='coolwarm', alpha=0.7)
        plt.title('Dispersión: Intentos Previos vs Créditos Estudiados')
        plt.xlabel('Número de Intentos Previos')
        plt.ylabel('Créditos Estudiados')
    plt.tight_layout()

    print("\n--- ATENCIÓN ---")
    print("Los gráficos han sido generados en memoria.")
    print("Se abrirán ventanas emergentes con los gráficos.")
    print("Para ver el siguiente gráfico, cierra la ventana actual o mira si se abrieron todas juntas.")
    
    # plt.show() es la función mágica que "despliega" los gráficos cuando no estás en un Notebook.
    # Bloqueará la ejecución del script hasta que cierres las ventanas de los gráficos.
    plt.show()

if __name__ == "__main__":
    run_eda()
