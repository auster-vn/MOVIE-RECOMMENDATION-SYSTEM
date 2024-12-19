from flask import Flask, render_template, request, send_from_directory
import pandas as pd
import os
import requests
from dotenv import load_dotenv

# Load API Key from .env file
load_dotenv()
api_key = os.getenv("API_KEY")

app = Flask(__name__)

# Load data from the updated data.csv
df_movies = pd.read_csv('/home/cp/project/webs/data/data.csv', encoding='utf-8')

# Ensure numeric columns are properly converted
df_movies['vote_average'] = pd.to_numeric(df_movies['vote_average'], errors='coerce')
df_movies['vote_count'] = pd.to_numeric(df_movies['vote_count'], errors='coerce')
df_movies['runtime'] = pd.to_numeric(df_movies['runtime'], errors='coerce')

# Convert 'genres_list' and 'actor' columns from string to list
df_movies['genres_list'] = df_movies['genres_list'].apply(eval)
df_movies['actor'] = df_movies['actor'].apply(eval)

# Generate movie titles for the datalist
movie_titles = df_movies['title'].tolist()

# Function to fetch poster from TMDb API
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    response = requests.get(url).json()
    poster_path = response.get('poster_path')
    return f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else "https://via.placeholder.com/150"

# Search function
def search_movies(query, min_rating=0):
    """
    Search for movies by title matching or containing the query,
    and filter by minimum rating.
    """
    matching_movies = df_movies[
        df_movies['title'].str.contains(query, case=False, na=False) &
        (df_movies['vote_average'] >= min_rating)
    ]
    results = []
    for _, movie in matching_movies.iterrows():
        poster_url = fetch_poster(movie['id'])
        results.append({
            'title': movie['title'],
            'poster_path': poster_url,
            'vote_average': movie['vote_average']
        })
    return results

@app.route('/')
def home():
    return render_template('index.html', movie_list=movie_titles, search_query="", rating_filter=0)

@app.route('/recommend', methods=['POST'])
def recommend():
    # Get form data
    movie_name = request.form['movie_name']
    min_rating = float(request.form['rating'])
    # Search for matching movies
    recommendations = search_movies(movie_name, min_rating)
    return render_template(
        'index.html',
        movie_list=movie_titles,
        recommendations=recommendations,
        search_query=movie_name,
        rating_filter=min_rating
    )

@app.route('/members')
def members():
    team_members = [
        {"MSSV": "22110158", "Hovaten": "Tran Chau Phu"},
        {"MSSV": "22110170", "Hovaten": "Ho Minh Quan"},
        {"MSSV": "22110123", "Hovaten": "Le Nguyen Duc Nam"},
        {"MSSV": "22110124", "Hovaten": "Le Thi Kim Nga"},
        {"MSSV": "22110155", "Hovaten": "Tran Nguyen Thanh Phong"},
    ]
    return render_template('members.html', members=team_members)

@app.route('/documents')
def documents():
    doc_folder = './static/doc'
    files = os.listdir(doc_folder)
    return render_template('documents.html', files=files)

@app.route('/doc/<filename>')
def serve_pdf(filename):
    return send_from_directory('./static/doc', filename)

if __name__ == '__main__':
    app.run(debug=True)