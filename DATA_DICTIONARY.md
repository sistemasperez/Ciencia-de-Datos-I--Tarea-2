# Diccionario de Datos y Escalas Ordinales

Este documento explica las transformaciones aplicadas durante el ETL y la estructura de las tablas resultantes, para facilitar el Análisis Exploratorio de Datos (EDA) y el entrenamiento de modelos de Machine Learning.

## 1. Tabla: `StudentInfo_ordinal`
Contiene la información demográfica del estudiante y el resultado final del curso. Las variables categóricas clave han sido convertidas a **escalas ordinales numéricas** para que puedan ser procesadas matemáticamente por los algoritmos predictivos.

| Columna Original | Columna Transformada | Descripción de la Escala Ordinal | Justificación |
|-----------------|----------------------|--------------------------------|---------------|
| `gender` | `ordinal_genero` | **0** = M (Masculino)<br>**1** = F (Femenino) | Binarización estándar para ML. |
| `age_band` | `ordinal_edad` | **0** = 0-35 años<br>**1** = 35-55 años<br>**2** = 55 años o más | El orden importa. A mayor número, mayor rango de edad. |
| `final_result` | `ordinal_finalResult`| **0** = Fail (Reprobó)<br>**1** = Withdrawn (Abandonó/Se retiró)<br>**2** = Pass (Aprobó)<br>**3** = Distinction (Sobresaliente) | El orden refleja el éxito académico, desde fracaso total hasta excelencia. **Nota: El valor 1 (Withdrawn) es tu objetivo principal de predicción.** |
| `imd_band` | `imd_band` | Índice de privación. Se rellenaron los nulos con `'Missing'`. | Previene que el algoritmo falle por datos vacíos. |

*(Las demás columnas mantienen su formato original)*

---

## 2. Tabla: `etl_view_student_level`
Vista agregada ("Pivot") a nivel de estudiante con su comportamiento e interacciones en el Entorno Virtual de Aprendizaje (VLE).

| Columna | Descripción |
|---------|-------------|
| `id_student` | Identificador único del estudiante. Llave primaria parcial. |
| `code_module` | Código del curso. |
| `code_presentation` | Código de la presentación (semestre/año). |
| `total_n_days` | **Métrica clave de Engagement:** Cantidad de días distintos que el estudiante ingresó a la plataforma virtual. |
| `avg_sum_clicks_[actividad]` | **Comportamiento Específico:** Promedio de clics realizados por el estudiante en un tipo específico de recurso. Por ejemplo: `avg_sum_clicks_forumng` (uso de foros), `avg_sum_clicks_quiz` (exámenes de práctica), `avg_sum_clicks_homepage`. |
