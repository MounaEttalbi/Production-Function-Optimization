from flask import Flask, render_template, request
import pandas as pd
import plotly.graph_objects as go
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return render_template('index.html', message='No file part')

    file = request.files['file']
    if file.filename == '':
        return render_template('index.html', message='No selected file')

    if file:
        try:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            data = pd.read_csv(filepath, encoding='latin1')

            # Calcul des statistiques d'optimisation
            valeur_optimisee = data['Pieces_Produites'].sum() - data['Pieces_Rejetees'].sum()
            temps_de_travail = data['Temps_Operationnel (minutes)'].sum()
            matiere_premiere_a = data['Coût_Production (USD)'].sum()
            matiere_premiere_b = data['Arret_Machine (minutes)'].sum()

            # Préparation des résultats pour l'affichage
            results = {
                'valeur_optimisee': valeur_optimisee,
                'temps_de_travail': temps_de_travail,
                'matiere_premiere_a': matiere_premiere_a,
                'matiere_premiere_b': matiere_premiere_b
            }

            # Génération du graphique combiné par date
            fig = go.Figure()

            # Ajout des différentes séries au graphique
            fig.add_trace(go.Scatter(x=data['Date'], y=data['Pieces_Produites'], mode='lines+markers', name='Pièces Produites'))
            fig.add_trace(go.Scatter(x=data['Date'], y=data['Pieces_Rejetees'], mode='lines+markers', name='Pièces Rejetées'))
            fig.add_trace(go.Scatter(x=data['Date'], y=data['Coût_Production (USD)'], mode='lines+markers', name='Coût de Production (USD)'))
            fig.add_trace(go.Scatter(x=data['Date'], y=data['Arret_Machine (minutes)'], mode='lines+markers', name='Temps d\'Arrêt (minutes)'))

            fig.update_layout(
                title='Indicateurs de Production par Date',
                xaxis_title='Date',
                yaxis_title='Valeurs',
                legend_title='Indicateurs'
            )

            graph_html = fig.to_html(full_html=False)

            stats = data.describe()
            return render_template('index.html', message='File uploaded successfully!', stats=stats.to_html(), results=results, graph=graph_html)
        except Exception as e:
            return render_template('index.html', message=f'Error processing file: {e}')

if __name__ == '__main__':
    app.run(debug=True)
