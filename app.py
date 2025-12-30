from flask import Flask, render_template, jsonify, request
import pandas as pd
import json
import os
from datetime import datetime
import plotly
import plotly.express as px
import plotly.graph_objects as go

app = Flask(__name__)


# Загрузка данных
def load_data():
    try:
        # В реальном проекте здесь будет загрузка из API или базы данных
        with open('data/sample_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {
            'teams': [],
            'players': [],
            'matches': [],
            'stats': {}
        }

@app.route('/')
def index():
    data = load_data()
    return render_template('index.html', 
                         teams_count=len(data['teams']),
                         players_count=len(data['players']),
                         matches_count=len(data['matches']))

@app.route('/api/teams')
def get_teams():
    data = load_data()
    return jsonify(data['teams'])

@app.route('/api/players')
def get_players():
    data = load_data()
    return jsonify(data['players'])

@app.route('/api/matches')
def get_matches():
    data = load_data()
    return jsonify(data['matches'])

@app.route('/api/stats')
def get_stats():
    data = load_data()
    
    # Создание графиков
    if data['players']:
        df = pd.DataFrame(data['players'])
        fig = px.bar(df.head(10), x='name', y='goals', 
                    title='Топ 10 бомбардиров')
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        return jsonify({
            'graph': graphJSON,
            'top_scorer': max(data['players'], key=lambda x: x['goals']),
            'avg_goals': sum(p['goals'] for p in data['players']) / len(data['players'])
        })
    
    return jsonify({})

@app.route('/teams')
def teams_page():
    data = load_data()
    return render_template('teams.html', teams=data['teams'])

@app.route('/players')
def players_page():
    data = load_data()
    return render_template('players.html', players=data['players'])

@app.route('/matches')
def matches_page():
    data = load_data()
    return render_template('matches.html', matches=data['matches'])

@app.route('/search')
def search():
    query = request.args.get('q', '')
    data = load_data()
    
    results = {
        'players': [p for p in data['players'] if query.lower() in p['name'].lower()],
        'teams': [t for t in data['teams'] if query.lower() in t['name'].lower()]
    }
    
    return render_template('search.html', results=results, query=query)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=20000)
