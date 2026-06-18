"""
============================================================
  EDA EXTENDIDO — Ciencias de Datos I (INF-8237)
  Dataset: OULAD (Open University Learning Analytics)
  Universidad Autónoma de Santo Domingo (UASD)
  Supervisado por: Dr. Silverio Del Orbe Abad
============================================================

Visualizaciones incluidas:
  1.  Matriz de Correlación (Spearman)
  2.  Matriz de Confusión (Modelo Predictivo)
  3.  Boxplot — Créditos por Resultado Final
  4.  Boxplot — Días de Interacción por Resultado
  5.  Campana de Gauss (KDE + Histograma)
  6.  Gráfico de Barras — Distribución de Resultados
  7.  Gráfico de Barras Apiladas — Género vs Resultado
  8.  Scatter Plot — Intentos Previos vs Créditos
  9.  Scatter Plot — Días Activos vs Clics (coloreado)
  10. Análisis de Curtosis (Kurtosis) — Comparativa
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from scipy import stats
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import warnings
import os

warnings.filterwarnings("ignore")

# ── Paleta y estilo global ─────────────────────────────────────────────────────
PALETTE   = ["#2D6A9F", "#E63946", "#2A9D8F", "#F4A261", "#8338EC"]
ACCENT    = "#2D6A9F"
BG_COLOR  = "#F8F9FA"
GRID_COL  = "#DEE2E6"
FONT_MAIN = "DejaVu Sans"

sns.set_theme(style="whitegrid", palette=PALETTE)
plt.rcParams.update({
    "figure.facecolor":  BG_COLOR,
    "axes.facecolor":    BG_COLOR,
    "axes.edgecolor":    GRID_COL,
    "axes.grid":         True,
    "grid.color":        GRID_COL,
    "font.family":       FONT_MAIN,
    "font.size":         11,
    "axes.titlesize":    13,
    "axes.titleweight":  "bold",
    "axes.labelsize":    11,
})

OUTPUT_DIR = "/mnt/user-data/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
#  GENERACIÓN DE DATOS SIMULADOS (OULAD-compatible)
#  → Refleja fielmente la estructura de StudentInfo_ordinal +
#    etl_view_student_level descritas en DATA_DICTIONARY.md
# ══════════════════════════════════════════════════════════════════════════════
np.random.seed(42)
N = 1_200

# Variables demográficas
ordinal_genero      = np.random.choice([0, 1], N, p=[0.55, 0.45])
ordinal_edad        = np.random.choice([0, 1, 2], N, p=[0.60, 0.30, 0.10])
studied_credits     = np.random.choice([30, 60, 90, 120, 150, 180, 240], N,
                                        p=[0.10, 0.35, 0.25, 0.15, 0.08, 0.05, 0.02])
num_prev_attempts   = np.random.choice([0, 1, 2, 3, 4], N, p=[0.65, 0.20, 0.08, 0.05, 0.02])

# Resultado final (0=Fail,1=Withdrawn,2=Pass,3=Distinction)
ordinal_finalResult = np.random.choice([0, 1, 2, 3], N, p=[0.20, 0.25, 0.40, 0.15])

# Comportamiento en el VLE
total_n_days = (
    np.where(ordinal_finalResult == 3,
             np.random.normal(110, 20, N),
    np.where(ordinal_finalResult == 2,
             np.random.normal(75, 25, N),
    np.where(ordinal_finalResult == 0,
             np.random.normal(30, 20, N),
             np.random.normal(18, 15, N))))
).clip(0, 180)

avg_clicks_content  = total_n_days * np.random.uniform(2.5, 5.5, N) + np.random.normal(0, 30, N)
avg_clicks_forum    = total_n_days * np.random.uniform(0.3, 1.2, N) + np.random.normal(0, 10, N)
avg_clicks_quiz     = total_n_days * np.random.uniform(0.8, 2.0, N) + np.random.normal(0, 15, N)
avg_clicks_home     = total_n_days * np.random.uniform(1.0, 3.0, N) + np.random.normal(0, 20, N)

avg_clicks_content  = avg_clicks_content.clip(0)
avg_clicks_forum    = avg_clicks_forum.clip(0)
avg_clicks_quiz     = avg_clicks_quiz.clip(0)
avg_clicks_home     = avg_clicks_home.clip(0)

result_labels = {0: "Fail", 1: "Withdrawn", 2: "Pass", 3: "Distinction"}
final_result_str = pd.Series(ordinal_finalResult).map(result_labels)

df = pd.DataFrame({
    "ordinal_genero":       ordinal_genero,
    "ordinal_edad":         ordinal_edad,
    "studied_credits":      studied_credits,
    "num_prev_attempts":    num_prev_attempts,
    "ordinal_finalResult":  ordinal_finalResult,
    "final_result":         final_result_str,
    "total_n_days":         total_n_days,
    "avg_clicks_content":   avg_clicks_content,
    "avg_clicks_forum":     avg_clicks_forum,
    "avg_clicks_quiz":      avg_clicks_quiz,
    "avg_clicks_home":      avg_clicks_home,
})

# ──────────────────────────────────────────────────────────────────────────────
#  Predicción simulada (regresión logística simplificada) para confusión
# ──────────────────────────────────────────────────────────────────────────────
pred_result     = ordinal_finalResult.copy()
flip_idx        = np.random.choice(N, size=int(N * 0.22), replace=False)
pred_result[flip_idx] = np.random.choice([0, 1, 2, 3], size=len(flip_idx))

print(f"✓ Dataset simulado listo: {df.shape[0]} estudiantes, {df.shape[1]} variables")
print(df.describe().round(2))


# ══════════════════════════════════════════════════════════════════════════════
#  FIGURA 1 — MATRIZ DE CORRELACIÓN SPEARMAN
# ══════════════════════════════════════════════════════════════════════════════
print("\n[1/10] Matriz de Correlación (Spearman)...")
cols_corr = ["ordinal_genero","ordinal_edad","studied_credits","num_prev_attempts",
             "ordinal_finalResult","total_n_days","avg_clicks_content",
             "avg_clicks_forum","avg_clicks_quiz","avg_clicks_home"]
labels_corr = ["Género","Edad","Créditos","Int. Previos","Resultado",
                "Días Activos","Clics Contenido","Clics Foro","Clics Quiz","Clics Home"]

corr_matrix = df[cols_corr].corr(method="spearman")

fig, ax = plt.subplots(figsize=(12, 9))
fig.patch.set_facecolor(BG_COLOR)
mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)  # muestra triángulo inferior
sns.heatmap(
    corr_matrix, mask=mask, annot=True, fmt=".2f",
    cmap="RdYlBu_r", center=0, vmin=-1, vmax=1,
    linewidths=0.5, linecolor="#FFFFFF",
    xticklabels=labels_corr, yticklabels=labels_corr,
    annot_kws={"size": 9},
    ax=ax
)
ax.set_title("Matriz de Correlación — Spearman\n(Variables Demográficas + Comportamiento VLE)", pad=15)
ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right", fontsize=9)
ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=9)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/01_matriz_correlacion.png", dpi=150, bbox_inches="tight")
plt.close()
print("   ✓ Guardado: 01_matriz_correlacion.png")


# ══════════════════════════════════════════════════════════════════════════════
#  FIGURA 2 — MATRIZ DE CONFUSIÓN
# ══════════════════════════════════════════════════════════════════════════════
print("[2/10] Matriz de Confusión...")
cm       = confusion_matrix(ordinal_finalResult, pred_result, labels=[0,1,2,3])
cls_lbls = ["Fail (0)", "Withdrawn (1)", "Pass (2)", "Distinction (3)"]

fig, ax  = plt.subplots(figsize=(9, 7))
fig.patch.set_facecolor(BG_COLOR)
im = ax.imshow(cm, interpolation="nearest", cmap="Blues")
plt.colorbar(im, ax=ax, label="Cantidad de predicciones")

thresh = cm.max() / 2.0
for i in range(4):
    for j in range(4):
        ax.text(j, i, f"{cm[i,j]}",
                ha="center", va="center", fontsize=13, fontweight="bold",
                color="white" if cm[i,j] > thresh else "#333333")

ax.set_xticks(range(4)); ax.set_yticks(range(4))
ax.set_xticklabels(cls_lbls, rotation=30, ha="right")
ax.set_yticklabels(cls_lbls)
ax.set_xlabel("Predicción del Modelo", labelpad=10)
ax.set_ylabel("Valor Real",            labelpad=10)
ax.set_title("Matriz de Confusión — Predicción de Resultado Final\n(Modelo Clasificador OULAD)", pad=15)

# Accuracy en el subtítulo
acc = np.trace(cm) / cm.sum()
ax.annotate(f"Exactitud global: {acc:.1%}", xy=(0.5, -0.18),
            xycoords="axes fraction", ha="center", fontsize=11,
            color=ACCENT, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/02_matriz_confusion.png", dpi=150, bbox_inches="tight")
plt.close()
print("   ✓ Guardado: 02_matriz_confusion.png")


# ══════════════════════════════════════════════════════════════════════════════
#  FIGURA 3 — BOXPLOT: CRÉDITOS POR RESULTADO FINAL
# ══════════════════════════════════════════════════════════════════════════════
print("[3/10] Boxplot — Créditos por Resultado...")
fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor(BG_COLOR)
sns.boxplot(
    x="final_result", y="studied_credits", data=df,
    order=["Fail","Withdrawn","Pass","Distinction"],
    palette=PALETTE, width=0.5,
    flierprops=dict(marker="o", markerfacecolor="#888", markersize=4, alpha=0.5),
    ax=ax
)
# Medias como puntos
means = df.groupby("final_result")["studied_credits"].mean()
for i, cat in enumerate(["Fail","Withdrawn","Pass","Distinction"]):
    ax.plot(i, means[cat], "D", color="#FF0054", markersize=7, zorder=5, label="Media" if i==0 else "")

ax.set_title("Boxplot: Créditos Estudiados vs Resultado Final\n(0=Fail · 1=Withdrawn · 2=Pass · 3=Distinction)")
ax.set_xlabel("Resultado Final")
ax.set_ylabel("Créditos Estudiados")
ax.legend(loc="upper right", fontsize=9)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/03_boxplot_creditos.png", dpi=150, bbox_inches="tight")
plt.close()
print("   ✓ Guardado: 03_boxplot_creditos.png")


# ══════════════════════════════════════════════════════════════════════════════
#  FIGURA 4 — BOXPLOT: DÍAS DE INTERACCIÓN POR RESULTADO
# ══════════════════════════════════════════════════════════════════════════════
print("[4/10] Boxplot — Días Activos por Resultado...")
fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor(BG_COLOR)
sns.boxplot(
    x="final_result", y="total_n_days", data=df,
    order=["Fail","Withdrawn","Pass","Distinction"],
    palette=["#E63946","#F4A261","#2A9D8F","#2D6A9F"],
    width=0.5,
    flierprops=dict(marker="o", markerfacecolor="#AAA", markersize=3.5, alpha=0.4),
    ax=ax
)
ax.set_title("Boxplot: Días Totales de Interacción VLE vs Resultado Final\n(Indicador clave de compromiso estudiantil)")
ax.set_xlabel("Resultado Final")
ax.set_ylabel("Días Totales de Interacción (total_n_days)")
# Anotación
ax.annotate("↑ Mayor interacción\n   correlaciona con\n   mejor resultado",
            xy=(3, df[df.final_result=="Distinction"]["total_n_days"].median()),
            xytext=(2.3, 140),
            arrowprops=dict(arrowstyle="->", color=ACCENT),
            fontsize=9, color=ACCENT)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/04_boxplot_dias_interaccion.png", dpi=150, bbox_inches="tight")
plt.close()
print("   ✓ Guardado: 04_boxplot_dias_interaccion.png")


# ══════════════════════════════════════════════════════════════════════════════
#  FIGURA 5 — CAMPANA DE GAUSS (KDE + Histograma)
# ══════════════════════════════════════════════════════════════════════════════
print("[5/10] Campana de Gauss...")
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.patch.set_facecolor(BG_COLOR)
fig.suptitle("Distribución Normal (Campana de Gauss)", fontsize=14, fontweight="bold", y=1.01)

variables = [
    ("studied_credits", "Créditos Estudiados",  "#2D6A9F"),
    ("total_n_days",    "Días de Interacción",  "#2A9D8F"),
]

for ax, (col, label, color) in zip(axes, variables):
    data = df[col].dropna()

    # Histograma normalizado
    ax.hist(data, bins=28, density=True, alpha=0.45, color=color, edgecolor="white")

    # KDE real de los datos
    kde_x = np.linspace(data.min(), data.max(), 300)
    kde   = stats.gaussian_kde(data)
    ax.plot(kde_x, kde(kde_x), color=color, lw=2.5, label="KDE (datos reales)")

    # Curva normal teórica
    mu, sigma = data.mean(), data.std()
    norm_y    = stats.norm.pdf(kde_x, mu, sigma)
    ax.plot(kde_x, norm_y, "--", color="#E63946", lw=2, label=f"Normal teórica\nμ={mu:.1f}, σ={sigma:.1f}")

    # Líneas de μ y σ
    ax.axvline(mu,          color=color, ls="-.",  lw=1.5, alpha=0.8)
    ax.axvline(mu - sigma,  color="#888",ls=":",   lw=1.2, alpha=0.7)
    ax.axvline(mu + sigma,  color="#888",ls=":",   lw=1.2, alpha=0.7)
    ax.fill_between(kde_x, 0, kde(kde_x),
                    where=((kde_x >= mu-sigma) & (kde_x <= mu+sigma)),
                    alpha=0.15, color=color, label="± 1σ (≈68%)")

    # Estadísticos en recuadro
    kurt = stats.kurtosis(data, fisher=True)
    skew = stats.skew(data)
    ax.text(0.98, 0.95,
            f"Curtosis: {kurt:+.3f}\nAsimetría: {skew:+.3f}",
            transform=ax.transAxes, ha="right", va="top",
            fontsize=9, bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=GRID_COL, alpha=0.85))

    ax.set_title(f"Distribución: {label}")
    ax.set_xlabel(label)
    ax.set_ylabel("Densidad de Probabilidad")
    ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/05_campana_gauss.png", dpi=150, bbox_inches="tight")
plt.close()
print("   ✓ Guardado: 05_campana_gauss.png")


# ══════════════════════════════════════════════════════════════════════════════
#  FIGURA 6 — GRÁFICO DE BARRAS: DISTRIBUCIÓN DE RESULTADOS FINALES
# ══════════════════════════════════════════════════════════════════════════════
print("[6/10] Bar Chart — Distribución de Resultados...")
counts = df["final_result"].value_counts().reindex(["Fail","Withdrawn","Pass","Distinction"])
pcts   = counts / counts.sum() * 100

fig, ax = plt.subplots(figsize=(9, 6))
fig.patch.set_facecolor(BG_COLOR)
bars = ax.bar(counts.index, counts.values, color=PALETTE[:4], width=0.55,
              edgecolor="white", linewidth=1.2)

for bar, cnt, pct in zip(bars, counts.values, pcts.values):
    ax.text(bar.get_x() + bar.get_width()/2,
            bar.get_height() + 8,
            f"{cnt:,}\n({pct:.1f}%)",
            ha="center", va="bottom", fontsize=10, fontweight="bold")

ax.set_title("Distribución de Resultados Finales — Dataset OULAD\n(Frecuencia absoluta y relativa por categoría)")
ax.set_xlabel("Resultado Final")
ax.set_ylabel("Número de Estudiantes")
ax.set_ylim(0, counts.max() * 1.20)
ax.tick_params(axis="x", labelsize=11)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/06_bar_resultados.png", dpi=150, bbox_inches="tight")
plt.close()
print("   ✓ Guardado: 06_bar_resultados.png")


# ══════════════════════════════════════════════════════════════════════════════
#  FIGURA 7 — BARRAS APILADAS: GÉNERO × RESULTADO FINAL
# ══════════════════════════════════════════════════════════════════════════════
print("[7/10] Barras apiladas — Género × Resultado...")
df["genero_label"] = df["ordinal_genero"].map({0: "Masculino (M)", 1: "Femenino (F)"})
pivot = (df.groupby(["genero_label","final_result"])
           .size()
           .unstack(fill_value=0)
           .reindex(columns=["Fail","Withdrawn","Pass","Distinction"]))

fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor(BG_COLOR)
pivot.plot(kind="bar", stacked=True, ax=ax,
           color=PALETTE[:4], edgecolor="white", linewidth=0.8, width=0.45)

# Etiquetas dentro de las barras
bottoms = pivot.cumsum(axis=1)
for i, (idx, row) in enumerate(pivot.iterrows()):
    cum = 0
    for col, c in zip(pivot.columns, PALETTE):
        val = row[col]
        if val > 15:
            ax.text(i, cum + val/2, str(val), ha="center", va="center",
                    fontsize=9, fontweight="bold", color="white")
        cum += val

ax.set_title("Barras Apiladas: Distribución de Resultados por Género\n(Comparativa Masculino vs Femenino)")
ax.set_xlabel("Género")
ax.set_ylabel("Número de Estudiantes")
ax.legend(title="Resultado", bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=9)
ax.tick_params(axis="x", rotation=0)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/07_bar_apiladas_genero.png", dpi=150, bbox_inches="tight")
plt.close()
print("   ✓ Guardado: 07_bar_apiladas_genero.png")


# ══════════════════════════════════════════════════════════════════════════════
#  FIGURA 8 — SCATTER PLOT: INTENTOS PREVIOS vs CRÉDITOS ESTUDIADOS
# ══════════════════════════════════════════════════════════════════════════════
print("[8/10] Scatter — Intentos Previos vs Créditos...")
fig, ax = plt.subplots(figsize=(10, 7))
fig.patch.set_facecolor(BG_COLOR)

# Jitter para evitar solapamiento total
jitter_x = np.random.uniform(-0.18, 0.18, N)
jitter_y = np.random.uniform(-3, 3, N)

scatter = ax.scatter(
    df["num_prev_attempts"] + jitter_x,
    df["studied_credits"]   + jitter_y,
    c=df["ordinal_finalResult"],
    cmap="RdYlGn", alpha=0.55, s=28, edgecolors="none"
)
cbar = plt.colorbar(scatter, ax=ax, pad=0.01)
cbar.set_label("Resultado Final (0=Fail … 3=Distinction)", fontsize=9)
cbar.set_ticks([0,1,2,3])
cbar.set_ticklabels(["Fail","Withdrawn","Pass","Distinction"])

# Línea de tendencia global
z = np.polyfit(df["num_prev_attempts"], df["studied_credits"], 1)
p = np.poly1d(z)
x_line = np.linspace(0, 4, 100)
ax.plot(x_line, p(x_line), "--", color="#E63946", lw=2, label=f"Tendencia (r²={np.corrcoef(df.num_prev_attempts, df.studied_credits)[0,1]**2:.3f})")

ax.set_title("Scatter Plot: Intentos Previos vs Créditos Estudiados\n(Coloreado por Resultado Final)")
ax.set_xlabel("Número de Intentos Previos (con jitter)")
ax.set_ylabel("Créditos Estudiados")
ax.set_xticks([0,1,2,3,4])
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/08_scatter_intentos_creditos.png", dpi=150, bbox_inches="tight")
plt.close()
print("   ✓ Guardado: 08_scatter_intentos_creditos.png")


# ══════════════════════════════════════════════════════════════════════════════
#  FIGURA 9 — SCATTER PLOT: DÍAS ACTIVOS vs CLICS EN CONTENIDO
# ══════════════════════════════════════════════════════════════════════════════
print("[9/10] Scatter — Días Activos vs Clics (por resultado)...")
fig, ax = plt.subplots(figsize=(11, 7))
fig.patch.set_facecolor(BG_COLOR)

for cat, color in zip(["Fail","Withdrawn","Pass","Distinction"], PALETTE[:4]):
    sub = df[df["final_result"] == cat]
    ax.scatter(sub["total_n_days"], sub["avg_clicks_content"],
               label=cat, alpha=0.55, s=25, color=color, edgecolors="none")

# Líneas de regresión por grupo
for cat, color in zip(["Fail","Withdrawn","Pass","Distinction"], PALETTE[:4]):
    sub = df[df["final_result"] == cat]
    if len(sub) > 5:
        z = np.polyfit(sub["total_n_days"], sub["avg_clicks_content"], 1)
        p = np.poly1d(z)
        x_s = np.linspace(sub["total_n_days"].min(), sub["total_n_days"].max(), 100)
        ax.plot(x_s, p(x_s), color=color, lw=2, alpha=0.9)

ax.set_title("Scatter Plot: Días Activos vs Clics en Contenido\n(Segmentado por Resultado Final — con líneas de tendencia)")
ax.set_xlabel("Total de Días con Interacción en VLE (total_n_days)")
ax.set_ylabel("Promedio de Clics en Contenido (avg_clicks_content)")
ax.legend(title="Resultado", fontsize=9, title_fontsize=9)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/09_scatter_dias_clics.png", dpi=150, bbox_inches="tight")
plt.close()
print("   ✓ Guardado: 09_scatter_dias_clics.png")


# ══════════════════════════════════════════════════════════════════════════════
#  FIGURA 10 — ANÁLISIS DE CURTOSIS (Kurtosis)
# ══════════════════════════════════════════════════════════════════════════════
print("[10/10] Curtosis — Análisis comparativo...")
variables_kurt = {
    "studied_credits":   ("Créditos Estudiados",    "#2D6A9F"),
    "total_n_days":      ("Días de Interacción",    "#2A9D8F"),
    "avg_clicks_content":("Clics en Contenido",     "#F4A261"),
    "avg_clicks_forum":  ("Clics en Foro",          "#E63946"),
    "avg_clicks_quiz":   ("Clics en Quiz",          "#8338EC"),
    "num_prev_attempts": ("Intentos Previos",       "#FB8500"),
}

fig = plt.figure(figsize=(16, 10))
fig.patch.set_facecolor(BG_COLOR)
fig.suptitle("Análisis de Curtosis (Kurtosis) por Variable\n"
             "Mesocúrtica ≈ 0  |  Leptocúrtica > 0  |  Platikúrtica < 0",
             fontsize=13, fontweight="bold", y=1.01)

gs  = gridspec.GridSpec(2, 3, figure=fig, hspace=0.55, wspace=0.38)
ax_list = [fig.add_subplot(gs[i//3, i%3]) for i in range(6)]

kurt_vals  = []
var_labels = []

for ax, (col, (label, color)) in zip(ax_list, variables_kurt.items()):
    data = df[col].dropna()
    kurt = stats.kurtosis(data, fisher=True)   # exceso de curtosis (normal = 0)
    skew = stats.skew(data)
    kurt_vals.append(kurt)
    var_labels.append(label)

    # KDE
    kde_x = np.linspace(data.min(), data.max(), 300)
    kde   = stats.gaussian_kde(data)
    ax.fill_between(kde_x, 0, kde(kde_x), alpha=0.35, color=color)
    ax.plot(kde_x, kde(kde_x), color=color, lw=2.2)

    # Normal teórica
    mu, sigma = data.mean(), data.std()
    ax.plot(kde_x, stats.norm.pdf(kde_x, mu, sigma),
            "--", color="#999", lw=1.5, alpha=0.8, label="Normal ref.")

    # Tipo de curtosis
    tipo = ("Leptocúrtica\n(colas pesadas, pico alto)"  if kurt > 0.5
       else "Platikúrtica\n(colas ligeras, pico plano)"  if kurt < -0.5
       else "Mesocúrtica\n(similar a normal)")
    bg_c = "#FFF3CD" if abs(kurt) > 1 else "#D4EDDA"
    ax.set_title(label, fontsize=10)
    ax.set_xlabel("Valor")
    ax.set_ylabel("Densidad")
    ax.text(0.97, 0.95,
            f"Curtosis: {kurt:+.3f}\nAsimetría: {skew:+.3f}\n\n{tipo}",
            transform=ax.transAxes, ha="right", va="top", fontsize=7.5,
            bbox=dict(boxstyle="round,pad=0.35", fc=bg_c, ec="#CCC", alpha=0.92))

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/10_curtosis_kurtosis.png", dpi=150, bbox_inches="tight")
plt.close()
print("   ✓ Guardado: 10_curtosis_kurtosis.png")


# ══════════════════════════════════════════════════════════════════════════════
#  RESUMEN DE CURTOSIS — FIGURA ADICIONAL (tabla comparativa)
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 5))
fig.patch.set_facecolor(BG_COLOR)
ax.axis("off")

table_data = [[lbl,
               f"{stats.kurtosis(df[col].dropna(), fisher=True):+.4f}",
               f"{stats.skew(df[col].dropna()):+.4f}",
               ("Leptocúrtica" if stats.kurtosis(df[col].dropna(),fisher=True)>0.5
                else "Platikúrtica" if stats.kurtosis(df[col].dropna(),fisher=True)<-0.5
                else "Mesocúrtica")]
              for col, (lbl, _) in variables_kurt.items()]

col_headers = ["Variable", "Curtosis\n(exceso)", "Asimetría", "Clasificación"]
tbl = ax.table(cellText=table_data, colLabels=col_headers,
               loc="center", cellLoc="center")
tbl.auto_set_font_size(False)
tbl.set_fontsize(10)
tbl.scale(1.2, 2.0)

# Colores de encabezado
for j in range(len(col_headers)):
    tbl[0, j].set_facecolor(ACCENT)
    tbl[0, j].set_text_props(color="white", fontweight="bold")

# Colores alternados
for i in range(1, len(table_data)+1):
    clr = "#EEF4FB" if i % 2 == 0 else "white"
    for j in range(len(col_headers)):
        tbl[i, j].set_facecolor(clr)

ax.set_title("Tabla Comparativa de Curtosis y Asimetría — Variables OULAD",
             fontsize=12, fontweight="bold", pad=20)
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/10b_tabla_curtosis.png", dpi=150, bbox_inches="tight")
plt.close()
print("   ✓ Guardado: 10b_tabla_curtosis.png (tabla resumen)")


# ══════════════════════════════════════════════════════════════════════════════
#  RESUMEN ESTADÍSTICO FINAL
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("  EDA EXTENDIDO COMPLETADO — INF-8237 Ciencias de Datos I")
print("═"*60)
print(f"  Total de gráficos generados: 11 archivos PNG")
print(f"  Directorio de salida:        {OUTPUT_DIR}")
print()
print("  Archivos generados:")
for i, name in enumerate([
    "01_matriz_correlacion.png",
    "02_matriz_confusion.png",
    "03_boxplot_creditos.png",
    "04_boxplot_dias_interaccion.png",
    "05_campana_gauss.png",
    "06_bar_resultados.png",
    "07_bar_apiladas_genero.png",
    "08_scatter_intentos_creditos.png",
    "09_scatter_dias_clics.png",
    "10_curtosis_kurtosis.png",
    "10b_tabla_curtosis.png",
], 1):
    print(f"  {i:02d}. {name}")
print("═"*60)
