"""Módulo para hacer matching entre el documento del docente y el catálogo de Coursera."""
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from config import (
    SPANISH_STOP_WORDS, MIN_SIMILARITY_THRESHOLD, TOP_N_COURSERA,
    COL_NAME, COL_PARTNER, COL_HOURS, COL_RATING, COL_URL,
    COL_DESCRIPTION, COL_SKILLS, COL_CORE_SKILLS, COL_DIFFICULTY,
    COL_DOMAIN, COL_SUBDOMAIN, COL_LANGUAGE,
    SCOL_NAME, SCOL_PARTNERS, SCOL_URL, SCOL_DESCRIPTION,
    SCOL_DIFFICULTY, SCOL_DOMAIN, SCOL_SUBDOMAIN, SCOL_TYPE, SCOL_NUM_COURSES
)


class CourseraMatcher:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words=SPANISH_STOP_WORDS,
            min_df=2,
            max_df=0.85,
            ngram_range=(1, 2),
            sublinear_tf=True,
            lowercase=True
        )
        self._fitted = False
        self._course_vectors = None
        self._courses_df = None

    def fit(self, courses_df: pd.DataFrame):
        """Ajusta el vectorizador con el catálogo de cursos."""
        self._courses_df = courses_df.reset_index(drop=True)
        texts = self._courses_df["combined_text"].fillna("").tolist()
        self._course_vectors = self.vectorizer.fit_transform(texts)
        self._fitted = True

    def find_matches(self, document_text: str, top_n: int = None,
                     threshold: float = None) -> list[dict]:
        """
        Encuentra los cursos más similares al documento del docente.
        Retorna lista de dicts con info del curso y score de similitud.
        """
        if not self._fitted:
            raise RuntimeError("Debe llamar fit() antes de find_matches()")

        if top_n is None:
            top_n = TOP_N_COURSERA
        if threshold is None:
            threshold = MIN_SIMILARITY_THRESHOLD

        doc_vector = self.vectorizer.transform([document_text])
        similarities = cosine_similarity(doc_vector, self._course_vectors)[0]

        top_indices = np.argsort(similarities)[::-1]
        results = []

        for idx in top_indices:
            if len(results) >= top_n:
                break
            score = similarities[idx]
            if score < threshold:
                break

            row = self._courses_df.iloc[idx]
            skills = str(row.get(COL_SKILLS, ""))
            core_skills = str(row.get(COL_CORE_SKILLS, ""))

            results.append({
                "nombre": str(row.get(COL_NAME, "")),
                "partner": str(row.get(COL_PARTNER, "")),
                "horas": row.get(COL_HOURS, 0),
                "rating": row.get(COL_RATING, 0),
                "nivel": str(row.get(COL_DIFFICULTY, "")),
                "url": str(row.get(COL_URL, "")),
                "descripcion": str(row.get(COL_DESCRIPTION, ""))[:300],
                "skills": skills,
                "core_skills": core_skills,
                "dominio": str(row.get(COL_DOMAIN, "")),
                "subdominio": str(row.get(COL_SUBDOMAIN, "")),
                "idioma": str(row.get(COL_LANGUAGE, "")),
                "similitud": round(float(score), 4),
                "justificacion": _generate_justification(document_text, row, score)
            })

        return results


class SpecializationMatcher:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=3000,
            stop_words=SPANISH_STOP_WORDS,
            min_df=1,
            max_df=0.9,
            ngram_range=(1, 2),
            sublinear_tf=True,
            lowercase=True
        )
        self._fitted = False
        self._vectors = None
        self._df = None

    def fit(self, spec_df: pd.DataFrame):
        self._df = spec_df.reset_index(drop=True)
        texts = self._df["combined_text"].fillna("").tolist()
        self._vectors = self.vectorizer.fit_transform(texts)
        self._fitted = True

    def find_matches(self, document_text: str, top_n: int = 5,
                     threshold: float = None) -> list[dict]:
        if not self._fitted:
            raise RuntimeError("Debe llamar fit() antes de find_matches()")
        if threshold is None:
            threshold = MIN_SIMILARITY_THRESHOLD

        doc_vector = self.vectorizer.transform([document_text])
        similarities = cosine_similarity(doc_vector, self._vectors)[0]

        top_indices = np.argsort(similarities)[::-1]
        results = []

        for idx in top_indices:
            if len(results) >= top_n:
                break
            score = similarities[idx]
            if score < threshold:
                break

            row = self._df.iloc[idx]
            results.append({
                "nombre": str(row.get(SCOL_NAME, "")),
                "partner": str(row.get(SCOL_PARTNERS, "")),
                "num_cursos": row.get(SCOL_NUM_COURSES, 0),
                "nivel": str(row.get(SCOL_DIFFICULTY, "")),
                "url": str(row.get(SCOL_URL, "")),
                "descripcion": str(row.get(SCOL_DESCRIPTION, ""))[:300],
                "dominio": str(row.get(SCOL_DOMAIN, "")),
                "subdominio": str(row.get(SCOL_SUBDOMAIN, "")),
                "tipo": str(row.get(SCOL_TYPE, "")),
                "similitud": round(float(score), 4),
                "justificacion": _generate_spec_justification(row, score)
            })

        return results


def _generate_justification(doc_text: str, course_row, score: float) -> str:
    """Genera justificación de por qué este curso es relevante."""
    skills = str(course_row.get(COL_SKILLS, ""))
    name = str(course_row.get(COL_NAME, ""))
    domain = str(course_row.get(COL_DOMAIN, ""))
    hours = course_row.get(COL_HOURS, 0)

    parts = []
    if score > 0.3:
        parts.append(f"Alta coincidencia temática con el documento analizado (score: {score:.2f}).")
    elif score > 0.15:
        parts.append(f"Coincidencia moderada con las competencias identificadas (score: {score:.2f}).")
    else:
        parts.append(f"Coincidencia relevante en el área temática (score: {score:.2f}).")

    if domain:
        parts.append(f"Pertenece al dominio de {domain}.")

    if skills:
        skill_list = [s.strip() for s in skills.split(",")[:5]]
        parts.append(f"Desarrolla habilidades en: {', '.join(skill_list)}.")

    try:
        h = float(hours)
        if h <= 5:
            parts.append(f"Curso corto ({h:.1f} horas), ideal para una microcredencial rápida.")
        elif h <= 10:
            parts.append(f"Duración moderada ({h:.1f} horas), completable en 1-2 semanas.")
        else:
            parts.append(f"Curso de {h:.1f} horas, completable en 2-4 semanas con dedicación parcial.")
    except (ValueError, TypeError):
        pass

    return " ".join(parts)


def _generate_spec_justification(row, score: float) -> str:
    """Genera justificación para especializaciones."""
    tipo = str(row.get(SCOL_TYPE, ""))
    domain = str(row.get(SCOL_DOMAIN, ""))
    num_courses = row.get(SCOL_NUM_COURSES, 0)

    parts = [f"Coincidencia temática (score: {score:.2f})."]
    if tipo:
        parts.append(f"Tipo: {tipo}.")
    if domain:
        parts.append(f"Dominio: {domain}.")
    if num_courses:
        parts.append(f"Compuesta por {num_courses} cursos.")

    return " ".join(parts)
