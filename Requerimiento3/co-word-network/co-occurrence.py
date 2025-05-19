import sqlite3
import re
import networkx as nx
import matplotlib.pyplot as plt
from community import community_louvain
from collections import defaultdict
import pandas as pd
import os
import numpy as np
from adjustText import adjust_text


# Define the database path
db_path = '../../bibliometria.db'

# Connect to the database
conexion = sqlite3.connect(db_path)
cursor = conexion.cursor()

# Load abstracts
query = "SELECT id_producto, abstract FROM productos WHERE abstract != 'No encontrado';"
abstracts = cursor.execute(query).fetchall()
abstracts = [(row[0], row[1].lower()) for row in abstracts]

# Load frequency data
query_frec = '''
SELECT categoria, variable, SUM(frecuencia) AS total_frecuencia
FROM frecuencia_variables
GROUP BY categoria, variable;
'''
df_frecuencia = pd.read_sql_query(query_frec, conexion)

# Close the database connection
conexion.close()

# Define the categories and terms
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
    "Actitudes": {
        "Emotional": ["emotional", "affective", "emotional response"],
        "Engagement": ["engagement", "involvement", "participation"],
        "Motivation": ["motivation", "drive", "incentive"],
        "Perceptions": ["perceptions", "views", "perspectives"],
        "Persistence": ["persistence"],
        "Self-efficacy": ["self-efficacy"],
        "Self-perceived": ["self-perceived"]
    },
    "Propiedades psicométricas": {
        "Classical Test Theory": ["classical test theory", "ctt", "traditional_testing_theory"],
        "Confirmatory Factor Analysis": ["confirmatory factor analysis", "cfa", "confirmatory_modeling"],
        "Exploratory Factor Analysis": ["exploratory factor analysis", "efa", "factor_exploration"],
        "Item Response Theory (IRT)": ["item response theory", "irt", "irt_modeling", "item_analysis"],
        "Reliability": ["reliability", "consistency", "dependability"],
        "Structural Equation Model": ["structural equation model", "sem", "sem_analysis", "path_analysis"],
        "Validity": ["validity", "accuracy", "truthfulness"]
    },
    "Herramienta de evaluación": {
        "Beginners Computational Thinking test": ["beginners computational thinking test", "bctt", "bct_test"],
        "Coding Attitudes Survey": ["coding attitudes survey", "escas", "cas_survey"],
        "Collaborative Computing Observation Instrument": ["collaborative computing observation instrument", "ccoi_tool"],
        "Competent Computational Thinking test": ["competent computational thinking test", "cctt"],
        "Computational thinking skills test": ["computational thinking skills test", "ctst"],
        "Computational concepts": ["computational concepts"],
        "Computational Thinking Assessment for Chinese Elementary Students": ["computational thinking assessment for chinese elementary students", "cta-ces", "cta-ces_assessment"],
        "Computational Thinking Challenge": ["computational thinking challenge", "ctc"],
        "Computational Thinking Levels Scale": ["computational thinking levels scale", "ctls"],
        "Computational Thinking Scale": ["computational thinking scale", "cts"],
        "Computational Thinking Skill Levels Scale": ["computational thinking skill levels scale", "cts"],
        "Computational Thinking Test": ["computational thinking test", "ctt", "ct_evaluation"],
        "Computational Thinking Test for Elementary School Students": ["computational thinking test for elementary school students", "ctt-es"],
        "Computational Thinking Test for Lower Primary": ["computational thinking test for lower primary", "cttlp"],
        "Computational thinking-skill tasks on numbers and arithmetic": ["computational thinking-skill tasks on numbers and arithmetic"],
        "Computerized Adaptive Programming Concepts Test": ["computerized adaptive programming concepts test", "capct"],
        "CT Scale": ["ct scale", "cts"],
        "Elementary Student Coding Attitudes Survey": ["elementary student coding attitudes survey", "escas"],
        "General self-efficacy scale": ["general self-efficacy scale", "gses_tool"],
        "ICT competency test": ["ict competency test"],
        "Instrument of computational identity": ["instrument of computational identity"],
        "KBIT fluid intelligence subtest": ["kbit fluid intelligence subtest"],
        "Mastery of computational concepts Test and an Algorithmic Test": ["mastery of computational concepts test and an algorithmic test"],
        "Multidimensional 21st Century Skills Scale": ["multidimensional 21st century skills scale"],
        "Self-efficacy scale": ["self-efficacy scale"],
        "STEM learning attitude scale": ["stem learning attitude scale", "stem-las"],
        "The computational thinking scale": ["the computational thinking scale"]
    },
    "Diseño de investigación": {
        "No experimental": ["no experimental", "observational", "descriptive"],
        "Experimental": ["experimental", "controlled study", "trial"],
        "Longitudinal research": ["longitudinal research", "long-term study", "cohort analysis"],
        "Mixed methods": ["mixed methods", "multi-method", "integrated approach"],
        "Post-test": ["post-test", "post-assessment", "final evaluation"],
        "Pre-test": ["pre-test", "pre-assessment", "initial test"],
        "Quasi-experiments": ["quasi-experiments", "non-randomized trial", "natural experiment"]
    },
    "Nivel de escolaridad": {
        "Upper elementary education": ["upper elementary education", "upper elementary school", "middle elementary"],
        "Primary school": ["primary school", "primary education", "elementary school", "grade school"],
        "Early childhood education": ["early childhood education", "kindergarten", "preschool", "pre-primary education"],
        "Secondary school": ["secondary school", "secondary education", "high school education"],
        "High school": ["high school", "higher education"],
        "University": ["university", "college", "tertiary education"]
    },
    "Medio": {
        "Block programming": ["block programming"],
        "Mobile application": ["mobile application"],
        "Pair programming": ["pair programming"],
        "Plugged activities": ["plugged activities"],
        "Programming": ["programming"],
        "Robotics": ["robotics", "robotic systems"],
        "Spreadsheet": ["spreadsheet", "data sheets"],
        "STEM": ["stem", "science-tech-engineering-math"],
        "Unplugged activities": ["unplugged activities", "offline tasks"]
    },
    "Estrategia": {
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
    "Herramienta": {
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

# Compute co-occurrences
coocurrencias = defaultdict(int)
for id_producto, abstract in abstracts:
    # Find all variables present in the abstract
    variables_presentes = set()
    for categoria, terminos in categorias_terminos.items():
        for termino, sinonimos in terminos.items():
            patron = r'\b(' + '|'.join(map(re.escape, sinonimos)) + r')\b'
            if re.search(patron, abstract, flags=re.IGNORECASE):
                variables_presentes.add(termino)
    
    # Count co-occurrences for pairs of variables
    for var1 in variables_presentes:
        for var2 in variables_presentes:
            if var1 < var2:  # Avoid counting pairs twice and self-loops
                coocurrencias[(var1, var2)] += 1

# Create the network
G = nx.Graph()

# Add nodes with frequencies
frecuencias_dict = dict(zip(df_frecuencia['variable'], df_frecuencia['total_frecuencia']))
for variable in set([var for pair in coocurrencias.keys() for var in pair]):
    freq = frecuencias_dict.get(variable, 0)
    G.add_node(variable, frequency=freq)

# Add edges with co-occurrence weights (apply threshold)
min_coocurrencia = 2
for (var1, var2), count in coocurrencias.items():
    if count >= min_coocurrencia:
        G.add_edge(var1, var2, weight=count)

# Apply Louvain clustering
particion = community_louvain.best_partition(G, resolution=1.0, random_state=42)

# Assign clusters to nodes
nx.set_node_attributes(G, particion, 'cluster')

# Visualization
plt.figure(figsize=(15, 10))

# Layout with better spacing (increased k value)
pos = nx.spring_layout(G, k=0.8, iterations=100, seed=42)

# Node sizes (limiting max size for better readability)
node_sizes = [min(3000, G.nodes[node]['frequency'] * 15) for node in G.nodes]

# Node colors based on clusters
node_colors = [G.nodes[node]['cluster'] for node in G.nodes]

# Edge widths based on co-occurrence weight
edge_widths = [G.edges[edge]['weight'] * 0.3 for edge in G.edges]

# Draw nodes
nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, cmap=plt.cm.tab20, alpha=0.8)

# Draw edges
nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color='gray', alpha=0.5)

# Draw labels with smaller font and spacing adjustments
texts = []
for node, (x, y) in pos.items():
    if G.nodes[node]['frequency'] > 0:
        texts.append(plt.text(x, y, node, fontsize=7, ha='center', va='center'))

# Adjust text to avoid overlap
adjust_text(texts, arrowprops=dict(arrowstyle='-', color='lightgray'))

# Save the visualization
script_dir = os.path.dirname(os.path.abspath(__file__))  # Ruta de la carpeta del script
plt.title("Co-Word Network Visualization", fontsize=14)
plt.axis('off')
plt.savefig(
    os.path.join(script_dir, "co_word_network.png"),
    dpi=300,
    bbox_inches='tight',
    pad_inches=0.1
)
plt.close()

# Summarize clusters
cluster_summary = defaultdict(list)
for node, cluster_id in particion.items():
    cluster_summary[cluster_id].append(node)

print("Thematic Clusters:")
for cluster_id, nodes in cluster_summary.items():
    print(f"Cluster {cluster_id}: {', '.join(nodes)}")