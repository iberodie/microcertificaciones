"""
🎓 Recomendador de Microcredenciales
Universidad Iberoamericana — Ciudad de México

App Streamlit para recomendar microcredenciales a docentes
basándose en sus documentos de enseñanza.
"""
import sys
import os
import time
import hashlib
import hmac


# Asegurar que el directorio de la app esté en el path
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

import streamlit as st
import pandas as pd

from config import (
    EXCEL_PATH, OUTPUT_DIR, MAX_LEARNING_HOURS,
    UI_TITLE, UI_SUBTITLE, TOP_N_COURSERA, TOP_N_EXTERNAL, TOP_N_COMPETENCIES,
    COL_NAME, COL_HOURS, COL_RATING, COL_URL, COL_DOMAIN, COL_DIFFICULTY, COL_PARTNER
)
from modules.document_processor import extract_text, generate_summary
from modules.catalog_loader import load_courses, load_specializations, get_catalog_stats
from modules.competency_extractor import (
    extract_competencies, competencies_to_text, competencies_to_search_query
)
from modules.coursera_matcher import CourseraMatcher, SpecializationMatcher
from modules.external_searcher import search_external_certifications
from modules.report_generator import generate_report


# === Configuración de página ===
st.set_page_config(
    page_title="Recomendador de Microcredenciales — Ibero",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === Seguridad ===
def check_password():
    """Retorna True si el usuario ingresó la contraseña correcta."""
    if st.session_state.get("password_correct", False):
        return True

    # Estilos simples para login
    st.markdown(
        """
        <style>
        .stApp { background-color: #F6F6F5; }
        h1 { color: #ED1A37; font-family: 'Times New Roman', serif; text-align: center; }
        .stTextInput { width: 50%; margin: 0 auto; }
        div[data-testid="stVerticalBlock"] { text-align: center; }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("🔐 Acceso a Microcredenciales")
    st.write("Universidad Iberoamericana")

    password = st.text_input("Ingresa la contraseña", type="password")

    if st.button("Ingresar", type="primary"):
        expected_hash = st.secrets.get("APP_PASSWORD_HASH", "")
        if not expected_hash:
            st.error("Falta configurar APP_PASSWORD_HASH en Secrets.")
            st.stop()

        entered_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()

        if hmac.compare_digest(entered_hash, expected_hash):
            st.session_state.password_correct = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta")

    return False


if not check_password():
    st.stop()

# === CSS personalizado ===
# === CSS personalizado (Ibero Look & Feel) ===
st.markdown("""
<style>
    /* Tipografía y Colores Ibero */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Roboto:wght@300;400;700&display=swap');

    .stApp {
        background-color: #F6F6F5; /* Off-White */
    }
    
    h1, h2, h3, .main-title {
        color: #ED1A37 !important; /* Ibero Red */
        font-family: 'Playfair Display', 'Times New Roman', serif;
    }
    
    p, .stMarkdown, .subtitle {
        color: #000000;
        font-family: 'Roboto', sans-serif;
    }

    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        font-size: 1.2rem;
        color: #555;
        margin-top: 0;
        font-weight: 300;
        border-bottom: 3px solid #ED1A37;
        padding-bottom: 1rem;
        width: fit-content;
    }

    /* Botones */
    .stButton button {
        background-color: #ED1A37 !important;
        color: white !important;
        border-radius: 0px !important; /* Bordes cuadrados estilo minimalista */
        border: none;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        background-color: #B30020 !important;
    }

    /* Cards y Métricas */
    div[data-testid="metric-container"] {
        background-color: white;
        border-left: 5px solid #ED1A37;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Tags */
    .competency-tag {
        display: inline-block;
        background: white;
        color: #ED1A37;
        border: 1px solid #ED1A37;
        padding: 4px 12px;
        border-radius: 20px;
        margin: 4px;
        font-size: 0.85rem;
        font-weight: 500;
    }

    /* Footer Disclaimer */
    .disclaimer-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
        padding: 15px;
        margin-top: 30px;
        border-radius: 5px;
        font-size: 0.9rem;
        text-align: center;
    }
    
    .section-divider {
        border-top: 1px solid #ddd;
        margin: 30px 0;
    }
</style>
""", unsafe_allow_html=True)


# === Funciones de caché ===
@st.cache_data(show_spinner="Cargando catálogo de Coursera...")
def cached_load_courses(max_hours):
    return load_courses(max_hours=max_hours, use_cache=False)

@st.cache_data(show_spinner="Cargando especializaciones...")
def cached_load_specializations():
    return load_specializations()

@st.cache_resource(show_spinner="Preparando motor de búsqueda...")
def get_course_matcher(max_hours):
    df = cached_load_courses(max_hours)
    matcher = CourseraMatcher()
    matcher.fit(df)
    return matcher

@st.cache_resource(show_spinner="Preparando matcher de especializaciones...")
def get_spec_matcher():
    df = cached_load_specializations()
    matcher = SpecializationMatcher()
    matcher.fit(df)
    return matcher


# === Sidebar ===
with st.sidebar:
    st.markdown('<p class="main-title">🎓 Microcredenciales</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Universidad Iberoamericana</p>', unsafe_allow_html=True)
    st.markdown("---")

    # Subir documento
    st.subheader("📄 Documento del Docente")
    uploaded_file = st.file_uploader(
        "Sube un archivo TXT, PDF o DOCX",
        type=["txt", "pdf", "docx"],
        help="El documento será analizado para extraer competencias y recomendar microcredenciales."
    )

    st.markdown("---")

    # Configuración
    st.subheader("⚙️ Configuración")
    max_hours = st.slider(
        "Máximo de horas de aprendizaje",
        min_value=1, max_value=50, value=MAX_LEARNING_HOURS,
        help="Filtrar cursos con duración menor o igual a este valor."
    )

    n_coursera = st.slider(
        "Máx. resultados de Coursera",
        min_value=3, max_value=20, value=TOP_N_COURSERA
    )

    n_external = st.slider(
        "Máx. resultados externos",
        min_value=3, max_value=20, value=TOP_N_EXTERNAL
    )

    n_competencies = st.slider(
        "Núm. de competencias a extraer",
        min_value=5, max_value=20, value=TOP_N_COMPETENCIES
    )

    teacher_name = st.text_input(
        "Nombre del docente (opcional)",
        value="",
        placeholder="Ej: Dr. García López"
    )

    st.markdown("---")

    # Info del catálogo
    st.subheader("📊 Catálogo Coursera")
    try:
        courses_df = cached_load_courses(max_hours)
        stats = get_catalog_stats(courses_df)
        col1, col2 = st.columns(2)
        col1.metric("Cursos", f"{stats['total_courses']:,}")
        col2.metric("Dominios", stats['domains'])
        st.caption(f"Filtrado: ≤ {max_hours} horas de aprendizaje")
    except Exception as e:
        st.error(f"Error cargando catálogo: {e}")

    # Descargas y Transparencia
    st.markdown("---")
    st.subheader("📂 Fuentes de Datos")
    
    # Descargar Excel Maestro
    if os.path.exists(EXCEL_PATH):
        with open(EXCEL_PATH, "rb") as f:
            st.download_button(
                label="📥 Descargar Catálogo Excel",
                data=f.read(),
                file_name="Coursera_Enterprise_Catalog.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Base de datos completa de cursos de Coursera procesada por el sistema."
            )
    else:
        st.warning("Catálogo Excel no encontrado.")

    # Generar y Descargar Lista de Fuentes Externas
    from modules.external_searcher import DOMAIN_CERTIFICATIONS, PLATFORMS
    
    sources_text = "=== FUENTES DE DATOS EXTERNAS ===\n\n"
    sources_text += "Nota: Estas son las palabras clave y plataformas que el sistema utiliza para buscar recomendaciones fuera de Coursera. "
    sources_text += "Puedes usar estos términos para realizar búsquedas manuales.\n\n"
    
    sources_text += "--- PLATAFORMAS MONITOREADAS ---\n"
    for p in PLATFORMS:
        sources_text += f"- {p}\n"
        
    sources_text += "\n--- CERTIFICACIONES POR DOMINIO ---\n"
    for domain, certs in DOMAIN_CERTIFICATIONS.items():
        sources_text += f"\nDOMINIO: {domain.upper()}\n"
        for cert in certs:
            sources_text += f"- {cert}\n"
            
    st.download_button(
        label="📥 Descargar Fuentes Externas",
        data=sources_text,
        file_name="Fuentes_Microcredenciales_Externas.txt",
        mime="text/plain",
        help="Lista de plataformas y certificaciones que el sistema busca externamente."
    )

    # Botón de análisis
    st.markdown("---")
    analyze_button = st.button(
        "🔍 Analizar y Recomendar",
        type="primary",
        use_container_width=True,
        disabled=uploaded_file is None
    )


# === Área principal ===
st.markdown('<p class="main-title">🎓 Recomendador de Microcredenciales</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Sistema de análisis y recomendación para docentes de la Universidad Iberoamericana</p>', unsafe_allow_html=True)
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

if uploaded_file is None:
    # Estado inicial
    st.info(
        "👈 **Sube un documento** en la barra lateral para comenzar.\n\n"
        "El sistema analizará el contenido del documento del docente para:\n"
        "1. Extraer competencias y habilidades clave\n"
        "2. Buscar microcredenciales relevantes en Coursera (≤ horas configuradas)\n"
        "3. Buscar microcertificaciones en plataformas externas y de industria\n"
        "4. Generar un documento Word con todas las recomendaciones"
    )

    # Explicación del sistema
    with st.expander("ℹ️ ¿Cómo funciona este sistema?"):
        st.markdown("""
        **Paso 1:** El docente sube un documento que describe su área de enseñanza,
        materiales, programa de curso o cualquier texto relevante a su perfil académico.

        **Paso 2:** El sistema utiliza procesamiento de lenguaje natural (TF-IDF)
        para extraer las competencias y habilidades clave del documento.

        **Paso 3:** Estas competencias se comparan contra el catálogo de Coursera
        Enterprise (18,000+ cursos) usando similitud coseno, filtrando por duración.

        **Paso 4:** También se buscan microcertificaciones en plataformas externas
        como edX, LinkedIn Learning, Google Certificates, y certificaciones de industria.

        **Paso 5:** Se genera un documento Word profesional con todas las recomendaciones,
        justificaciones y enlaces de acceso.
        """)

elif analyze_button:
    # === PASO 1: ANÁLISIS ===
    with st.spinner("📄 Procesando documento..."):
        try:
            # 1. Extraer texto
            text = extract_text(uploaded_file)
            if len(text.strip()) < 30:
                st.error("El documento parece estar vacío.")
                st.stop()
            
            # 2. Generar resumen
            summary = generate_summary(text)
            
            # 3. Extraer competencias iniciales
            raw_competencies = extract_competencies(text, n_competencies=n_competencies)
            
            # Guardar en sesión
            st.session_state.analysis_done = True
            st.session_state.doc_text = text
            st.session_state.doc_summary = summary
            # Guardar solo los términos para edición fácil
            st.session_state.detected_terms = [c['term'] for c in raw_competencies]
            # Mantener scores originales para referencia (mapeo)
            st.session_state.term_scores = {c['term']: c['score'] for c in raw_competencies}
            
            st.rerun()
            
        except Exception as e:
            st.error(f"Error en análisis: {e}")

# === LÓGICA DE ESTADOS ===

if st.session_state.get("analysis_done", False):
    st.markdown("---")
    st.subheader("🕵️ Validación de Competencias")
    st.info("Revisa las competencias detectadas. Puedes eliminar las que no sean relevantes y agregar nuevas manualmente.")
    
    col_val1, col_val2 = st.columns([2, 1])
    
    with col_val1:
        # Edición de competencias detectadas
        selected_terms = st.multiselect(
            "Competencias seleccionadas para búsqueda:",
            options=st.session_state.detected_terms + st.session_state.get("added_terms", []),
            default=st.session_state.detected_terms + st.session_state.get("added_terms", []),
            help="Elimina los términos que no desees incluir en la búsqueda."
        )
    
    with col_val2:
        # Agregar nuevos términos
        new_term = st.text_input("Agregar término manual:")
        if st.button("➕ Agregar"):
            if new_term and new_term not in st.session_state.get("added_terms", []) and new_term not in st.session_state.detected_terms:
                if "added_terms" not in st.session_state:
                    st.session_state.added_terms = []
                st.session_state.added_terms.append(new_term)
                st.success(f"Agregado: {new_term}")
                st.rerun()

    # Visualización de resumen
    with st.expander("Ver Resumen del Documento", expanded=False):
        st.write(st.session_state.doc_summary)

    st.markdown("---")
    
    # === PASO 2: GENERACIÓN DE RECOMENDACIONES ===
    if st.button("🚀 Generar Recomendaciones Finales", type="primary", use_container_width=True):
        
        # Reconstruir lista de objetos de competencia con scores
        final_competencies = []
        for term in selected_terms:
            # Si tiene score original, usarlo, si no (manual), asignar score alto (1.0)
            score = st.session_state.term_scores.get(term, 1.0)
            final_competencies.append({'term': term, 'score': score})
            
        if not final_competencies:
            st.error("Debes seleccionar al menos una competencia.")
            st.stop()

        progress = st.progress(0, text="Iniciando búsqueda con competencias validadas...")
        
        # Generar representación de texto de competencias para matching
        competencies_text_report = competencies_to_text(final_competencies)
        
        # Para el matching de Coursera, usamos el texto original del documento 
        # PERO ponderado o filtrado por las competencias seleccionadas?
        # Por simplicidad y eficacia actual, seguimos enviando el texto completo del documento al matcher de Coursera
        # ya que este usa TF-IDF sobre el texto completo. 
        # Sin embargo, para la búsqueda externa SÍ usamos las competencias explícitas.
        
        # NOTA: Si el usuario borró competencias clave, el matching de texto completo las seguirá encontrando.
        # Mejora futura: Filtrar el texto o boostear términos seleccionados.
        # Por ahora: Usamos el texto original para Coursera (enfoque holístico) y las keywords para Externos (enfoque específico)
        
        # Paso 4: Matching con Coursera
        progress.progress(20, text="🔍 Buscando en catálogo de Coursera...")
        try:
            course_matcher = get_course_matcher(max_hours)
            # Usamos el texto original
            coursera_results = course_matcher.find_matches(
                st.session_state.doc_text, top_n=n_coursera
            )
        except Exception as e:
            st.warning(f"Error en matching de cursos: {e}")
            coursera_results = []

        # Paso 5: Matching con especializaciones
        progress.progress(40, text="🔍 Buscando especializaciones...")
        try:
            spec_matcher = get_spec_matcher()
            spec_results = spec_matcher.find_matches(
                st.session_state.doc_text, top_n=5
            )
        except Exception as e:
            st.warning(f"Error en matching de especializaciones: {e}")
            spec_results = []

        # Paso 6: Búsqueda externa (USANDO LAS COMPETENCIAS VALIDADAS)
        progress.progress(60, text="🌐 Buscando microcertificaciones externas...")
        external_results = search_external_certifications(
            final_competencies, st.session_state.doc_text, max_results=n_external
        )

        # Paso 7: Generar reporte Word
        progress.progress(80, text="📝 Generando documento Word...")
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_filename = f"Recomendaciones_Microcredenciales_{timestamp}.docx"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        try:
            generate_report(
                document_summary=st.session_state.doc_summary,
                competencies=final_competencies,
                competencies_text=competencies_text_report,
                coursera_courses=coursera_results,
                coursera_specializations=spec_results,
                external_results=external_results,
                output_path=output_path,
                teacher_name=teacher_name if teacher_name else "Docente"
            )
        except Exception as e:
            st.error(f"Error generando reporte: {e}")
            st.stop()
        
        progress.progress(100, text="✅ ¡Análisis completado!")

        # === MOSTRAR RESULTADOS ===
        st.success("✅ Análisis completado exitosamente")

        # Botón de descarga
        with open(output_path, "rb") as f:
            st.download_button(
                label="📥 Descargar Documento Word",
                data=f.read(),
                file_name=output_filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
                use_container_width=True
            )

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        # Tab layout para resultados
        tab1, tab2, tab3, tab4 = st.tabs([
            "📝 Resumen y Competencias",
            "📚 Coursera",
            "🌐 Externas",
            "📄 Documento Completo"
        ])

        with tab1:
            st.subheader("Resumen del Documento")
            st.write(st.session_state.doc_summary)

            st.subheader("Competencias Utilizadas")
            # Mostrar como tags
            tags_html = ""
            for comp in final_competencies:
                tags_html += f'<span class="competency-tag">{comp["term"].title()}</span>'
            st.markdown(tags_html, unsafe_allow_html=True)

        with tab2:
            st.subheader(f"Cursos de Coursera ({len(coursera_results)} encontrados)")
            if coursera_results:
                for i, course in enumerate(coursera_results, 1):
                    with st.expander(
                        f"**{i}. {course['nombre']}** — "
                        f"{course.get('horas', 'N/A')} hrs | "
                        f"⭐ {course.get('rating', 'N/A')} | "
                        f"Score: {course['similitud']:.3f}"
                    ):
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Horas", f"{course.get('horas', 'N/A')}")
                        col2.metric("Rating", f"{course.get('rating', 'N/A')}")
                        col3.metric("Nivel", course.get("nivel", "N/A"))

                        st.write(f"**Partner:** {course.get('partner', '')}")
                        st.write(f"**Dominio:** {course.get('dominio', '')} — {course.get('subdominio', '')}")
                        st.write(f"**Skills:** {course.get('skills', '')[:200]}")
                        st.write(f"**URL:** {course.get('url', '')}")
                        st.info(f"💡 **Justificación:** {course.get('justificacion', '')}")
            else:
                 st.warning("No se encontraron cursos de Coursera.")

            # Especializaciones
            if spec_results:
                st.markdown("---")
                st.subheader(f"Especializaciones ({len(spec_results)} encontradas)")
                for i, spec in enumerate(spec_results, 1):
                    with st.expander(f"**{i}. {spec['nombre']}**"):
                        st.write(f"**URL:** {spec.get('url', '')}")
                        st.info(f"💡 **Justificación:** {spec.get('justificacion', '')}")

        with tab3:
            st.subheader(f"Microcertificaciones Externas ({len(external_results)} encontradas)")
            if external_results:
                for i, res in enumerate(external_results, 1):
                    with st.expander(f"**{i}. {res['nombre']}** ({res.get('plataforma', 'N/A')})"):
                        st.write(f"**URL:** {res.get('url', '')}")
                        st.info(f"💡 **Justificación:** {res.get('justificacion', '')}")
            else:
                st.warning("No se encontraron resultados externos.")

        with tab4:
             st.subheader("Documento Generado")
             st.write(f"📁 **Archivo:** `{output_filename}`")
        
        # Botón para reiniciar
        if st.button("🔄 Analizar otro documento"):
            for key in ["analysis_done", "doc_text", "doc_summary", "detected_terms", "added_terms", "term_scores"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

elif uploaded_file is not None and not st.session_state.get("analysis_done", False):
    # Archivo subido pero no se ha presionado analizar
    st.info("📄 Documento cargado. Presiona **🔍 Analizar y Recomendar** en la barra lateral para comenzar.")
    
    # Preview del texto
    with st.expander("👁️ Vista previa del documento"):
        try:
            preview_text = extract_text(uploaded_file)
            st.text_area("Contenido extraído", preview_text[:3000], height=300, disabled=True)
            st.caption(f"Total: {len(preview_text)} caracteres")
        except Exception as e:
            st.error(f"Error al leer: {e}")

# Footer Disclaimer
st.markdown("""
<div class="disclaimer-box">
    <strong>⚠️ Aviso de Responsabilidad:</strong><br>
    Este software utiliza algoritmos de inteligencia artificial para generar recomendaciones. 
    Aunque nos esforzamos por la precisión, el sistema puede cometer errores o sugerir contenidos no perfectamente alineados. 
    Se recomienda a los docentes verificar manualmente todas las recomendaciones y el contenido de los cursos sugeridos.
</div>
<div style="text-align: center; margin-top: 20px; font-size: 0.8rem; color: #888;">
    © 2026 Universidad Iberoamericana CDMX - Dirección de Innovación Educativa
</div>
""", unsafe_allow_html=True)
