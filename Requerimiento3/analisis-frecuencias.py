import sqlite3
import re
from collections import Counter

# Obtener la ruta absoluta de la base de datos
db_path = '../bibliometria.db'
conexion = sqlite3.connect(db_path)
cursor = conexion.cursor()

# Crear la tabla para almacenar los resultados si no existe
cursor.execute('''
CREATE TABLE IF NOT EXISTS frecuencia_variables (
    categoria TEXT,
    variable TEXT,
    frecuencia INTEGER,
    UNIQUE(categoria, variable)
);
''')
conexion.commit()

# Consultar los abstracts de la tabla productos
query = "SELECT abstract FROM productos WHERE abstract != 'No encontrado';"
abstracts = [row[0].lower() for row in cursor.execute(query).fetchall()]

# Diccionario de categorías con términos y sinónimos
categorias_terminos = {
    "Habilidades": {
        "Abstraction": ["abstraction"],
        "Algorithm": ["algorithm"],
        "Algorithmic thinking": ["algorithmic thinking"],
        "Coding": ["coding"],
        "Collaboration": ["collaboration"],
        "Cooperation": ["cooperation"],
        "Creativity": ["creativity"],
        "Critical thinking": ["critical thinking"],
        "Debug": ["debug"],
        "Decomposition": ["decomposition"],
        "Evaluation": ["evaluation"],
        "Generalization": ["generalization"],
        "Logic": ["logic"],
        "Logical thinking": ["logical thinking"],
        "Modularity": ["modularity"],
        "Pattern recognition": ["pattern recognition"],
        "Problem solving": ["problem solving"],
        "Programming": ["programming"]
    },
    "Conceptos Computacionales": {
        "Conditionals": ["conditionals"],
        "Control structures": ["control structures"],
        "Directions": ["directions"],
        "Events": ["events", "triggers", "actions"],
        "Functions": ["functions", "methods", "procedures"],
        "Loops": ["loops", "iterations", "repetitions"],
        "Modular structure": ["modular structure"],
        "Parallelism": ["parallelism"],
        "Sequences": ["sequences"],
        "Software/hardware": ["software", "hardware"],
        "Variables": ["variables"]
    },
    "Actitudes":{
        "Emotional": ["emotional", "affective", "emotional response"],
        "Engagement": ["engagement", "involvement", "participation"],
        "Motivation": ["motivation", "drive", "incentive"],
        "Perceptions": ["perceptions", "views", "perspectives"],
        "Persistence":["persistence"],
        "Self-efficacy":["self-efficacy"],
        "Self-perceived":["self-perceived"]
    },
    "Propiedades psicométricas":{
        "Classical Test Theory": ["classical test theory", "ctt", "traditional testing theory"],
        "Confirmatory Factor Analysis": ["confirmatory factor analysis", "cfa", "confirmatory modeling"],
        "Exploratory Factor Analysis": ["exploratory factor analysis", "efa", "factor exploration"],
        "Item Response Theory (IRT)": ["item response theory", "irt", "irt modeling", "item analysis"],
        "Reliability": ["reliability", "consistency", "dependability"],
        "Structural Equation Model": ["structural equation model", "sem", "sem analysis", "path analysis"],
        "Validity": ["validity", "accuracy", "truthfulness"]
    },
    "Herramienta de evaluación":{
        "Beginners Computational Thinking test": ["beginners computational thinking test", "bctt", "bct test"],
        "Coding Attitudes Survey": ["coding attitudes survey", "escas", "cas survey"],
        "Collaborative Computing Observation Instrument": ["collaborative computing observation instrument", "ccoi tool"],
        "Competent Computational Thinking test": ["competent computational thinking test", "cctt"],
        "Computational thinking skills test": ["computational thinking skills test", "ctst"],
        "Computational concepts": ["computational concepts"],
        "Computational Thinking Assessment for Chinese Elementary Students": ["computational thinking assessment for chinese elementary students", "cta-ces", "cta-ces assessment"],
        "Computational Thinking Challenge": ["computational thinking challenge", "ctc"],
        "Computational Thinking Levels Scale": ["computational thinking levels scale", "ctls"],
        "Computational Thinking Scale": ["computational thinking scale", "cts"],
        "Computational Thinking Skill Levels Scale": ["computational thinking skill levels scale", "cts"],
        "Computational Thinking Test": ["computational thinking test", "ctt", "ct evaluation"],
        "Computational Thinking Test for Elementary School Students": ["computational thinking test for elementary school students", "ctt-es"],
        "Computational Thinking Test for Lower Primary": ["computational thinking test for lower primary", "cttlp"],
        "Computational thinking-skill tasks on numbers and arithmetic": ["computational thinking-skill tasks on numbers and arithmetic"],
        "Computerized Adaptive Programming Concepts Test": ["computerized adaptive programming concepts test", "capct"],
        "CT Scale": ["ct scale", "cts"],
        "Elementary Student Coding Attitudes Survey": ["elementary student coding attitudes survey", "escas"],
        "General self-efficacy scale": ["general self-efficacy scale", "gses tool"],
        "ICT competency test": ["ict competency test"],
        "Instrument of computational identity": ["instrument of computational identity"],
        "KBIT fluid intelligence subtest": ["kbit fluid intelligence subtest"],
        "Mastery of computational concepts Test and an Algorithmic Test": ["mastery of computational concepts test and an algorithmic test"],
        "Multidimensional 21st Century Skills Scale": ["multidimensional 21st century skills scale"],
        "Self-efficacy scale": ["self-efficacy scale"],
        "STEM learning attitude scale": ["stem learning attitude scale", "stem-las"],
        "The computational thinking scale": ["the computational thinking scale"]
    },
    "Diseño de investigación":{
        "No experimental": ["no experimental", "observational", "descriptive"],
        "Experimental": ["experimental", "controlled study", "trial"],
        "Longitudinal research": ["longitudinal research", "long-term study", "cohort analysis"],
        "Mixed methods": ["mixed methods", "multi-method", "integrated approach"],
        "Post-test": ["post-test", "post-assessment", "final evaluation"],
        "Pre-test": ["pre-test", "pre-assessment", "initial test"],
        "Quasi-experiments": ["quasi-experiments", "non-randomized trial", "natural experiment"]
    },
    "Nivel de escolaridad":{
        "Upper elementary education": ["upper elementary education", "upper elementary school", "middle elementary"],
        "Primary school": ["primary school", "primary education", "elementary school", "grade school"],
        "Early childhood education": ["early childhood education", "kindergarten", "preschool", "pre-primary education"],
        "Secondary school": ["secondary school", "secondary education", "high school education"],
        "High school": ["high school", "higher education"],
        "University": ["university", "college", "tertiary education"]
    },
    "Medio":{
        "Block programming":["Block programming"],
        "Mobile application":["Mobile application"],
        "Pair programming":["Pair programming"],
        "Plugged activities":["Plugged activities"],
        "Programming":["Programming"],
        "Robotics": ["robotics", "robotic systems"],
        "Spreadsheet": ["spreadsheet", "data sheets"],
        "STEM": ["stem", "science-tech-engineering-math"],
        "Unplugged activities": ["unplugged activities", "offline tasks"]
    },
    "Estrategia":{
        "Construct-by-self mind mapping": ["construct-by-self mind mapping", "cbs-mm", "self-constructed mapping"],
        "Construct-on-scaffold mind mapping": ["construct-on-scaffold mind mapping", "cos-mm", "scaffolded mapping"],
        "Design-based learning": ["design-based learning", "dbl", "project-based design"],
        "Evidence-centred design approach": ["evidence-centred design approach", "evidence-based design"],
        "Gamification": ["gamification", "game elements", "playful learning"],
        "Reverse engineering pedagogy": ["reverse engineering pedagogy", "rep", "backwards engineering"],
        "Technology-enhanced learning": ["technology-enhanced learning", "tech-supported learning"],
        "Collaborative learning": ["collaborative learning", "group learning"],
        "Cooperative learning": ["cooperative learning", "team-based learning"],
        "Flipped classroom": ["flipped classroom", "inverted classroom"],
        "Game-based learning": ["game-based learning", "play-based education"],
        "Inquiry-based learning": ["inquiry-based learning", "question-driven learning"],
        "Personalized learning": ["personalized learning", "tailored education"],
        "Problem-based learning": ["problem-based learning", "case-based learning"],
        "Project-based learning": ["project-based learning", "task-based learning"],
        "Universal design for learning": ["universal design for learning", "inclusive design"]
    },
    "Herramienta":{
        "Alice": ["alice", "alice platform"],
        "Arduino": ["arduino"],
        "Scratch": ["scratch", "scratch environment"],
        "ScratchJr": ["scratchjr"],
        "Blockly Games": ["blockly games"],
        "Code.org": ["code.org"],
        "Codecombat": ["codecombat"],
        "CSUnplugged": ["csunplugged"],
        "Robot Turtles": ["robot turtles"],
        "Hello Ruby": ["hello ruby"],
        "Kodable": ["kodable"],
        "LightbotJr": ["lightbotjr"],
        "KIBO robots": ["kibo robots"],
        "BEE BOT": ["bee bot"],
        "CUBETTO": ["cubetto"],
        "Minecraft": ["minecraft", "minecraft education"],
        "Agent Sheets": ["agent sheets"],
        "Mimo": ["mimo"],
        "Py–Learn": ["py", "learn", "python learning"],
        "SpaceChem": ["spacechem"]
    }
}

# Inicializar una lista para almacenar las frecuencias con categoría
frecuencias = []

# Contar la frecuencia de aparición de cada término en los abstracts
for abstract in abstracts:
    for categoria, terminos in categorias_terminos.items():
        for termino, sinonimos in terminos.items():
            # Crear una expresión regular que busque cualquiera de los sinónimos del término
            patron = r'\b(' + '|'.join(map(re.escape, sinonimos)) + r')\b'
            conteo = len(re.findall(patron, abstract, flags=re.IGNORECASE))
            if conteo > 0:
                frecuencias.append({"categoria": categoria, "variable": termino, "frecuencia": conteo})

# Insertar los resultados en la tabla `frecuencia_variables`
for frecuencia in frecuencias:
    try:
        cursor.execute('''
        INSERT INTO frecuencia_variables (categoria, variable, frecuencia)
        VALUES (?, ?, ?)
        ''', (frecuencia['categoria'], frecuencia['variable'], frecuencia['frecuencia']))
    except sqlite3.IntegrityError:
        # Actualizar el conteo si el registro ya existe
        cursor.execute('''
        UPDATE frecuencia_variables
        SET frecuencia = frecuencia + ?
        WHERE categoria = ? AND variable = ?
        ''', (frecuencia['frecuencia'], frecuencia['categoria'], frecuencia['variable']))

# Confirmar 
conexion.commit()
conexion.close()

print("Análisis de frecuencias completado y almacenado en la base de datos.")