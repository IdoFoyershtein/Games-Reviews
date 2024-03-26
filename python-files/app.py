from flask import Flask, request, render_template, redirect, url_for, session
from urllib.parse import quote, unquote
from database import *
import os

# Initialize Flask app
app = Flask(__name__)

# Use environment variable for MongoDB URI or default to Docker Compose service name
mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://mongo:27017/')

# Connect to MongoDB
client = MongoClient(mongodb_uri)

# Accessing a specific database called 'appdb' within the MongoDB server
db = client['games_reviews_db']

# Accessing a collection named 'reviews' within the 'appdb' database
reviews = db['reviews']

# Set a secret key for the session
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Route for the home page
@app.route('/')
def index():
    # Retrieve all reviews and average rating
    reviews = get_all_reviews()
    avg_rate = get_avg_rate()

    # Retrieve search query, search results, and total occurrences from session variables
    search_query = session.get('search_query', '')
    search_results = session.pop('search_results', None)
    total_occurrences = session.pop('total_occurrences', 0)
    
    # If search_results is not None, assign its value to the reviews
    if search_results is not None:
        reviews = search_results
    
    for i in range(len(reviews)):
        reviews[i]['review'] = unquote(reviews[i]['review'])

    # If search_query is an empty string, set total_occurrences to 0
    if search_query == '':
        total_occurrences = 0
    
    # Render the index.html template with the retrieved reviews and average rating
    return render_template('index.html', reviews=reviews, avg_rate=avg_rate, query=search_query, total_occurrences=total_occurrences)

# Route for submitting a review
@app.route('/submit_review', methods=['POST'])
def submit():
    # Get user review and rating from the submitted form
    user_review = request.form['userreview']
    user_rating = int(request.form['ratelist'])

    # Encode the search query to ensure special characters are properly handled
    encoded_review = quote(user_review)

    # Call a function to save the user review and rating to the database
    response = save_to_database(encoded_review, user_rating)
    print(response)

    # Redirect to the home page to display the updated list of reviews and average rating after submitting a review
    return redirect(url_for('index'))

# Route for deleting a review
@app.route('/delete_review', methods=['POST'])
def delete_review():
    # Get the ID of the review to be deleted from the submitted form
    review_id = request.form['review_id']
    
    # Call a function to delete the review from the database based on the review_id
    response = delete_review_from_database(review_id)
    print(response)
    
    # Redirect to the home page to display the updated list of reviews and average rating after deleting a review
    return redirect(url_for('index'))

# Route for searching reviews
@app.route('/search')
def search_reviews():
    # Get the search query from the URL parameters
    search_query  = request.args.get('query')
    
    # Encode the search query to ensure special characters are properly handled
    encoded_query = quote(search_query)

    # Call the function to retrieve reviews, passing the query
    search_results, total_occurrences = search_reviews_in_database(encoded_query)
    
    # Store search results and total occurrences in session variables
    session['search_query'] = search_query
    session['search_results'] = search_results
    session['total_occurrences'] = total_occurrences

    # Redirect to the home page to display the search results and total occurrences
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
