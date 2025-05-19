from flask import Flask, render_template_string
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import sqlite3
import io
import base64
import os
from wordcloud import WordCloud
import re
import networkx as nx
from community import community_louvain
from collections import defaultdict
import numpy as np
from adjustText import adjust_text

app = Flask(__name__)

# Utilidad para convertir un plt a imagen base64
def fig_to_base64():
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img = base64.b64encode(buf.getvalue()).decode('utf8')
    buf.close()
    plt.close()
    return img

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard Bibliometría</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container py-5">
            <h1 class="mb-4 text-center">Dashboard Bibliometría</h1>
            <ul class="list-group list-group-flush shadow-sm">
                <li class="list-group-item"><a href="/anios_tipoproducto">Años por Tipo de Producto</a></li>
                <li class="list-group-item"><a href="/apariciones_journal">Apariciones por Journal</a></li>
                <li class="list-group-item"><a href="/autores_apariciones">Autores más citados</a></li>
                <li class="list-group-item"><a href="/productos_por_tipo">Productos por Tipo</a></li>
                <li class="list-group-item"><a href="/publisher_apariciones">Apariciones por Publisher</a></li>
                <li class="list-group-item"><a href="/nubes_palabras">Generar nubes de palabras por categoría</a></li>
                <li class="list-group-item"><a href="/coocurrencia_palabras">Generar Word Occurrence</a></li>
            </ul>
        </div>
    </body>
    </html>
    '''
@app.route('/anios_tipoproducto')
def anios_tipoproducto():
    db_path = '../bibliometria.db'
    conn = sqlite3.connect(db_path)
    tipos_producto = ["Article", "Conference", "BookChapter", "Book"]
    imgs = []
    for tipo in tipos_producto:
        query = f"""
        SELECT anio_publicacion, COUNT(*) as cantidad
        FROM productos
        WHERE tipo_producto = '{tipo}' AND anio_publicacion != 'No encontrado'
        GROUP BY anio_publicacion
        ORDER BY anio_publicacion ASC;
        """
        data = conn.execute(query).fetchall()
        df = pd.DataFrame(data, columns=['anio_publicacion', 'cantidad'])
        if df.empty:
            continue
        plt.figure(figsize=(18, 8))  # HD: más grande
        ax = sns.barplot(data=df, x='anio_publicacion', y='cantidad', palette='flare')
        for p in ax.patches:
            height = p.get_height()
            if height > 0:
                ax.annotate(f'{int(height)}', (p.get_x() + p.get_width() / 2., height),
                            ha='center', va='bottom', fontsize=14, color='black')
        plt.title(f"Productos por Año - {tipo}", fontsize=20)
        plt.xlabel("Año de Publicación", fontsize=16)
        plt.ylabel("Cantidad", fontsize=16)
        plt.xticks(rotation=45, fontsize=12)
        plt.yticks(fontsize=12)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)  # HD: dpi alto
        buf.seek(0)
        img = base64.b64encode(buf.getvalue()).decode('utf8')
        buf.close()
        plt.close()
        imgs.append(img)
    conn.close()
    html_imgs = ''.join([
        f'<img src="data:image/png;base64,{img}" style="width:100%; max-width:2000px; margin:30px 0; border-radius:12px; box-shadow:0 0 16px #333;"/>' 
        for img in imgs
    ])
    return f'<h2 style="margin-bottom:32px;">Años de Publicación por Tipo de Producto</h2>{html_imgs}<br><a href="/">Volver</a>'

@app.route('/apariciones_journal')
def apariciones_journal():
    db_path = '../bibliometria.db'
    conn = sqlite3.connect(db_path)
    query = """
    SELECT journal, COUNT(*) as cantidad
    FROM productos
    WHERE journal != 'No encontrado'
    GROUP BY journal
    ORDER BY cantidad DESC
    LIMIT 15;
    """
    data = conn.execute(query).fetchall()
    conn.close()
    df = pd.DataFrame(data, columns=['journal', 'cantidad'])
    plt.figure(figsize=(18, 10))  # HD: más grande
    ax = sns.barplot(data=df, x='cantidad', y='journal', palette='flare')
    for p in ax.patches:
        width = p.get_width()
        if width > 0:
            ax.annotate(f'{int(width)}', (p.get_x() + width, p.get_y() + p.get_height() / 2),
                        ha='left', va='center', fontsize=16, color='black')
    plt.title("15 Journals con más Apariciones", fontsize=22)
    plt.xlabel("Cantidad de Productos", fontsize=16)
    plt.ylabel("Journal", fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)  # HD: dpi alto
    buf.seek(0)
    img = base64.b64encode(buf.getvalue()).decode('utf8')
    buf.close()
    plt.close()
    return f'<h2>Apariciones por Journal</h2><img src="data:image/png;base64,{img}" style="width:100%; max-width:2000px; margin:30px 0; border-radius:12px; box-shadow:0 0 16px #333;"/><br><a href="/">Volver</a>'


@app.route('/autores_apariciones')
def autores_apariciones():
    db_path = '../bibliometria.db'
    conn = sqlite3.connect(db_path)
    query = """
    SELECT primer_autor, COUNT(*) as cantidad
    FROM productos
    WHERE primer_autor != 'No encontrado'
    GROUP BY primer_autor
    ORDER BY cantidad DESC
    LIMIT 15;
    """
    data = conn.execute(query).fetchall()
    conn.close()
    df = pd.DataFrame(data, columns=['primer_autor', 'cantidad'])
    plt.figure(figsize=(18, 10))  # HD: más grande
    ax = sns.barplot(data=df, x='cantidad', y='primer_autor', palette='flare')
    for p in ax.patches:
        width = p.get_width()
        if width > 0:
            ax.annotate(f'{int(width)}', (p.get_x() + width, p.get_y() + p.get_height() / 2),
                        ha='left', va='center', fontsize=16, color='black')
    plt.title("15 Autores Más Citados", fontsize=22)
    plt.xlabel("Cantidad de Artículos", fontsize=16)
    plt.ylabel("Primer Autor", fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)  # HD: dpi alto
    buf.seek(0)
    img = base64.b64encode(buf.getvalue()).decode('utf8')
    buf.close()
    plt.close()
    return f'<h2>Autores más citados</h2><img src="data:image/png;base64,{img}" style="width:100%; max-width:2000px; margin:30px 0; border-radius:12px; box-shadow:0 0 16px #333;"/><br><a href="/">Volver</a>'


@app.route('/productos_por_tipo')
def productos_por_tipo():
    db_path = '../bibliometria.db'
    conn = sqlite3.connect(db_path)
    query = """
    SELECT tipo_producto, COUNT(*) as cantidad
    FROM productos
    GROUP BY tipo_producto
    ORDER BY cantidad DESC;
    """
    data = conn.execute(query).fetchall()
    conn.close()
    df = pd.DataFrame(data, columns=['tipo_producto', 'cantidad'])
    plt.figure(figsize=(14, 8))  # HD: más grande
    ax = sns.barplot(data=df, x='tipo_producto', y='cantidad', palette='flare')
    for p in ax.patches:
        height = p.get_height()
        if height > 0:
            ax.annotate(f'{int(height)}', (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='bottom', fontsize=14, color='black')
    plt.title("Cantidad de Productos por Tipo", fontsize=20)
    plt.xlabel("Tipo de Producto", fontsize=16)
    plt.ylabel("Cantidad de Productos", fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)  # HD: dpi alto
    buf.seek(0)
    img = base64.b64encode(buf.getvalue()).decode('utf8')
    buf.close()
    plt.close()
    return f'<h2>Productos por Tipo</h2><img src="data:image/png;base64,{img}" style="width:100%; max-width:2000px; margin:30px 0; border-radius:12px; box-shadow:0 0 16px #333;"/><br><a href="/">Volver</a>'


@app.route('/publisher_apariciones')
def publisher_apariciones():
    db_path = '../bibliometria.db'
    conn = sqlite3.connect(db_path)
    query = """
    SELECT base_datos, COUNT(*) as cantidad
    FROM productos
    GROUP BY base_datos
    ORDER BY cantidad DESC;
    """
    data = conn.execute(query).fetchall()
    conn.close()
    df = pd.DataFrame(data, columns=['base_datos', 'cantidad'])
    plt.figure(figsize=(14, 8))  # HD: más grande
    ax = sns.barplot(data=df, x='base_datos', y='cantidad', palette='flare')
    for p in ax.patches:
        height = p.get_height()
        if height > 0:
            ax.annotate(f'{int(height)}', (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='bottom', fontsize=14, color='black')
    plt.title("Cantidad de Productos por Publisher", fontsize=20)
    plt.xlabel("Publisher", fontsize=16)
    plt.ylabel("Cantidad de Productos", fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)  # HD: dpi alto
    buf.seek(0)
    img = base64.b64encode(buf.getvalue()).decode('utf8')
    buf.close()
    plt.close()
    return f'<h2>Apariciones por Publisher</h2><img src="data:image/png;base64,{img}" style="width:100%; max-width:2000px; margin:30px 0; border-radius:12px; box-shadow:0 0 16px #333;"/><br><a href="/">Volver</a>'

@app.route('/nubes_palabras')
def nubes_palabras():
    db_path = '../bibliometria.db'
    conexion = sqlite3.connect(db_path)
    query = '''
    SELECT categoria, variable, SUM(frecuencia) AS total_frecuencia
    FROM frecuencia_variables
    GROUP BY categoria, variable
    ORDER BY categoria, total_frecuencia DESC;
    '''
    df_frecuencia = pd.read_sql_query(query, conexion)
    conexion.close()

    output_dir = "nubes_palabras"
    os.makedirs(output_dir, exist_ok=True)

    # Nube total
    frecuencias_totales = dict(zip(df_frecuencia['variable'], df_frecuencia['total_frecuencia']))
    
    wordcloud_total = WordCloud(
        width=3840, height=2160, background_color='black', colormap='Set3',
        scale=4, max_words=120, margin=0
    ).generate_from_frequencies(frecuencias_totales)
    plt.figure(figsize=(12, 6), facecolor='black')
    plt.imshow(wordcloud_total, interpolation='bilinear')
    plt.axis('off')
    plt.margins(0, 0)
    plt.gca().set_position([0, 0, 1, 1])
    plt.savefig(os.path.join(output_dir, "nube_todas_categorias.png"),
            dpi=400, bbox_inches='tight', pad_inches=0, facecolor='black')
    plt.close()

    # Nubes por categoría
    categorias = df_frecuencia['categoria'].unique()
    for categoria in categorias:
        df_categoria = df_frecuencia[df_frecuencia['categoria'] == categoria]
        frecuencias_categoria = dict(zip(df_categoria['variable'], df_categoria['total_frecuencia']))
        wordcloud_categoria = WordCloud(
            width=1920, height=1080, background_color='black', colormap='Set3',
            scale=2, max_words=120, margin=0
        ).generate_from_frequencies(frecuencias_categoria)
        plt.figure(figsize=(12, 6), facecolor='black')
        plt.imshow(wordcloud_categoria, interpolation='bilinear')
        plt.axis('off')
        plt.margins(0, 0)
        plt.gca().set_position([0, 0, 1, 1])
        filename = f"nube_{categoria.replace(' ', '_').lower()}.png"
        plt.savefig(os.path.join(output_dir, filename),
                    dpi=200, bbox_inches='tight', pad_inches=0, facecolor='black')
        plt.close()

    # Diccionario para títulos amigables
    titulos_amigables = {
        "nube_todas_categorias.png": "Nube de todas las categorías",
        "nube_actitudes.png": "Nube de palabras: Actitudes",
        "nube_habilidades.png": "Nube de palabras: Habilidades",
        "nube_conceptos_computacionales.png": "Nube de palabras: Conceptos Computacionales",
        "nube_propiedades_psicométricas.png": "Nube de palabras: Propiedades Psicométricas",
        "nube_herramienta_de_evaluación.png": "Nube de palabras: Herramienta de Evaluación",
        "nube_diseño_de_investigación.png": "Nube de palabras: Diseño de Investigación",
        "nube_nivel_de_escolaridad.png": "Nube de palabras: Nivel de Escolaridad",
        "nube_medio.png": "Nube de palabras: Medio",
        "nube_estrategia.png": "Nube de palabras: Estrategia",
        "nube_herramienta.png": "Nube de palabras: Herramienta"
        # Agrega más si tienes otras categorías
    }

    # Mostrar las imágenes generadas con títulos amigables
    imgs_html = ""
    for filename in sorted(os.listdir(output_dir)):
        if filename.endswith(".png"):
            titulo = titulos_amigables.get(filename, filename)
            with open(os.path.join(output_dir, filename), "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode('utf8')
                imgs_html += f"<h3>{titulo}</h3><img src='data:image/png;base64,{img_base64}' style='width:100%; max-width:1800px; margin-bottom:40px; border-radius:12px; box-shadow:0 0 16px #333;'/><br>"

    return f"<h2>Nubes de palabras por categoría</h2>{imgs_html}<br><a href='/'>Volver</a>"

@app.route('/coocurrencia_palabras')
def coocurrencia_palabras():
    # --- Código de co-occurrence.py adaptado para Flask ---
    db_path = '../bibliometria.db'
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
    conexion.close()

    # Define the categories and terms (copiado tal cual del co-occurrence.py)
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
        variables_presentes = set()
        for categoria, terminos in categorias_terminos.items():
            for termino, sinonimos in terminos.items():
                patron = r'\b(' + '|'.join(map(re.escape, sinonimos)) + r')\b'
                if re.search(patron, abstract, flags=re.IGNORECASE):
                    variables_presentes.add(termino)
        for var1 in variables_presentes:
            for var2 in variables_presentes:
                if var1 < var2:
                    coocurrencias[(var1, var2)] += 1

    # Create the network
    G = nx.Graph()
    frecuencias_dict = dict(zip(df_frecuencia['variable'], df_frecuencia['total_frecuencia']))
    for variable in set([var for pair in coocurrencias.keys() for var in pair]):
        freq = frecuencias_dict.get(variable, 0)
        G.add_node(variable, frequency=freq)

    min_coocurrencia = 2
    for (var1, var2), count in coocurrencias.items():
        if count >= min_coocurrencia:
            G.add_edge(var1, var2, weight=count)

    # Louvain clustering
    if len(G.nodes) > 0 and len(G.edges) > 0:
        particion = community_louvain.best_partition(G, resolution=1.0, random_state=42)
        nx.set_node_attributes(G, particion, 'cluster')
    else:
        particion = {}

    # Visualization
    plt.figure(figsize=(15, 10))
    pos = nx.spring_layout(G, k=0.8, iterations=100, seed=42)
    node_sizes = [min(3000, G.nodes[node]['frequency'] * 15) for node in G.nodes]
    node_colors = [G.nodes[node].get('cluster', 0) for node in G.nodes]
    edge_widths = [G.edges[edge]['weight'] * 0.3 for edge in G.edges]
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, cmap=plt.cm.tab20, alpha=0.8)
    nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color='gray', alpha=0.5)
    texts = []
    for node, (x, y) in pos.items():
        if G.nodes[node]['frequency'] > 0:
            texts.append(plt.text(x, y, node, fontsize=7, ha='center', va='center'))
    adjust_text(texts, arrowprops=dict(arrowstyle='-', color='lightgray'))
    plt.title("Co-Word Network Visualization", fontsize=14)
    plt.axis('off')

    # Guardar la imagen en una ruta temporal
    img_path = "co_word_network.png"
    plt.savefig(img_path, dpi=300, bbox_inches='tight', pad_inches=0.1)
    plt.close()

    # Mostrar la imagen en la web
    if not os.path.exists(img_path):
        return "<h2>No se pudo generar la red de coocurrencia.</h2><a href='/'>Volver</a>"

    with open(img_path, "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode('utf8')

    html = f"""
    <h2>Red de Coocurrencia de Palabras Clave</h2>
    <img src='data:image/png;base64,{img_base64}' style='max-width:90vw; margin-bottom:40px;'/><br>
    <a href='/'>Volver</a>
    """
    return html


if __name__ == '__main__':
    app.run(debug=True)