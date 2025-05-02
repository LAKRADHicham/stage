import os
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

DOCUMENTS_FOLDER = os.path.join('static', 'documents')
CATEGORIES = ['Gammes operatoires', 'Procedures maintenance', 'REX']

def lister_sous_dossiers():
    structure = {}
    for cat in CATEGORIES:
        chemin = os.path.join(DOCUMENTS_FOLDER, cat)
        sous_dossiers = [d for d in os.listdir(chemin) if os.path.isdir(os.path.join(chemin, d))]
        structure[cat] = sous_dossiers
    return structure

def lister_documents_par_categorie():
    documents = {}
    for cat in CATEGORIES:
        chemin_categorie = os.path.join(DOCUMENTS_FOLDER, cat)
        categorie_docs = {}
        
        # Parcourir les sous-dossiers de la catégorie
        for sous_dossier in os.listdir(chemin_categorie):
            chemin_sous_dossier = os.path.join(chemin_categorie, sous_dossier)
            if os.path.isdir(chemin_sous_dossier):
                # Lister les fichiers PDF dans le sous-dossier
                fichiers = [f for f in os.listdir(chemin_sous_dossier) if f.lower().endswith('.pdf')]
                categorie_docs[sous_dossier] = fichiers
        
        documents[cat] = categorie_docs
    return documents

def rechercher_documents(term):
    results = []
    for category in CATEGORIES:
        base_path = os.path.join(DOCUMENTS_FOLDER, category)
        for root, _, files in os.walk(base_path):
            for file in files:
                if term.lower() in file.lower() and file.lower().endswith('.pdf'):
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, start=DOCUMENTS_FOLDER)
                    results.append((file, relative_path.replace('\\', '/')))
    return results

@app.route('/', methods=['GET', 'POST'])
def index():
    dossiers = lister_sous_dossiers()
    documents = lister_documents_par_categorie()
    results = []
    message = ""
    
    if request.method == 'POST':
        if 'search' in request.form:
            search_term = request.form.get('search')
            if not search_term:
                message = "Veuillez renseigner la barre de recherche."
            else:
                results = rechercher_documents(search_term)
    
    return render_template('index.html', 
                         results=results, 
                         dossiers=dossiers, 
                         documents=documents,
                         message=message,
                         categories=CATEGORIES)

@app.route('/view/<path:path>')
def view_document(path):
    return render_template('view_document.html', file_path=path)

@app.route('/download/<path:path>')
def download_document(path):
    file_path = os.path.join(DOCUMENTS_FOLDER, path)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')  # accessible sur tout le réseau local