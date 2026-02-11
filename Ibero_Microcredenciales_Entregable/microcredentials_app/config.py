"""Configuración central de la app de Microcredenciales."""
import os

# === Rutas ===
# === Rutas ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DATA_DIR apunta a la raíz del proyecto (un nivel arriba de microcredentials_app)
PROJ_ROOT = os.path.dirname(BASE_DIR)
EXCEL_PATH = os.path.join(PROJ_ROOT, "Coursera Enterprise Catalog_Master.xlsx")
CACHE_PATH = os.path.join(BASE_DIR, "data", "courses_cache.pkl")
OUTPUT_DIR = os.path.join(PROJ_ROOT, "output_reports")

# === Filtros ===
MAX_LEARNING_HOURS = 20
MIN_SIMILARITY_THRESHOLD = 0.08
TOP_N_COURSERA = 10
TOP_N_EXTERNAL = 10
TOP_N_COMPETENCIES = 20

# === Hojas del Excel ===
SHEET_COURSES = "All Enterprise Courses"
SHEET_SPECIALIZATIONS = "Specializations & Certificates"
EXCEL_SKIPROWS = 3

# === Columnas de cursos ===
COL_NAME = "Course Name"
COL_PARTNER = "University / Industry Partner Name"
COL_TYPE = "Type of Content"
COL_DIFFICULTY = "Difficulty Level"
COL_HOURS = "Avg Total Learning Hours"
COL_RATING = "Course Rating"
COL_URL = "Course URL"
COL_DESCRIPTION = "Course Description"
COL_SKILLS = "Skills Learned"
COL_CORE_SKILLS = "Core Skills"
COL_DOMAIN = "Domain"
COL_SUBDOMAIN = "Sub-Domain"
COL_LANGUAGE = "Course Language"
COL_SPECIALIZATION = "Specialization"
COL_SPEC_URL = "Specialization URL"

# === Columnas de especializaciones ===
SCOL_NAME = "Specialization Name"
SCOL_PARTNERS = "Partners"
SCOL_NUM_COURSES = "Number of Courses"
SCOL_LANGUAGE = "Specialization Language"
SCOL_DOMAIN = "Specialization Primary Domain"
SCOL_SUBDOMAIN = "Specialization Primary Subdomain"
SCOL_DESCRIPTION = "Specialization Description"
SCOL_DIFFICULTY = "Difficulty Level"
SCOL_URL = "Specialization URL"
SCOL_TYPE = "Specialization Type"

# === Stop words español (para TF-IDF) ===
SPANISH_STOP_WORDS = [
    "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las", "por",
    "un", "para", "con", "no", "una", "su", "al", "lo", "como", "más", "pero",
    "sus", "le", "ya", "o", "este", "sí", "porque", "esta", "entre", "cuando",
    "muy", "sin", "sobre", "también", "me", "hasta", "hay", "donde", "quien",
    "desde", "todo", "nos", "durante", "todos", "uno", "les", "ni", "contra",
    "otros", "ese", "eso", "ante", "ellos", "e", "esto", "mí", "antes", "algunos",
    "qué", "unos", "yo", "otro", "otras", "otra", "él", "tanto", "esa", "estos",
    "mucho", "quienes", "nada", "muchos", "cual", "poco", "ella", "estar", "estas",
    "algunas", "algo", "nosotros", "mi", "mis", "tú", "te", "ti", "tu", "tus",
    "ellas", "nosotras", "vosotros", "vosotras", "os", "mío", "mía", "míos",
    "mías", "tuyo", "tuya", "tuyos", "tuyas", "suyo", "suya", "suyos", "suyas",
    "nuestro", "nuestra", "nuestros", "nuestras", "vuestro", "vuestra", "vuestros",
    "vuestras", "esos", "esas", "estoy", "estás", "está", "estamos", "estáis",
    "están", "esté", "estés", "estemos", "estéis", "estén", "estaré", "estarás",
    "estará", "estaremos", "estaréis", "estarán", "estaría", "estarías",
    "estaríamos", "estaríais", "estarían", "estaba", "estabas", "estábamos",
    "estabais", "estaban", "estuve", "estuviste", "estuvo", "estuvimos",
    "estuvisteis", "estuvieron", "ser", "soy", "eres", "es", "somos", "sois",
    "son", "sea", "seas", "seamos", "seáis", "sean", "seré", "serás", "será",
    "seremos", "seréis", "serán", "sería", "serías", "seríamos", "seríais",
    "serían", "era", "eras", "éramos", "erais", "eran", "fui", "fuiste", "fue",
    "fuimos", "fuisteis", "fueron", "haber", "he", "has", "ha", "hemos", "habéis",
    "han", "haya", "hayas", "hayamos", "hayáis", "hayan", "habré", "habrás",
    "habrá", "habremos", "habréis", "habrán", "habría", "habrías", "habríamos",
    "habríais", "habrían", "había", "habías", "habíamos", "habíais", "habían",
    "hube", "hubiste", "hubo", "hubimos", "hubisteis", "hubieron", "tener",
    "tengo", "tienes", "tiene", "tenemos", "tenéis", "tienen", "tenga", "tengas",
    "tengamos", "tengáis", "tengan", "tendré", "tendrás", "tendrá", "tendremos",
    "tendréis", "tendrán", "tendría", "tendrías", "tendríamos", "tendríais",
    "tendrían", "tenía", "tenías", "teníamos", "teníais", "tenían", "tuve",
    "tuviste", "tuvo", "tuvimos", "tuvisteis", "tuvieron", "hacer", "hago",
    "haces", "hace", "hacemos", "hacéis", "hacen", "haga", "hagas", "hagamos",
    "hagáis", "hagan", "haré", "harás", "hará", "haremos", "haréis", "harán",
    "haría", "harías", "haríamos", "haríais", "harían", "hacía", "hacías",
    "hacíamos", "hacíais", "hacían", "hice", "hiciste", "hizo", "hicimos",
    "hicisteis", "hicieron", "poder", "puedo", "puedes", "puede", "podemos",
    "podéis", "pueden", "ir", "voy", "vas", "va", "vamos", "vais", "van",
    "the", "of", "and", "to", "in", "a", "is", "that", "for", "it", "with",
    "as", "on", "was", "at", "by", "an", "be", "this", "from", "or", "are",
    "but", "not", "you", "all", "can", "had", "her", "one", "our", "out",
    "will", "has", "their", "been", "would", "each", "which", "do", "how",
    "if", "its", "than", "up", "other", "about", "into", "more", "your",
    "them", "way", "could", "these", "may", "use", "such", "then", "new",
    "also", "should", "did", "between", "after", "just", "some", "time",
    "very", "when", "who", "any", "no", "only", "well", "through", "course",
    "learn", "learning", "students", "student", "using", "based", "including",
    "concepts", "skills", "knowledge", "understand", "apply", "able",
    "will", "work", "working", "used", "different", "includes", "provide",
    "provided", "practice", "practices", "approach", "approaches",
    "curso", "cursos", "aprender", "aprendizaje", "estudiantes", "estudiante",
    "conocimientos", "habilidades", "competencias", "comprender", "aplicar",
    "capaz", "trabajo", "trabajar", "utilizar", "diferentes", "incluye",
    "incluyen", "proporcionar", "práctica", "prácticas", "enfoque", "enfoques",
    "nombre", "materia", "docente", "semestre", "periodo", "modalidad", 
    "presentación", "sesión", "horas", "duración", "horario", "atención", 
    "correo", "electrónico", "asesorías", "asesoria", "virtual", "presencial",
    "requisitos", "evaluación", "bibliografía", "temario", "objetivo", "objetivos",
    "introducción", "parte", "capítulo", "unidad", "tema", "temas", "contenido",
    "actividades", "aprendizaje", "alumnos", "alumno", "curso", "cursos",
    "desarrollo", "diseño", "diseno", "herramientas", "implementación", "implementacion",
    "fundamentos", "principios", "técnicas", "tecnicas", "proyecto", "proyectos",
    "taller", "seminario", "diplomado", "general", "programa", "módulo", "modulo"
]

# === Textos de la interfaz ===
UI_TITLE = "🎓 Recomendador de Microcredenciales"
UI_SUBTITLE = "Universidad Iberoamericana — Ciudad de México"
UI_UPLOAD_LABEL = "📄 Sube el documento del docente"
UI_UPLOAD_HELP = "Formatos: TXT, PDF, DOCX"
UI_HOURS_LABEL = "⏱️ Máximo de horas de aprendizaje"
UI_ANALYZE_BUTTON = "🔍 Analizar y Recomendar"
UI_PROCESSING = "Procesando..."
UI_NO_MATCHES = "No se encontraron microcredenciales que coincidan con el perfil del documento."
