"""Test end-to-end del sistema de recomendación de microcredenciales."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time

# Documento de prueba: un syllabus de curso de análisis de datos
TEST_DOCUMENT = """
Programa del Curso: Análisis de Datos para la Toma de Decisiones

Universidad Iberoamericana - Departamento de Ingeniería Industrial

Descripción del Curso:
Este curso introduce a los estudiantes en las técnicas fundamentales del análisis de datos
aplicado a la toma de decisiones empresariales. Se cubren temas como estadística descriptiva,
visualización de datos, análisis predictivo y machine learning básico.

Objetivos de Aprendizaje:
1. Comprender los fundamentos de la ciencia de datos y su aplicación en contextos empresariales
2. Dominar herramientas de análisis estadístico como Python, R y Excel
3. Aplicar técnicas de visualización de datos usando Tableau y Power BI
4. Desarrollar modelos predictivos básicos utilizando regresión y clasificación
5. Interpretar resultados de análisis para la toma de decisiones estratégicas

Contenido Temático:
- Módulo 1: Introducción a la ciencia de datos y Big Data
- Módulo 2: Estadística descriptiva e inferencial
- Módulo 3: Programación en Python para análisis de datos (pandas, numpy, matplotlib)
- Módulo 4: Bases de datos SQL y NoSQL
- Módulo 5: Visualización de datos con Tableau y Power BI
- Módulo 6: Introducción al Machine Learning (regresión lineal, árboles de decisión)
- Módulo 7: Análisis predictivo y modelos de clasificación
- Módulo 8: Ética en el uso de datos y privacidad
- Módulo 9: Proyecto integrador: análisis de caso real empresarial

Competencias a Desarrollar:
- Pensamiento analítico y resolución de problemas basada en datos
- Manejo de herramientas tecnológicas para análisis
- Comunicación efectiva de resultados a stakeholders no técnicos
- Pensamiento crítico y ético en el manejo de información

Bibliografía:
- "Data Science for Business" - Foster Provost & Tom Fawcett
- "Python for Data Analysis" - Wes McKinney
- "Storytelling with Data" - Cole Nussbaumer Knaflic
"""

def run_test():
    print("=" * 60)
    print("TEST E2E: Sistema de Recomendación de Microcredenciales")
    print("=" * 60)

    # 1. Test document processor
    print("\n[1/7] Testing document processor...")
    from modules.document_processor import generate_summary
    summary = generate_summary(TEST_DOCUMENT)
    print(f"  ✓ Resumen generado: {len(summary)} chars")
    print(f"  Preview: {summary[:150]}...")

    # 2. Test catalog loader
    print("\n[2/7] Testing catalog loader...")
    t0 = time.time()
    from modules.catalog_loader import load_courses, load_specializations, get_catalog_stats
    courses_df = load_courses(max_hours=20, use_cache=False)
    t1 = time.time()
    stats = get_catalog_stats(courses_df)
    print(f"  ✓ Cursos cargados: {stats['total_courses']} en {t1-t0:.1f}s")
    print(f"  ✓ Dominios: {stats['domains']}")

    specs_df = load_specializations()
    print(f"  ✓ Especializaciones cargadas: {len(specs_df)}")

    # 3. Test competency extractor
    print("\n[3/7] Testing competency extractor...")
    from modules.competency_extractor import extract_competencies, competencies_to_text
    competencies = extract_competencies(TEST_DOCUMENT, n_competencies=12)
    print(f"  ✓ Competencias extraídas: {len(competencies)}")
    for c in competencies[:5]:
        print(f"    - {c['term']} (score: {c['score']}, tipo: {c['type']})")
    comp_text = competencies_to_text(competencies)
    print(f"  ✓ Texto de competencias: {len(comp_text)} chars")

    # 4. Test coursera matcher
    print("\n[4/7] Testing Coursera matcher...")
    t0 = time.time()
    from modules.coursera_matcher import CourseraMatcher, SpecializationMatcher
    matcher = CourseraMatcher()
    matcher.fit(courses_df)
    coursera_results = matcher.find_matches(TEST_DOCUMENT, top_n=10)
    t1 = time.time()
    print(f"  ✓ Resultados Coursera: {len(coursera_results)} en {t1-t0:.1f}s")
    for r in coursera_results[:3]:
        print(f"    - {r['nombre'][:60]} (score: {r['similitud']}, hrs: {r['horas']})")

    spec_matcher = SpecializationMatcher()
    spec_matcher.fit(specs_df)
    spec_results = spec_matcher.find_matches(TEST_DOCUMENT, top_n=5)
    print(f"  ✓ Especializaciones: {len(spec_results)}")
    for r in spec_results[:3]:
        print(f"    - {r['nombre'][:60]} (score: {r['similitud']})")

    # 5. Test external searcher
    print("\n[5/7] Testing external searcher...")
    from modules.external_searcher import search_external_certifications
    external = search_external_certifications(competencies, TEST_DOCUMENT, max_results=10)
    print(f"  ✓ Resultados externos: {len(external)}")
    for e in external[:3]:
        print(f"    - {e['nombre'][:60]} ({e.get('plataforma', '')})")

    # 6. Test report generator
    print("\n[6/7] Testing report generator...")
    from modules.report_generator import generate_report
    output_path = "/sessions/relaxed-elegant-bardeen/microcredentials_app/test_output.docx"
    generate_report(
        document_summary=summary,
        competencies=competencies,
        competencies_text=comp_text,
        coursera_courses=coursera_results,
        coursera_specializations=spec_results,
        external_results=external,
        output_path=output_path,
        teacher_name="Dr. Prueba Test"
    )
    file_size = os.path.getsize(output_path)
    print(f"  ✓ Documento generado: {output_path} ({file_size:,} bytes)")

    # 7. Resumen
    print("\n[7/7] Resumen del test...")
    print(f"  Documento de entrada: {len(TEST_DOCUMENT)} chars")
    print(f"  Competencias identificadas: {len(competencies)}")
    print(f"  Cursos Coursera recomendados: {len(coursera_results)}")
    print(f"  Especializaciones: {len(spec_results)}")
    print(f"  Opciones externas: {len(external)}")
    print(f"  Documento Word generado: {file_size:,} bytes")

    print("\n" + "=" * 60)
    print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
    print("=" * 60)

    # Cleanup
    if os.path.exists(output_path):
        os.remove(output_path)

    return True

if __name__ == "__main__":
    run_test()
