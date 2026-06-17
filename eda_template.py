import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Configuración
SQLITE_DB_PATH = "oulad_database.sqlite"

def get_data_for_eda():
    """
    Se conecta a la BD local, extrae la data procesada en el ETL 
    y cruza demografía con comportamiento para la tesis de Abandono.
    """
    print("Extrayendo datos...")
    conn = sqlite3.connect(SQLITE_DB_PATH)
    df_info = pd.read_sql("SELECT * FROM StudentInfo_ordinal", conn)
    df_vle = pd.read_sql("SELECT * FROM etl_view_student_level", conn)
    conn.close()
    
    # Hacemos el cruce (Merge) usando las llaves del estudiante y su curso
    df_eda = pd.merge(df_info, df_vle, on=['id_student', 'code_module', 'code_presentation'], how='inner')
    
    # FEATURE ENGINEERING PARA LA TESIS:
    # Como el foco es predecir el Abandono (Withdrawn), que en nuestra escala ordinal es el '1',
    # creamos una variable binaria (target) explícita: 1 = Abandonó, 0 = No abandonó (Fail/Pass/Distinction).
    # Esto facilita muchísimo hacer gráficos coloreados por esta variable.
    df_eda['abandono_target'] = (df_eda['ordinal_finalResult'] == 1).astype(int)
    
    print(f"Dataset analítico listo. Registros: {len(df_eda)}")
    return df_eda

# ==============================================================================
# FUNCIONES SOLICITADAS PARA EL EDA EXTENDIDO (TODOs para el compañero)
# ==============================================================================

def plot_matriz_correlacion(df):
    """
    Requisito: Matriz correlacional.
    TODO: 
    1. Filtra las columnas numéricas (edad ordinal, total de días, clics en foros, abandono_target).
    2. Calcula df.corr().
    3. Usa sns.heatmap() para visualizar cuáles actividades tienen la correlación más 
       fuerte (positiva o negativa) con la probabilidad de abandonar el curso.
    """
    print("Ejecutando: Matriz de Correlación...")
    pass

def plot_boxplot_abandono(df):
    """
    Requisito: Boxplot.
    TODO: 
    1. Compara visualmente la distribución de interacción.
    2. Usa sns.boxplot(x='abandono_target', y='total_n_days', data=df).
    3. Esto responderá a la tesis: ¿Es evidente que los alumnos que se retiran entran menos días al portal?
    """
    print("Ejecutando: Boxplot de Abandono...")
    pass

def plot_campana_gauss(df):
    """
    Requisito: Campana de Gauss (KDE / Histograma con curva).
    TODO: 
    1. Toma una métrica clave (ej. avg_sum_clicks_forumng o avg_sum_clicks_quiz).
    2. Usa sns.histplot(data=df, x='...', hue='abandono_target', kde=True).
    3. Analiza si la distribución de interacciones tiene forma normal (Campana de Gauss) 
       y cómo se desplaza la campana entre los que abandonan y los que se quedan.
    """
    print("Ejecutando: Campana de Gauss...")
    pass

def plot_dispersion_engagement(df):
    """
    Requisito: Gráfico de dispersión (Scatter plot).
    TODO: 
    1. Relaciona dos variables continuas. Ej: sns.scatterplot(x='avg_sum_clicks_forumng', y='avg_sum_clicks_resource', hue='abandono_target').
    2. Útil para identificar si hay "clústers" de alumnos (ej. los que leen mucho material pero participan poco en foros son propensos a desertar).
    """
    print("Ejecutando: Gráfico de Dispersión...")
    pass

def plot_matriz_confusion_simulada(df):
    """
    Requisito: Matriz de Confusión.
    OJO: Una matriz de confusión real evalúa un modelo predictivo (ej. Regresión Logística), no el EDA puro.
    TODO: 
    1. Como estamos en la fase de EDA, puedes crear una "regla heurística" baseline para tu tesis.
       Ejemplo: "Si total_n_days < 10, predigo abandono = 1, sino = 0".
    2. Usa from sklearn.metrics import confusion_matrix y sns.heatmap() para graficar 
       qué tan buena es esa regla humana comparada con la realidad (abandono_target).
    """
    print("Ejecutando: Matriz de Confusión...")
    pass


if __name__ == "__main__":
    df = get_data_for_eda()
    
    # Llama las funciones a medida que vayas escribiendo el código de matplotlib/seaborn
    # plot_matriz_correlacion(df)
    # plot_boxplot_abandono(df)
    # plot_campana_gauss(df)
    # plot_dispersion_engagement(df)
    # plot_matriz_confusion_simulada(df)
