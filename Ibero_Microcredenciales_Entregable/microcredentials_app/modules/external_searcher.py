"""Módulo para buscar microcertificaciones externas (fuera de Coursera)."""
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus


# Base de datos de plataformas conocidas con URLs de búsqueda
PLATFORMS = {
    "edX": {
        "search_url": "https://www.edx.org/search?q={query}&tab=program",
        "base_url": "https://www.edx.org",
        "tipo": "Plataforma educativa",
        "costo_tipico": "Gratis (auditar) / $50-$300 USD (certificado verificado)",
    },
    "LinkedIn Learning": {
        "search_url": "https://www.linkedin.com/learning/search?keywords={query}",
        "base_url": "https://www.linkedin.com/learning",
        "tipo": "Plataforma profesional",
        "costo_tipico": "$29.99/mes USD (suscripción)",
    },
    "Google Certificates": {
        "search_url": "https://grow.google/certificates/",
        "base_url": "https://grow.google/certificates",
        "tipo": "Certificación profesional",
        "costo_tipico": "$49/mes USD vía Coursera",
    },
    "FutureLearn": {
        "search_url": "https://www.futurelearn.com/search?q={query}&filter_type=microcredential",
        "base_url": "https://www.futurelearn.com",
        "tipo": "Plataforma de microcredenciales",
        "costo_tipico": "$500-$1,500 USD por microcredencial",
    },
    "Credly / Acclaim": {
        "search_url": "https://www.credly.com/organizations/search?q={query}",
        "base_url": "https://www.credly.com",
        "tipo": "Plataforma de badges digitales",
        "costo_tipico": "Varía según emisor",
    },
    "IEEE": {
        "search_url": "https://iln.ieee.org/public/searchresults.aspx?q={query}",
        "base_url": "https://iln.ieee.org",
        "tipo": "Certificación industria (ingeniería/tecnología)",
        "costo_tipico": "$100-$500 USD",
    },
    "PMI (Project Management Institute)": {
        "search_url": "https://www.pmi.org/certifications",
        "base_url": "https://www.pmi.org",
        "tipo": "Certificación industria (gestión de proyectos)",
        "costo_tipico": "$225-$555 USD (examen)",
    },
    "HubSpot Academy": {
        "search_url": "https://academy.hubspot.com/courses?q={query}",
        "base_url": "https://academy.hubspot.com",
        "tipo": "Certificación marketing/ventas",
        "costo_tipico": "Gratis",
    },
    "IBM SkillsBuild": {
        "search_url": "https://skillsbuild.org/learn?q={query}",
        "base_url": "https://skillsbuild.org",
        "tipo": "Plataforma tecnológica",
        "costo_tipico": "Gratis",
    },
    "Microsoft Learn": {
        "search_url": "https://learn.microsoft.com/en-us/search/?terms={query}&category=Credentials",
        "base_url": "https://learn.microsoft.com",
        "tipo": "Certificación tecnológica",
        "costo_tipico": "$80-$165 USD (examen)",
    },
    "AWS Training & Certification": {
        "search_url": "https://aws.amazon.com/training/learn-about/?nc2=sb_tr_la&trk=8287a443-b5f2-4036-bfcd-5885b6cd1faa&sc_channel=search",
        "base_url": "https://aws.amazon.com/training",
        "tipo": "Certificación cloud/tecnología",
        "costo_tipico": "$100-$300 USD (examen)",
    },
    "Salesforce Trailhead": {
        "search_url": "https://trailhead.salesforce.com/en/search?keywords={query}",
        "base_url": "https://trailhead.salesforce.com/",
        "tipo": "Plataforma de habilidades empresariales y CRM",
        "costo_tipico": "Gratis (aprendizaje) / $200-$400 USD (examen certificación)",
    },
    "Meta Blueprint": {
        "search_url": "https://www.facebook.com/business/learn/certification?q={query}",
        "base_url": "https://www.facebook.com/business/learn/certification",
        "tipo": "Certificación en Marketing Digital y Redes Sociales",
        "costo_tipico": "$99-$150 USD (examen)",
    },
    "Autodesk Education": {
        "search_url": "https://www.autodesk.com/certification/all-certifications?search={query}",
        "base_url": "https://www.autodesk.com/certification",
        "tipo": "Certificación en Diseño, Ingeniería y Arquitectura",
        "costo_tipico": "$150-$250 USD (examen)",
    },
    "Cisco Networking Academy": {
        "search_url": "https://www.netacad.com/courses?q={query}",
        "base_url": "https://www.netacad.com",
        "tipo": "Certificación redes/tecnología",
        "costo_tipico": "Gratis (curso) / $165-$330 USD (examen)",
    },
}

# Dominios académicos y sus certificaciones industriales relevantes
DOMAIN_CERTIFICATIONS = {
    # === Ingenierías y Tecnología ===
    "data science": ["Google Data Analytics", "IBM Data Science", "Microsoft Azure Data Scientist", "SAS Data Science"],
    "machine learning": ["Google Machine Learning", "AWS Machine Learning", "TensorFlow Developer", "DeepLearning.AI"],
    "cloud computing": ["AWS Cloud Practitioner", "Azure Fundamentals", "Google Cloud Digital Leader"],
    "cybersecurity": ["CompTIA Security+", "Google Cybersecurity", "IBM Cybersecurity Analyst", "CISSP"],
    "project management": ["Google Project Management", "PMI CAPM", "Scrum.org PSM I", "Agile Master"],
    "marketing": ["Google Digital Marketing", "HubSpot Inbound Marketing", "Meta Social Media Marketing", "Salesforce Marketing Cloud"],
    "programming": ["Oracle Java Certified", "Microsoft Technology Associate", "Python Institute PCEP", "Unity Certified User"],
    "business": ["Six Sigma Yellow Belt", "Google Business Intelligence", "Lean Management", "Salesforce Associate"],
    "artificial intelligence": ["Google AI Essentials", "IBM AI Engineering", "DeepLearning.AI TensorFlow", "Microsoft Azure AI Fundamentals"],
    
    # === Diseño, Arquitectura y Arte ===
    "design": ["Google UX Design", "Adobe Certified Professional", "Interaction Design Foundation", "Autodesk Certified User"],
    "arquitectura": ["Autodesk Revit Architecture", "LEED Green Associate", "AutoCAD Certified User", "BIM Manager"],
    "arte": ["Sotheby's Institute of Art", "MoMA Courses", "Adobe Creative Cloud"],
    "urbanismo": ["Planetizen Courses", "LEED Green Associate", "GIS Certification"],

    # === Ciencias de la Salud y Químicas ===
    "health": ["HIPAA Compliance", "WHO Health Emergency", "Public Health Informatics", "Red Cross First Aid"],
    "salud": ["WHO Health", "HIPAA", "Public Health", "Soporte Vital Básico"],
    "nutrición": ["Stanford Introduction to Food and Health", "Precision Nutrition", "ServSafe"],
    "ingeniería de alimentos": ["HACCP Certification", "FSSC 22000", "ServSafe Manager"],
    "biotecnología": ["BioTech Primer", "Good Manufacturing Practice (GMP)"],

    # === Humanidades y Ciencias Sociales ===
    # === Humanidades, Educación y Sociales ===
    "education": ["Google Certified Educator", "ISTE Certification", "UNESCO ICT-CFT", "Apple Teacher", "Canvas Certified Educator"],
    "educación": ["Google Certified Educator", "ISTE", "Apple Teacher", "Microsoft Educator", "Certificación CONOCER Logro Educativo"],
    "pedagogía": ["Montessori Diploma", "Reggio Emilia Approach", "Neurodidáctica", "Estrategias de Enseñanza-Aprendizaje"],
    "humanidades": ["Unesco Chair in Bioethics", "Digital Humanities Certificate", "Stanford Introduction to Logic"],
    "teaching": ["TEFL/TESOL Certification", "Cambridge CELTA", "TKT (Teaching Knowledge Test)"],
    "derecho": ["Legal Technology Certificate", "GDPR Compliance", "Intellectual Property Law", "Arbitraje Internacional"],
    "law": ["Legal Tech", "Cyber Law", "International Law Certificate", "Legal Project Management"],
    "derechos humanos": ["Amnesty International Human Rights", "UN Human Rights Education", "Corte Interamericana DH"],
    "psicología": ["Mental Health First Aid", "APA Continuing Education", "Counseling Skills", "Terapia Cognitivo-Conductual"],
    # === Ciencias Básicas e Ingeniería ===
    "física": ["Diplomado en Físca (UNAM)", "Física Computacional", "Mecánica Cuántica para Científicos", "Curso de Física (Edutin)"],
    "química": ["Diplomado en Química Analítica (ITM)", "Química en Contexto", "Curso de Química (Edutin)", "SC(ASCP) Chemistry Specialist"],
    "ingeniería química": ["Six Sigma Green Belt (Español)", "Gestión de Seguridad de Procesos", "Diplomado en Ingeniería Química"],
    "biología": ["Diplomado en Biología Molecular (Genotipia)", "Curso de Biología (Edutin)", "Bioinformática", "Genómica"],
    "robótica": ["Diplomado en Robótica (Tec de Monterrey)", "Curso de Robótica (Edutin)", "Certificación FANUC", "Programación de Robots (Rosetta)"],
    
    # === Humanidades y Artes (Ampliado) ===
    "historia": ["Diplomado Historia de México (UNAM)", "Curso de Historia Universal (Edutin)", "Estudios de Museos", "Archivística"],
    "literatura": ["Diplomado en Literatura y Lengua (Educa Perú)", "Certificación Experto en Literatura Contemporánea", "Escritura Creativa (Español)"],
    "humanidades": ["Diplomado en Humanidades Digitales", "Cátedra UNESCO Bioética", "Comunicación Intercultural"],
    "arte": ["Diplomado en Historia del Arte", "Curso de Artística Profesional (Edutin)", "Diseño Gráfico (Español)"],

    # === Tecnología Avanzada (Ampliado) ===
    "artificial intelligence": ["Ingeniero de IA de Microsoft Azure", "Ingeniero de ML Profesional de Google", "Certificado Profesional de IA Aplicada de IBM"],
    "inteligencia artificial": ["Ingeniero de IA de Microsoft Azure", "Ingeniero de ML Profesional de Google", "Certificado Profesional de IA Aplicada de IBM"],
    "programación": ["Desarrollador Certificado AWS (Español)", "Certificado Profesional de Desarrollador de Android", "Python Institute PCAP (Español)"],
    "diseño": ["Certificado Profesional de Diseño de Experiencia del Usuario (UX) de Google", "Adobe Certified Professional (Español)", "Design Thinking (Español)"],
    "tecnología": ["Certificado Profesional de Soporte de TI de Google", "AWS Cloud Practitioner (Español)", "Cisco CCNA (Español)"],
    "transformación digital": ["Transformación Digital (MIT en Español)", "Scrum Master (Español)", "Diplomado en Transformación Digital"],

    # === Traducciones directas y alias comunes en español ===
    "análisis de datos": ["Certificado Profesional de Google en Análisis de Datos", "Ciencia de Datos de IBM", "Analista de Datos de Microsoft Power BI"],
    "gestión de proyectos": ["Certificado Profesional de Gestión de Proyectos de Google", "CAPM del PMI", "Scrum Master Certificado"],
    "ciberseguridad": ["Certificado Profesional de Ciberseguridad de Google", "CompTIA Security+ (Español)", "Analista de Ciberseguridad de IBM"],
    "mercadotecnia": ["Marketing Digital y E-commerce de Google", "Meta Social Media Marketing (Español)", "HubSpot Inbound Marketing (Español)"],
    "educación": ["Educador Certificado de Google", "Certificación ISTE", "UNESCO ICT-CFT"],
    "salud": ["Primeros Auxilios (Cruz Roja)", "HIPAA (Español)", "Salud Pública"],
    "liderazgo": ["SHRM-CP (Español)", "Liderazgo CCL", "Harvard ManageMentor (Español)"],
    "sustentabilidad": ["Sustentabilidad ISSP", "Estándares GRI", "Alfabetización en Carbono"],
    "finanzas": ["CFA Institute", "Conceptos de Mercado Bloomberg (Español)", "Instituto de Finanzas Corporativas"],
}


def search_external_certifications(competencies: list[dict],
                                    document_text: str = "",
                                    max_results: int = 10) -> list[dict]:
    """
    Busca microcertificaciones externas basándose en las competencias extraídas.
    Usa la base de datos pre-compilada de plataformas y certificaciones de industria.
    """
    results = []

    # Extraer términos de búsqueda de las competencias
    search_terms = [c["term"] for c in competencies[:6]]
    combined_query = " ".join(search_terms)

    # 1. Buscar certificaciones de industria relevantes
    industry_results = _match_industry_certifications(search_terms, combined_query)
    results.extend(industry_results)

    # 2. Generar enlaces de búsqueda en plataformas externas
    platform_results = _generate_platform_searches(search_terms, combined_query)
    results.extend(platform_results)

    # Deduplicar y limitar
    seen = set()
    unique_results = []
    for r in results:
        key = r["nombre"].lower().strip()
        if key not in seen:
            seen.add(key)
            unique_results.append(r)

    return unique_results[:max_results]


def _match_industry_certifications(search_terms: list[str],
                                    combined_query: str) -> list[dict]:
    """Busca certificaciones de industria que coincidan con los términos."""
    results = []
    query_lower = combined_query.lower()

    for domain, certs in DOMAIN_CERTIFICATIONS.items():
        # Verificar si algún término coincide con el dominio
        domain_words = [w for w in domain.lower().split() if len(w) > 3]
        match_score = sum(1 for term in search_terms
                         if any(dw in term.lower() for dw in domain_words))

        if match_score > 0 or any(dw in query_lower for dw in domain_words):
            for cert_name in certs:
                results.append({
                    "nombre": cert_name,
                    "plataforma": "Certificación de Industria",
                    "url": f"https://www.google.com/search?q={quote_plus(cert_name + ' certification')}",
                    "duracion": "Variable (típicamente 1-3 meses)",
                    "costo": "Varía según proveedor",
                    "descripcion": f"Certificación profesional relacionada con {domain}. "
                                   f"Buscar directamente en el sitio del proveedor para información actualizada.",
                    "justificacion": f"Coincide con el área de {domain} identificada en el documento del docente. "
                                     f"Es una certificación reconocida en la industria que valida competencias prácticas.",
                    "caracteristicas": "Certificación de industria reconocida internacionalmente",
                    "tipo": "Industria"
                })

    return results


def _generate_platform_searches(search_terms: list[str],
                                 combined_query: str) -> list[dict]:
    """Genera enlaces de búsqueda en plataformas externas."""
    results = []
    encoded_query = quote_plus(combined_query)

    priority_platforms = ["edX", "FutureLearn", "LinkedIn Learning",
                          "Microsoft Learn", "IBM SkillsBuild", "HubSpot Academy",
                          "Salesforce Trailhead", "Meta Blueprint", "Autodesk Education"]

    for platform_name in priority_platforms:
        if platform_name not in PLATFORMS:
            continue
        platform = PLATFORMS[platform_name]
        search_url = platform["search_url"].replace("{query}", encoded_query)

        results.append({
            "nombre": f"Búsqueda en {platform_name}: {combined_query[:50]}",
            "plataforma": platform_name,
            "url": search_url,
            "duracion": "Variable según programa seleccionado",
            "costo": platform["costo_tipico"],
            "descripcion": f"Resultados de búsqueda en {platform_name} para las competencias identificadas. "
                           f"Visitar el enlace para ver programas disponibles actualizados.",
            "justificacion": f"{platform_name} es una plataforma reconocida ({platform['tipo']}) "
                             f"que ofrece microcredenciales y certificaciones en el área temática identificada.",
            "caracteristicas": platform["tipo"],
            "tipo": "Plataforma"
        })

    return results


def enrich_with_web_search(competencies: list[dict],
                            search_function=None) -> list[dict]:
    """
    Enriquece resultados con búsqueda web real (para uso con WebSearch tool).
    search_function debe ser una función que reciba un query string y retorne resultados.
    """
    if search_function is None:
        return []

    results = []
    search_terms = [c["term"] for c in competencies[:3]]

    for term in search_terms:
        queries = [
            f"{term} microcredential certification online 2025 2026",
            f"{term} professional certificate free open enrollment",
        ]
        for query in queries:
            try:
                search_results = search_function(query)
                if search_results:
                    results.extend(search_results)
            except Exception:
                continue

    return results
