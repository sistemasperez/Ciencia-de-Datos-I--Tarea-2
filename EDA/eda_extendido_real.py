# -*- coding: utf-8 -*-
"""
================================================================================
  EDA EXTENDIDO — Open University Learning Analytics Dataset (OULAD)
  Caso Práctico 2 · INF-8237 Ciencias de Datos I (Módulo 2)
  Maestría en Ciencias de Datos e Inteligencia Artificial — UASD
  Grupo 9 · Facilitador: Dr. Silverio Del Orbe Abad

  Este script reproduce, sobre los DATOS REALES del OULAD, todo el análisis
  exploratorio del trabajo: ETL, estadística descriptiva e inferencial
  (correlación de Spearman, ANOVA con eta cuadrado, prueba t de Welch con
  d de Cohen, ji-cuadrado con V de Cramér), un clasificador Random Forest con
  su matriz de confusión, y los 11 gráficos del EDA.

  Uso:
      python eda_extendido_real.py --data ./MontarOULAD --out ./salidas

  Requisitos:
      pip install pandas numpy scipy scikit-learn matplotlib seaborn
================================================================================
"""

import argparse
import os
import json
import warnings

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────────────────────
#  ESTILO GLOBAL DE LAS FIGURAS
# ──────────────────────────────────────────────────────────────────────────────
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

PAL  = ["#E63946", "#F4A261", "#2A9D8F", "#2D6A9F"]   # Fail · Withdrawn · Pass · Distinction
ACC  = "#2D6A9F"
BG   = "#F8F9FA"
GRID = "#DEE2E6"
ORDER = ["Fail", "Withdrawn", "Pass", "Distinction"]

sns.set_theme(style="whitegrid")
plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": BG, "axes.edgecolor": GRID,
    "grid.color": GRID, "font.family": "DejaVu Sans", "font.size": 11,
    "axes.titlesize": 13, "axes.titleweight": "bold", "axes.labelsize": 11,
    "figure.dpi": 150,
})


# ══════════════════════════════════════════════════════════════════════════════
#  1. ETL — EXTRACCIÓN Y TRANSFORMACIÓN A NIVEL DE ESTUDIANTE
# ══════════════════════════════════════════════════════════════════════════════
def cargar_y_transformar(data_dir: str) -> pd.DataFrame:
    """Lee los CSV del OULAD, agrega los ~10.6 M de clics del VLE a nivel de
    estudiante-presentación, consolida las evaluaciones y une todo con la
    información demográfica. Devuelve el DataFrame analítico con ordinales."""

    # --- VLE: archivo grande (~430 MB), se leen tipos compactos ---
    dtype_vle = {"code_module": "category", "code_presentation": "category",
                 "id_student": "int32", "id_site": "int32",
                 "date": "int16", "sum_click": "int16"}
    vle = pd.read_csv(f"{data_dir}/studentVle.csv", dtype=dtype_vle)

    g = vle.groupby(["id_student", "code_module", "code_presentation"], observed=True)
    vle_agg = g.agg(total_clicks=("sum_click", "sum"),
                    active_days=("date", "nunique"),
                    vle_records=("sum_click", "size")).reset_index()

    # Clics por tipo de actividad (une id_site -> activity_type)
    sites = pd.read_csv(f"{data_dir}/vle.csv", usecols=["id_site", "activity_type"])
    act = (vle.merge(sites, on="id_site", how="left")
              .groupby(["id_student", "code_module", "code_presentation", "activity_type"],
                       observed=True)["sum_click"].sum().reset_index())
    act_piv = act.pivot_table(index=["id_student", "code_module", "code_presentation"],
                              columns="activity_type", values="sum_click",
                              fill_value=0).reset_index()
    act_piv.columns = [c if c in ("id_student", "code_module", "code_presentation")
                       else f"clk_{c}" for c in act_piv.columns]
    del vle

    # --- Evaluaciones: nota media por estudiante ---
    sa = pd.read_csv(f"{data_dir}/studentAssessment.csv")
    asmt = pd.read_csv(f"{data_dir}/assessments.csv")
    sa = sa.merge(asmt[["id_assessment", "code_module", "code_presentation"]],
                  on="id_assessment", how="left")
    sa["score"] = pd.to_numeric(sa["score"], errors="coerce")
    asg = sa.groupby(["id_student", "code_module", "code_presentation"]).agg(
        mean_score=("score", "mean"), n_assess=("score", "size")).reset_index()

    # --- Demografía + matrícula ---
    si = pd.read_csv(f"{data_dir}/studentInfo.csv")
    reg = pd.read_csv(f"{data_dir}/studentRegistration.csv")

    df = (si.merge(reg, on=["id_student", "code_module", "code_presentation"], how="left")
            .merge(vle_agg, on=["id_student", "code_module", "code_presentation"], how="left")
            .merge(act_piv, on=["id_student", "code_module", "code_presentation"], how="left")
            .merge(asg,     on=["id_student", "code_module", "code_presentation"], how="left"))

    # --- Limpieza de ausentes ---
    for c in ["total_clicks", "active_days", "vle_records"]:
        df[c] = df[c].fillna(0)
    clk_cols = [c for c in df.columns if c.startswith("clk_")]
    df[clk_cols] = df[clk_cols].fillna(0)

    return agregar_ordinales(df)


def agregar_ordinales(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte las categorías alfanuméricas a una escala ordinal numérica."""
    df["ord_final"]  = df["final_result"].map({"Fail": 0, "Withdrawn": 1, "Pass": 2, "Distinction": 3})
    df["ord_gender"] = df["gender"].map({"M": 0, "F": 1})
    df["ord_age"]    = df["age_band"].map({"0-35": 0, "35-55": 1, "55<=": 2})
    df["ord_edu"]    = df["highest_education"].map({
        "No Formal quals": 0, "Lower Than A Level": 1, "A Level or Equivalent": 2,
        "HE Qualification": 3, "Post Graduate Qualification": 4})
    df["ord_imd"]    = df["imd_band"].map({
        "0-10%": 0, "10-20": 1, "20-30%": 2, "30-40%": 3, "40-50%": 4,
        "50-60%": 5, "60-70%": 6, "70-80%": 7, "80-90%": 8, "90-100%": 9})
    df["ord_disab"]  = df["disability"].map({"N": 0, "Y": 1})
    df["passed"]     = df["final_result"].isin(["Pass", "Distinction"]).astype(int)
    return df


# ══════════════════════════════════════════════════════════════════════════════
#  2. ESTADÍSTICA DESCRIPTIVA E INFERENCIAL
# ══════════════════════════════════════════════════════════════════════════════
def _desc(s: pd.Series) -> dict:
    s = pd.Series(s).dropna()
    mean = float(s.mean())
    return dict(n=int(s.size), mean=round(mean, 2), median=round(float(s.median()), 2),
                std=round(float(s.std()), 2),
                cv=round(float(s.std() / mean * 100), 1) if mean else None,
                min=round(float(s.min()), 2), max=round(float(s.max()), 2),
                skew=round(float(stats.skew(s)), 3),
                kurt=round(float(stats.kurtosis(s, fisher=True)), 3))


def estadistica(df: pd.DataFrame) -> dict:
    R = {"N": int(len(df))}
    R["final_result_n"]   = {k: int(v) for k, v in df.final_result.value_counts().items()}
    R["final_result_pct"] = {k: round(v * 100, 1) for k, v in df.final_result.value_counts(normalize=True).items()}
    R["gender_pct"]       = {k: round(v * 100, 1) for k, v in df.gender.value_counts(normalize=True).items()}
    R["disability_pct"]   = {k: round(v * 100, 1) for k, v in df.disability.value_counts(normalize=True).items()}

    for v in ["total_clicks", "active_days", "mean_score", "studied_credits",
              "num_of_prev_attempts", "clk_forumng", "clk_quiz"]:
        R[f"desc_{v}"] = _desc(df[v])

    R["grp_clicks"] = {g: round(float(df[df.final_result == g].total_clicks.mean()), 1) for g in ORDER}
    R["grp_days"]   = {g: round(float(df[df.final_result == g].active_days.mean()), 1) for g in ORDER}
    R["grp_score"]  = {g: round(float(df[df.final_result == g].mean_score.dropna().mean()), 1) for g in ORDER}

    # Correlación de Spearman
    def corr(a, b):
        d = df[[a, b]].dropna()
        r, p = stats.spearmanr(d[a], d[b])
        return dict(r=round(float(r), 3), p=float(p), n=int(len(d)))
    R["corr_clicks_final"] = corr("total_clicks", "ord_final")
    R["corr_days_final"]   = corr("active_days", "ord_final")
    R["corr_score_final"]  = corr("mean_score", "ord_final")
    R["corr_clicks_score"] = corr("total_clicks", "mean_score")
    R["corr_prevatt_final"] = corr("num_of_prev_attempts", "ord_final")

    # ANOVA de un factor (+ eta cuadrado + Kruskal-Wallis)
    def anova(col, groupcol, groups):
        samples = [df.loc[df[groupcol] == g, col].dropna().values for g in groups]
        F, p = stats.f_oneway(*samples)
        allv = np.concatenate(samples); grand = allv.mean()
        ssb = sum(len(s) * (s.mean() - grand) ** 2 for s in samples)
        sst = ((allv - grand) ** 2).sum()
        H, pk = stats.kruskal(*samples)
        return dict(F=round(float(F), 2), p=float(p), eta2=round(float(ssb / sst), 4),
                    kruskal_H=round(float(H), 2), kruskal_p=float(pk),
                    group_means={g: round(float(s.mean()), 1) for g, s in zip(groups, samples)})
    R["anova_clicks_by_result"] = anova("total_clicks", "final_result", ORDER)
    R["anova_score_by_result"]  = anova("mean_score", "final_result", ORDER)

    # Prueba t de Welch (+ d de Cohen)
    def ttest(col, mask_a, mask_b):
        a = df.loc[mask_a, col].dropna(); b = df.loc[mask_b, col].dropna()
        t, p = stats.ttest_ind(a, b, equal_var=False)
        sp = np.sqrt(((len(a) - 1) * a.std() ** 2 + (len(b) - 1) * b.std() ** 2) / (len(a) + len(b) - 2))
        return dict(t=round(float(t), 2), p=float(p), cohen_d=round(float((a.mean() - b.mean()) / sp), 3),
                    mean_a=round(float(a.mean()), 1), mean_b=round(float(b.mean()), 1))
    R["t_clicks_pass_vs_fail"] = ttest("total_clicks", df.passed == 1, df.passed == 0)
    R["t_score_pass_vs_fail"]  = ttest("mean_score",   df.passed == 1, df.passed == 0)
    R["t_clicks_gender"]       = ttest("total_clicks", df.gender == "F", df.gender == "M")
    R["t_score_gender"]        = ttest("mean_score",   df.gender == "F", df.gender == "M")
    R["t_days_pass_vs_fail"]   = ttest("active_days",  df.passed == 1, df.passed == 0)

    # Ji-cuadrado (+ V de Cramér)
    def chi(a, b):
        ct = pd.crosstab(df[a], df[b])
        c2, p, dof, _ = stats.chi2_contingency(ct)
        v = np.sqrt(c2 / (ct.values.sum() * (min(ct.shape) - 1)))
        return dict(chi2=round(float(c2), 2), p=float(p), dof=int(dof), cramer_v=round(float(v), 3))
    R["chi_gender_result"] = chi("gender", "final_result")
    R["chi_disab_result"]  = chi("disability", "final_result")
    R["chi_age_result"]    = chi("age_band", "final_result")
    return R


# ══════════════════════════════════════════════════════════════════════════════
#  3. MODELO PREDICTIVO + MATRIZ DE CONFUSIÓN
# ══════════════════════════════════════════════════════════════════════════════
def modelo_confusion(df: pd.DataFrame) -> dict:
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import (confusion_matrix, accuracy_score, f1_score, roc_auc_score)

    feats = ["total_clicks", "active_days", "vle_records", "studied_credits",
             "num_of_prev_attempts", "ord_gender", "ord_age", "ord_edu", "ord_imd", "ord_disab",
             "clk_forumng", "clk_quiz", "clk_oucontent", "clk_homepage", "clk_resource",
             "clk_subpage", "clk_url"]
    d = df.copy()
    for c in ["ord_imd", "ord_edu"]:
        d[c] = d[c].fillna(d[c].median())
    X = d[feats]
    R = {}

    # 4 clases
    Xtr, Xte, ytr, yte = train_test_split(X, d["final_result"], test_size=.25,
                                          random_state=42, stratify=d["final_result"])
    rf = RandomForestClassifier(n_estimators=300, max_depth=18, min_samples_leaf=5,
                                random_state=42, n_jobs=-1, class_weight="balanced").fit(Xtr, ytr)
    pred = rf.predict(Xte)
    R["cm4_labels"] = ORDER
    R["cm4_matrix"] = confusion_matrix(yte, pred, labels=ORDER).tolist()
    R["cm4_accuracy"] = round(float(accuracy_score(yte, pred)), 3)
    R["cm4_macro_f1"] = round(float(f1_score(yte, pred, average="macro")), 3)

    # Binario aprobado / no aprobado
    Xtr, Xte, ytr, yte = train_test_split(X, d["passed"], test_size=.25,
                                          random_state=42, stratify=d["passed"])
    rfb = RandomForestClassifier(n_estimators=300, max_depth=16, min_samples_leaf=5,
                                 random_state=42, n_jobs=-1, class_weight="balanced").fit(Xtr, ytr)
    predb = rfb.predict(Xte); proba = rfb.predict_proba(Xte)[:, 1]
    R["cmbin_labels"] = ["No aprobado", "Aprobado"]
    R["cmbin_matrix"] = confusion_matrix(yte, predb).tolist()
    R["cmbin_accuracy"] = round(float(accuracy_score(yte, predb)), 3)
    R["cmbin_f1"] = round(float(f1_score(yte, predb)), 3)
    R["cmbin_auc"] = round(float(roc_auc_score(yte, proba)), 3)
    R["feat_importance"] = sorted([(f, round(float(v), 4)) for f, v in zip(feats, rfb.feature_importances_)],
                                  key=lambda x: -x[1])
    return R


# ══════════════════════════════════════════════════════════════════════════════
#  4. GRÁFICOS DEL EDA (11 figuras)
# ══════════════════════════════════════════════════════════════════════════════
def generar_graficos(df: pd.DataFrame, R: dict, out: str):
    os.makedirs(out, exist_ok=True)

    def save(name):
        plt.tight_layout(); plt.savefig(f"{out}/{name}", bbox_inches="tight"); plt.close()

    # 01 — Matriz de correlación (Spearman)
    cv = ["ord_final", "total_clicks", "active_days", "mean_score", "studied_credits",
          "num_of_prev_attempts", "ord_edu", "ord_imd", "ord_age", "ord_gender", "ord_disab"]
    lc = ["Resultado", "Clics tot.", "Días act.", "Nota med.", "Créditos", "Int. prev.",
          "Educación", "IMD", "Edad", "Género", "Discap."]
    fig, ax = plt.subplots(figsize=(11, 8.5)); fig.patch.set_facecolor(BG)
    mask = np.triu(np.ones_like(df[cv].corr(method="spearman"), dtype=bool), k=1)
    sns.heatmap(df[cv].corr(method="spearman"), mask=mask, annot=True, fmt=".2f", cmap="RdYlBu_r",
                center=0, vmin=-1, vmax=1, linewidths=.5, linecolor="white",
                xticklabels=lc, yticklabels=lc, annot_kws={"size": 9}, ax=ax,
                cbar_kws={"label": "ρ de Spearman"})
    ax.set_title("Matriz de correlación de Spearman\n(variables demográficas, compromiso y desempeño)", pad=14)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=40, ha="right", fontsize=9)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=9)
    save("01_correlacion.png")

    # 02 — Distribución de resultados (barras)
    cnts = df.final_result.value_counts().reindex(ORDER); pct = cnts / cnts.sum() * 100
    fig, ax = plt.subplots(figsize=(9, 5.5)); fig.patch.set_facecolor(BG)
    bars = ax.bar(ORDER, cnts.values, color=PAL, width=.6, edgecolor="white", linewidth=1.2)
    for bar, c, p in zip(bars, cnts.values, pct.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 120,
                f"{c:,}\n({p:.1f}%)", ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.set_title("Distribución de resultados finales — OULAD real (N = 32,593)")
    ax.set_xlabel("Resultado final"); ax.set_ylabel("Número de estudiantes")
    ax.set_ylim(0, cnts.max() * 1.18); save("02_barras_resultados.png")

    # 03 — Boxplot: días activos por resultado
    fig, ax = plt.subplots(figsize=(9.5, 6)); fig.patch.set_facecolor(BG)
    sns.boxplot(x="final_result", y="active_days", data=df, order=ORDER, palette=PAL, width=.55,
                flierprops=dict(marker="o", markerfacecolor="#999", markersize=3, alpha=.3), ax=ax)
    m = df.groupby("final_result")["active_days"].mean()
    for i, c in enumerate(ORDER):
        ax.plot(i, m[c], "D", color="#111", markersize=7, zorder=5, label="Media" if i == 0 else "")
    ax.set_title("Días activos en el VLE según resultado final (datos reales)")
    ax.set_xlabel("Resultado final"); ax.set_ylabel("Días activos (active_days)"); ax.legend()
    save("03_boxplot_dias.png")

    # 04 — Boxplot: créditos por resultado
    fig, ax = plt.subplots(figsize=(9.5, 6)); fig.patch.set_facecolor(BG)
    sns.boxplot(x="final_result", y="studied_credits", data=df, order=ORDER, palette=PAL, width=.55,
                flierprops=dict(marker="o", markerfacecolor="#999", markersize=3, alpha=.3), ax=ax)
    ax.set_ylim(0, 300); ax.set_title("Créditos estudiados según resultado final")
    ax.set_xlabel("Resultado final"); ax.set_ylabel("Créditos estudiados"); save("04_boxplot_creditos.png")

    # 05 — Campana de Gauss (KDE + normal teórica)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5)); fig.patch.set_facecolor(BG)
    fig.suptitle("Distribuciones y campana de Gauss — datos OULAD reales", fontsize=13, fontweight="bold", y=1.02)
    for ax, (col, name, color) in zip(axes, [("mean_score", "Nota media", "#2D6A9F"),
                                             ("total_clicks", "Clics totales", "#2A9D8F")]):
        d = df[col].dropna()
        ax.hist(d, bins=40, density=True, alpha=.45, color=color, edgecolor="white")
        xx = np.linspace(d.min(), d.max(), 300)
        ax.plot(xx, stats.gaussian_kde(d)(xx), color=color, lw=2.5, label="KDE (real)")
        mu, sg = d.mean(), d.std()
        ax.plot(xx, stats.norm.pdf(xx, mu, sg), "--", color="#E63946", lw=2,
                label=f"Normal teórica\nμ={mu:.1f}, σ={sg:.1f}")
        ax.text(.97, .95, f"Curtosis: {stats.kurtosis(d, fisher=True):+.2f}\nAsimetría: {stats.skew(d):+.2f}",
                transform=ax.transAxes, ha="right", va="top", fontsize=9.5,
                bbox=dict(boxstyle="round,pad=.4", fc="white", ec=GRID, alpha=.9))
        ax.set_title(name); ax.set_xlabel(name); ax.set_ylabel("Densidad"); ax.legend(fontsize=8)
    save("05_campana_gauss.png")

    # 06 — ANOVA: clics por resultado (medias + IC 95%)
    fig, ax = plt.subplots(figsize=(9.5, 6)); fig.patch.set_facecolor(BG)
    means = [df[df.final_result == g].total_clicks.mean() for g in ORDER]
    sems = [df[df.final_result == g].total_clicks.sem() * 1.96 for g in ORDER]
    bars = ax.bar(ORDER, means, yerr=sems, capsize=6, color=PAL, edgecolor="white",
                  linewidth=1.2, error_kw=dict(ecolor="#333", lw=1.5))
    for bar, mn in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 40, f"{mn:,.0f}",
                ha="center", va="bottom", fontsize=10, fontweight="bold")
    a = R["anova_clicks_by_result"]
    ax.set_title(f"Clics totales por resultado final\nF(3, {R['N']-4:,}) = {a['F']:,.0f}; "
                 f"p < .001; η² = {a['eta2']:.3f} (efecto grande)")
    ax.set_xlabel("Resultado final"); ax.set_ylabel("Clics totales (media ± IC 95%)")
    save("06_anova_clics.png")

    # 07 — Prueba t: aprobados vs no aprobados (violín)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5)); fig.patch.set_facecolor(BG)
    fig.suptitle("Prueba t: aprobados vs. no aprobados (datos reales)", fontsize=13, fontweight="bold", y=1.02)
    dd = df.copy(); dd["grp"] = np.where(dd.passed == 1, "Aprobados", "No aprobados")
    for ax, (col, name, tk) in zip(axes, [("total_clicks", "Clics totales", "t_clicks_pass_vs_fail"),
                                          ("active_days", "Días activos", "t_days_pass_vs_fail")]):
        sns.violinplot(x="grp", y=col, data=dd, order=["No aprobados", "Aprobados"],
                       palette=["#E63946", "#2D6A9F"], ax=ax, cut=0)
        if col == "total_clicks":
            ax.set_ylim(0, 8000)
        t = R[tk]
        ax.set_title(f"{name}\nt = {t['t']:.1f}; p < .001; d de Cohen = {t['cohen_d']:.2f}", fontsize=11)
        ax.set_xlabel(""); ax.set_ylabel(name)
    save("07_ttest_violin.png")

    # 08 — Dispersión: días activos vs clics (por resultado)
    fig, ax = plt.subplots(figsize=(10, 6.5)); fig.patch.set_facecolor(BG)
    for cat, c in zip(ORDER, PAL):
        s = df[df.final_result == cat]
        ax.scatter(s.active_days, s.total_clicks, s=8, alpha=.25, color=c, label=cat, edgecolors="none")
    ax.set_ylim(0, 12000); ax.set_title("Dispersión: días activos vs. clics totales (por resultado final)")
    ax.set_xlabel("Días activos (active_days)"); ax.set_ylabel("Clics totales")
    lg = ax.legend(title="Resultado", markerscale=2)
    for lh in lg.legend_handles:
        lh.set_alpha(1)
    save("08_scatter_dias_clics.png")

    # 09 — Matrices de confusión (binaria + 4 clases)
    fig, axes = plt.subplots(1, 2, figsize=(14, 6)); fig.patch.set_facecolor(BG)
    fig.suptitle("Matrices de confusión — clasificador Random Forest (conjunto de prueba, 25%)",
                 fontsize=13, fontweight="bold", y=1.02)
    cmb = np.array(R["cmbin_matrix"]); ax = axes[0]; ax.imshow(cmb, cmap="Blues"); th = cmb.max() / 2
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"{cmb[i, j]:,}", ha="center", va="center", fontsize=14,
                    fontweight="bold", color="white" if cmb[i, j] > th else "#222")
    ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
    ax.set_xticklabels(R["cmbin_labels"]); ax.set_yticklabels(R["cmbin_labels"])
    ax.set_xlabel("Predicción"); ax.set_ylabel("Real")
    ax.set_title(f"Binario (Aprobado/No)\nExactitud {R['cmbin_accuracy']:.1%} · "
                 f"F1 {R['cmbin_f1']:.2f} · AUC {R['cmbin_auc']:.2f}", fontsize=11)
    cm4 = np.array(R["cm4_matrix"]); ax = axes[1]; ax.imshow(cm4, cmap="Blues"); th = cm4.max() / 2
    for i in range(4):
        for j in range(4):
            ax.text(j, i, f"{cm4[i, j]:,}", ha="center", va="center", fontsize=11,
                    fontweight="bold", color="white" if cm4[i, j] > th else "#222")
    ax.set_xticks(range(4)); ax.set_yticks(range(4))
    ax.set_xticklabels(R["cm4_labels"], rotation=25, ha="right"); ax.set_yticklabels(R["cm4_labels"])
    ax.set_xlabel("Predicción"); ax.set_ylabel("Real")
    ax.set_title(f"4 clases\nExactitud {R['cm4_accuracy']:.1%} · F1 macro {R['cm4_macro_f1']:.2f}", fontsize=11)
    save("09_matriz_confusion.png")

    # 10 — Importancia de variables
    fi = R["feat_importance"][:12]
    names = {"total_clicks": "Clics totales", "active_days": "Días activos", "vle_records": "Registros VLE",
             "clk_homepage": "Clics homepage", "clk_quiz": "Clics quiz", "clk_resource": "Clics resource",
             "clk_subpage": "Clics subpage", "clk_oucontent": "Clics oucontent", "clk_forumng": "Clics foro",
             "clk_url": "Clics url", "studied_credits": "Créditos", "num_of_prev_attempts": "Intentos prev.",
             "ord_imd": "IMD", "ord_edu": "Educación", "ord_age": "Edad", "ord_gender": "Género",
             "ord_disab": "Discapacidad"}
    fnames = [names.get(f, f) for f, _ in fi][::-1]; fvals = [v for _, v in fi][::-1]
    cols = ["#2D6A9F" if any(k in f for k in ("Clics", "Días", "Registros")) else "#F4A261" for f in fnames]
    fig, ax = plt.subplots(figsize=(9.5, 6.5)); fig.patch.set_facecolor(BG)
    ax.barh(fnames, fvals, color=cols, edgecolor="white")
    for i, v in enumerate(fvals):
        ax.text(v + .003, i, f"{v:.3f}", va="center", fontsize=9)
    ax.set_title("Importancia de variables (Random Forest)\nAzul = compromiso/VLE · Naranja = demográficas")
    ax.set_xlabel("Importancia (Gini)"); ax.set_xlim(0, max(fvals) * 1.15); save("10_importancia.png")

    # 11 — Curtosis y asimetría (tabla)
    kv = {"total_clicks": "Clics totales", "active_days": "Días activos", "mean_score": "Nota media",
          "studied_credits": "Créditos", "clk_forumng": "Clics foro", "clk_quiz": "Clics quiz",
          "num_of_prev_attempts": "Intentos prev."}
    rows = []
    for col, nm in kv.items():
        d = df[col].dropna(); k = stats.kurtosis(d, fisher=True); sk = stats.skew(d)
        tipo = "Leptocúrtica" if k > 0.5 else "Platicúrtica" if k < -0.5 else "Mesocúrtica"
        rows.append([nm, f"{k:+.3f}", f"{sk:+.3f}", tipo])
    fig, ax = plt.subplots(figsize=(9.5, 4.2)); fig.patch.set_facecolor(BG); ax.axis("off")
    tb = ax.table(cellText=rows, colLabels=["Variable", "Curtosis (exceso)", "Asimetría", "Clasificación"],
                  loc="center", cellLoc="center")
    tb.auto_set_font_size(False); tb.set_fontsize(10.5); tb.scale(1.15, 1.9)
    for j in range(4):
        tb[0, j].set_facecolor(ACC); tb[0, j].set_text_props(color="white", fontweight="bold")
    for i in range(1, len(rows) + 1):
        for j in range(4):
            tb[i, j].set_facecolor("#EEF4FB" if i % 2 == 0 else "white")
    ax.set_title("Curtosis y asimetría de variables clave — OULAD real", fontsize=12, fontweight="bold", pad=16)
    save("11_curtosis_tabla.png")


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    ap = argparse.ArgumentParser(description="EDA extendido del OULAD (datos reales).")
    ap.add_argument("--data", default="./MontarOULAD", help="Carpeta con los CSV del OULAD")
    ap.add_argument("--out",  default="./salidas",     help="Carpeta de salida (figuras + resultados)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    print("1/4  ETL — cargando y transformando los datos reales del OULAD…")
    df = cargar_y_transformar(a.data)
    df.to_csv(f"{a.out}/student_level.csv", index=False)
    print(f"     Dataset analítico: {df.shape[0]:,} estudiantes × {df.shape[1]} variables")

    print("2/4  Estadística descriptiva e inferencial…")
    R = estadistica(df)

    print("3/4  Modelo predictivo y matriz de confusión…")
    R.update(modelo_confusion(df))
    print(f"     Binario AUC = {R['cmbin_auc']:.3f} · Exactitud = {R['cmbin_accuracy']:.3f}")

    print("4/4  Generando los 11 gráficos del EDA…")
    generar_graficos(df, R, a.out)

    json.dump(R, open(f"{a.out}/resultados.json", "w"), indent=2, ensure_ascii=False, default=str)

    print("\n" + "=" * 64)
    print("  EDA EXTENDIDO COMPLETADO")
    print("=" * 64)
    print(f"  Resultados: {a.out}/resultados.json")
    print(f"  Dataset:    {a.out}/student_level.csv")
    print(f"  Figuras:    11 archivos PNG en {a.out}/")
    print("  Hallazgo principal: el compromiso (días activos, clics) es el")
    print(f"  predictor dominante del resultado (η² = {R['anova_clicks_by_result']['eta2']}, "
          f"d = {R['t_clicks_pass_vs_fail']['cohen_d']}).")

if __name__ == "__main__":
    main()
