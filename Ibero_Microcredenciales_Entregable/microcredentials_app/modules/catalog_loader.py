"""Módulo para cargar y filtrar el catálogo de Coursera desde el Excel."""
import os
import pickle
import pandas as pd
from config import (
    EXCEL_PATH, CACHE_PATH, SHEET_COURSES, SHEET_SPECIALIZATIONS,
    EXCEL_SKIPROWS, MAX_LEARNING_HOURS,
    COL_NAME, COL_PARTNER, COL_TYPE, COL_DIFFICULTY, COL_HOURS,
    COL_RATING, COL_URL, COL_DESCRIPTION, COL_SKILLS, COL_CORE_SKILLS,
    COL_DOMAIN, COL_SUBDOMAIN, COL_LANGUAGE, COL_SPECIALIZATION, COL_SPEC_URL,
    SCOL_NAME, SCOL_PARTNERS, SCOL_NUM_COURSES, SCOL_LANGUAGE,
    SCOL_DOMAIN, SCOL_SUBDOMAIN, SCOL_DESCRIPTION, SCOL_DIFFICULTY,
    SCOL_URL, SCOL_TYPE
)


def load_courses(max_hours: float = None, use_cache: bool = True) -> pd.DataFrame:
    """Carga cursos del catálogo Coursera filtrados por horas."""
    if max_hours is None:
        max_hours = MAX_LEARNING_HOURS

    cache_key = f"{CACHE_PATH}_{max_hours}.pkl"
    if use_cache and os.path.exists(cache_key):
        with open(cache_key, "rb") as f:
            return pickle.load(f)

    df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_COURSES, skiprows=EXCEL_SKIPROWS)

    # Filtrar por horas
    df[COL_HOURS] = pd.to_numeric(df[COL_HOURS], errors='coerce')
    df_filtered = df[df[COL_HOURS] <= max_hours].copy()

    # Limpiar NaN en columnas de texto
    text_cols = [COL_NAME, COL_DESCRIPTION, COL_SKILLS, COL_CORE_SKILLS,
                 COL_DOMAIN, COL_SUBDOMAIN, COL_PARTNER]
    for col in text_cols:
        if col in df_filtered.columns:
            df_filtered[col] = df_filtered[col].fillna("")

    # Crear texto combinado para matching
    df_filtered["combined_text"] = (
        df_filtered[COL_NAME].astype(str) + " " +
        df_filtered[COL_DESCRIPTION].astype(str) + " " +
        df_filtered[COL_SKILLS].astype(str) + " " +
        df_filtered[COL_CORE_SKILLS].astype(str)
    )

    # Cachear
    os.makedirs(os.path.dirname(cache_key), exist_ok=True)
    with open(cache_key, "wb") as f:
        pickle.dump(df_filtered, f)

    return df_filtered


def load_specializations() -> pd.DataFrame:
    """Carga especializaciones y certificados profesionales."""
    df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_SPECIALIZATIONS, skiprows=EXCEL_SKIPROWS)

    text_cols = [SCOL_NAME, SCOL_DESCRIPTION, SCOL_DOMAIN, SCOL_SUBDOMAIN, SCOL_PARTNERS]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].fillna("")

    df["combined_text"] = (
        df[SCOL_NAME].astype(str) + " " +
        df[SCOL_DESCRIPTION].astype(str)
    )

    return df


def get_catalog_stats(df: pd.DataFrame) -> dict:
    """Obtiene estadísticas del catálogo para mostrar en la UI."""
    return {
        "total_courses": len(df),
        "avg_hours": df[COL_HOURS].mean() if COL_HOURS in df.columns else 0,
        "domains": df[COL_DOMAIN].nunique() if COL_DOMAIN in df.columns else 0,
        "languages": df[COL_LANGUAGE].nunique() if COL_LANGUAGE in df.columns else 0,
    }
