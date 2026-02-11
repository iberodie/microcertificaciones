"""Marco conceptual de microcredenciales para el documento de salida."""

FRAMEWORK_INTRO = """Las microcredenciales no certifican simplemente la asistencia a un curso; su función principal es validar y dar fe de resultados de aprendizaje específicos adquiridos tras una experiencia educativa breve."""

FRAMEWORK_SECTIONS = {
    "resultados_aprendizaje": {
        "titulo": "1. Resultados de Aprendizaje Específicos",
        "descripcion": """A diferencia de un título tradicional que certifica una formación general amplia, la microcredencial certifica una competencia granular. Según la definición de consenso de la Comisión Europea y la UNESCO, una microcredencial es el registro de los resultados de aprendizaje que un alumno ha adquirido, verificando lo que:
• Sabe (Conocimiento teórico).
• Comprende (Entendimiento conceptual).
• Puede hacer (Aplicación práctica de habilidades)."""
    },
    "competencias_evaluadas": {
        "titulo": "2. Competencias Evaluadas (No solo asistencia)",
        "descripcion": """Para que una microcredencial tenga valor, debe certificar que el aprendizaje ha sido evaluado rigurosamente. No basta con "estar presente".
• Validación de la competencia: Certifican que el alumno ha superado una evaluación basada en estándares transparentes y claramente definidos.
• Niveles de dominio:
  - Microcredencial de Conocimiento: Certifica que el alumno posee conocimientos fundamentales ("conciencia").
  - Microcredencial de Aplicación: Certifica que el alumno ha demostrado la capacidad de aplicar ese conocimiento en escenarios prácticos ("competencia" o "maestría")."""
    },
    "carga_trabajo": {
        "titulo": "3. Carga de Trabajo y Nivel",
        "descripcion": """Certifican el volumen de aprendizaje invertido para lograr esa competencia.
• Se expresa en horas de aprendizaje u horas nocionales.
• Pueden certificar créditos académicos (ECTS), típicamente entre 1 y 5 créditos, lo que permite que sean acumulables ("apilables") hacia títulos mayores.
• Certifican el nivel de cualificación alineado con marcos nacionales o internacionales."""
    },
    "habilidades_laborales": {
        "titulo": "4. Habilidades Laborales y Transversales",
        "descripcion": """Las microcredenciales son especialmente ágiles para certificar habilidades que el mercado laboral demanda:
• Habilidades técnicas/duras: Lenguajes de programación, análisis de datos, manejo de herramientas específicas.
• Habilidades blandas/transversales: Liderazgo, pensamiento crítico, resolución de problemas, trabajo en equipo."""
    },
    "experiencias_no_formales": {
        "titulo": "5. Experiencias No Formales e Informales",
        "descripcion": """Certifican aprendizajes que ocurren fuera del aula tradicional:
• Experiencia laboral o voluntariado.
• Actividades co-curriculares (como liderazgo estudiantil).
• Aprendizaje previo (RPL - Recognition of Prior Learning), transformando la experiencia vivida en un crédito académico formal."""
    }
}

FRAMEWORK_SUMMARY = """Una microcredencial certifica: "Esta persona ha demostrado, mediante evaluación, que domina una competencia específica y dedicó un número determinado de horas a aprenderla". Actúa como un documento verificable que garantiza la identidad del alumno, la autenticidad del emisor y la validez de la habilidad reclamada."""


def get_full_framework_text():
    """Retorna el texto completo del marco de microcredenciales."""
    parts = [FRAMEWORK_INTRO, ""]
    for section in FRAMEWORK_SECTIONS.values():
        parts.append(f"{section['titulo']}")
        parts.append(section['descripcion'])
        parts.append("")
    parts.append(FRAMEWORK_SUMMARY)
    return "\n".join(parts)
