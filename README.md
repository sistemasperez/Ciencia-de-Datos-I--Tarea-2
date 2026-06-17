# OULAD ETL Pipeline

## Descripción del Proyecto
Este proyecto implementa un pipeline ETL (Extracción, Transformación y Carga) modular y optimizado en Python para el dataset [Open University Learning Analytics Dataset (OULAD)](https://analyse.kmi.open.ac.uk/open_dataset). 

El objetivo principal es procesar grandes volúmenes de datos educativos, aplicar reglas de negocio para la limpieza y codificación de variables, y transformar los datos de actividad del entorno virtual de aprendizaje (VLE) mediante pivotes analíticos. Finalmente, los datos se estructuran y se cargan eficientemente en una base de datos embebida (SQLite) para su posterior Análisis Exploratorio de Datos (EDA).

## Arquitectura y Funciones Principales
El código sigue una arquitectura de módulos separados, garantizando encapsulación y funciones reutilizables:

* **`extract.py` (`extract_oulad_data`)**: Se encarga de la lectura de los archivos CSV originales. Implementa optimizaciones estrictas de memoria (definiendo `dtypes` específicos) para manejar archivos pesados como `studentVle.csv`, reduciendo el consumo de memoria RAM hasta en un 75%.
* **`transform.py`**: Contiene la lógica central de negocio.
  * `clean_and_encode_student_info`: Limpia valores nulos (ej. en `imd_band`) y aplica codificación ordinal a variables categóricas (género, edad, resultado final) para alimentar la tabla estructurada `StudentInfo_ordinal`.
  * `build_student_vle_view`: Realiza cruces (MERGE) entre los logs de actividad y la metadata de los recursos. Aplica un `pivot_table` para aplanar las interacciones de los estudiantes, calculando el promedio de clics por tipo de actividad y contando los días únicos de interacción, generando así la vista analítica `etl_view_student_level`.
* **`load.py` (`load_data_to_mysql` / `get_sqlite_engine`)**: Maneja la creación del motor de base de datos usando *SQLAlchemy* y realiza la inserción de datos por lotes (*chunksize*) para evitar colapsos de memoria durante la escritura a disco.
* **`main.py` (`run_etl_pipeline`)**: El script orquestador. Coordina secuencialmente y maneja los errores de las fases de Extracción, Transformación y Carga.
* **`test_transform.py`**: Módulo de control de calidad de software (*Testing*). Utiliza `pytest` para inyectar datos simulados (Mocks) y comprobar automáticamente que la lógica de transformación y limpieza funciona correctamente.

## Requisitos Previos

- Python 3.8 o superior.
- **MUY IMPORTANTE:** Los archivos CSV del dataset OULAD (`studentInfo.csv`, `studentVle.csv`, `vle.csv`) deben ser descargados y colocados **estrictamente dentro de la carpeta vacía `data/`** que se encuentra en la raíz de este proyecto. (Estos archivos no están en GitHub debido a su gran tamaño).

## Instalación

Abre tu terminal, navega a la carpeta raíz de este proyecto y ejecuta el siguiente comando para instalar las dependencias requeridas:

```bash
pip install pandas sqlalchemy pytest
```

## Cómo Ejecutar

### 1. Ejecutar el Pipeline ETL Completo
Para iniciar el proceso de limpieza y transformación de los datos, ejecuta en tu terminal:
```bash
python main.py
```

### 2. Ejecutar las Pruebas Unitarias
Para comprobar la integridad de las reglas de transformación y garantizar la calidad del código, ejecuta:
```bash
pytest test_transform.py -v
```

---

## Enfoque Analítico: Predicción de Abandono Escolar (Dropout)

A nivel de negocio y modelado de datos, toda la estructura de este pipeline ha sido pensada para servir como insumo directo en investigaciones sobre la **Predicción Temprana de Abandono**.

Si detallamos el proceso, no solo hicimos una simple limpieza; convertimos variables cualitativas a escalas ordinales y agregamos los registros de clics diarios en métricas consolidadas de motivación estudiantil (como `total_n_days` o promedios de clics por recurso). Esto no fue aleatorio. Dentro de la variable ordinal de resultado final, contamos con la clase explícita de retiro (*Withdrawn*), que se convierte en nuestro *target* predictivo.

La estrategia para la etapa de Análisis Exploratorio (EDA) y futuro entrenamiento de machine learning es sencilla pero efectiva: cruzar el perfil demográfico del alumno con su nivel de interacción en la plataforma virtual. Por ejemplo, si en las visualizaciones notamos que los estudiantes que terminan desertando presentan caídas evidentes en su participación en foros durante las primeras semanas (visibles a través de nuestra vista pivot), ya tendríamos nuestra hipótesis base validada. Con esa información estructurada, entrenar un algoritmo que detecte esos patrones y alerte a los tutores a tiempo se vuelve un objetivo totalmente realizable con este dataset.
