from flask import Flask, render_template, request, send_from_directory
import pandas as pd
import os

app = Flask(__name__)

# Load the dataset
df_movies = pd.read_csv('./data/data.csv', encoding='utf-8')

# Preprocess the dataset
df_movies['genres_list'] = df_movies['genres_list'].apply(eval)  # Convert genres_list from string to list
movie_titles = df_movies['title'].tolist()  # Get all movie titles for the datalist


def search_movies(query, min_rating=0):
    """
    Search for movies by title matching or containing the query,
    and filter by minimum rating.
    """
    # Filter movies whose title matches or contains the query (case-insensitive)
    matching_movies = df_movies[
        df_movies['title'].str.contains(query, case=False, na=False) &
        (df_movies['vote_average'] >= min_rating)
    ]
    # Sort by rating
    return matching_movies.sort_values(by='vote_average', ascending=False).to_dict('records')


@app.route('/')
def home():
    return render_template('index.html', movie_list=movie_titles, search_query="", rating_filter=0)

@app.route('/members')
def members():
    # Example team members
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


if __name__ == '__main__':
    app.run(debug=True)

