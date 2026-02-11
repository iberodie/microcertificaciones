"""Módulo para extraer competencias/habilidades clave de un documento usando TF-IDF."""
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from config import SPANISH_STOP_WORDS, TOP_N_COMPETENCIES


def extract_competencies(document_text: str, n_competencies: int = None) -> list[dict]:
    """
    Extrae las competencias/habilidades clave de un documento.
    Retorna lista de dicts: [{"term": "...", "score": 0.xx, "type": "bigram|unigram"}, ...]
    """
    if n_competencies is None:
        n_competencies = TOP_N_COMPETENCIES

    if not document_text or len(document_text.strip()) < 20:
        return []

    # Vectorizador TF-IDF para el documento
    vectorizer = TfidfVectorizer(
        max_features=300,
        stop_words=SPANISH_STOP_WORDS,
        min_df=1,
        max_df=1.0,
        ngram_range=(1, 3),
        token_pattern=r'(?u)\b[a-záéíóúñü][a-záéíóúñü]+\b',
        lowercase=True,
        sublinear_tf=True
    )

    try:
        tfidf_matrix = vectorizer.fit_transform([document_text])
    except ValueError:
        return []

    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.toarray()[0]

    # Obtener top términos
    top_indices = np.argsort(scores)[::-1]

    competencies = []
    seen_roots = set()

    for idx in top_indices:
        if len(competencies) >= n_competencies:
            break

        term = feature_names[idx]
        score = scores[idx]

        if score <= 0:
            continue

        # Boost para términos en el encabezado (primeros 300 caracteres)
        if term in document_text[:300].lower():
            score *= 1.5

        # Evitar duplicados por raíz (ahora más flexible)
        root = term.split()[0][:10] if " " in term else term[:10]
        if root in seen_roots:
            continue
        seen_roots.add(root)

        # Filtrar términos muy genéricos o muy cortos
        if len(term) < 4:
            continue

        n_words = len(term.split())
        term_type = "trigram" if n_words == 3 else ("bigram" if n_words == 2 else "unigram")

        competencies.append({
            "term": term,
            "score": round(float(score), 4),
            "type": term_type
        })

    return competencies


def competencies_to_search_query(competencies: list[dict]) -> str:
    """Convierte las competencias extraídas en una query de búsqueda."""
    terms = [c["term"] for c in competencies[:8]]
    return " ".join(terms)


def competencies_to_text(competencies: list[dict]) -> str:
    """Genera texto descriptivo de las competencias para el reporte."""
    if not competencies:
        return "No se pudieron identificar competencias específicas del documento."

    lines = ["Con base en el análisis del documento proporcionado, se identificaron las siguientes competencias y áreas temáticas clave:\n"]

    for i, comp in enumerate(competencies, 1):
        term = comp["term"].title()
        score = comp["score"]
        relevance = "Alta" if score > 0.3 else ("Media" if score > 0.15 else "Moderada")
        lines.append(f"  {i}. {term} (relevancia: {relevance})")

    lines.append("\nEstas competencias fueron utilizadas como criterio de búsqueda para identificar microcredenciales relevantes tanto en el catálogo de Coursera como en plataformas externas.")
    return "\n".join(lines)
