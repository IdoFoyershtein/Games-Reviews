import pytest
import urllib.parse
from pymongo import MongoClient
from python_files import app
from python_files import database
import os

# Setup mongoodb test client and test database
@pytest.fixture(scope='module')
def mongodb():
    mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://mongo:27017/games_reviews_db')
    client = MongoClient(mongodb_uri)
    db = client["games_reviews_db"]
    yield db

# Fixture function to create a test client for Flask application and use the test database for the tests
@pytest.fixture
def client(mongodb):
    # Set Flask application config to testing mode
    app.app.config['TESTING'] = True

    app.app.config['MONGODB_URI'] = 'mongodb://mongo:27017/games_reviews_db'
    db = mongodb
    reviews = db['reviews']

    # Create a test client for Flask application, and yield it for use in test cases
    with app.app.test_client() as client:
        with app.app.app_context():
            # Initialize anything if needed
            pass
        yield client

# Fixture function to provide sample review data for testing
@pytest.fixture
def sample_review_data():
    # Provide some sample review data with a review and a rating for testing
    return {'user_review': 'Test review', 'user_rating': 5}

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200

def test_submit_review_route(client):
    response = client.post('/submit_review', data={'userreview': 'Test review', 'ratelist': '5'})
    assert response.status_code == 302

def test_search_reviews_route(client):
    query = 'test' # Define the search query

    # Encode the search query to ensure special characters are properly handled
    encoded_query = urllib.parse.quote(query)
    
    response = client.get(f'/search?query={encoded_query}')

    assert response.status_code == 302

def test_delete_review_route(client):
    reviews_list = database.get_all_reviews()

    if reviews_list:
        # Sort the list of reviews by '_id' in descending order
        reviews_list.sort(key=lambda x: x['_id'], reverse=True)

        # Get the ID of the last review
        last_review_id = reviews_list[0]['_id']

        response = client.post('/delete_review', data={'review_id': last_review_id})
        assert response.status_code == 302
    else:
        pytest.skip("No reviews found in the database for deletion test")

# Test function to check saving review data to the database
def test_save_to_database(sample_review_data):
    # Number of reviews in the database before saving new data
    count_before_saving = len(database.get_all_reviews())
    
    # Save the sample review data to the database
    response = database.save_to_database(sample_review_data['user_review'], sample_review_data['user_rating'])
    
    # Number of reviews in the database after saving new data
    count_after_saving = len(database.get_all_reviews())

    # Assert that the count of reviews increased by 1 after saving
    # (The save was successful)
    assert count_before_saving == count_after_saving - 1

# Test function to check getting all the reviews
def test_get_all_reviews():
    # Checks if the list from the function in the db file is the same as the list from the collection function
    assert database.get_all_reviews() == list(database.reviews.find())

# Test function to check calculation of average rating
def test_get_avg_rate():
    avg_rate = 0.0 # Initialize the variable to store the sum of ratings
    count = 0 # Initialize the variable to store the count of reviews

    # Iterate through each review in the collection
    for review in database.reviews.find():
        # Add the rating of each review to the sum
        avg_rate += review['rating']
        # Increment the count of reviews
        count += 1

    # Chrck if there are reviews in the database
    if count != 0:
        # If there are reviews, calculate the average rating
        avg_rate = round(avg_rate / count, 1)
    else:
        # If there are no reviews, set the average rating to 0
        avg_rate = 0
    
    # Assert that the average rating retrieved from the database matches the calculated average rating
    assert database.get_avg_rate() == avg_rate

# Test function to check searching reviews in the database
def test_search_reviews_in_database():
    query = 'test' # Define the search query

    # Call the function to search reviews in the database
    func_search_results, func_total_occurrences = database.search_reviews_in_database(query)

    # Find reviews containing the search query using MongoDB's find method
    search_results = list(database.reviews.find({"review": {"$regex": query, "$options": "i"}}))
    
    # Convert ObjectId to string for each review in search results
    for review in search_results:
        review['_id'] = str(review['_id'])

    # Count the total occurrences of the query in the database
    total_occurrences = 0
    for review in search_results:
        total_occurrences += review['review'].lower().count(query.lower())
    
    # Assert that the search results and total occurrences match with the function results
    assert func_search_results == search_results and func_total_occurrences == total_occurrences

# Test function to check deletion of a review from the database
def test_delete_review_from_database():
    # Get the list of all reviews from the database
    reviews_list = database.get_all_reviews()

    # Check if there are reviews in the database
    if reviews_list:
        # Count the number of reviews before deletion
        count_before_deleting = len(reviews_list)
        
        # Get the ID of the last review in the list and delete it
        last_review_id = reviews_list[-1]['_id']
        response = database.delete_review_from_database(str(last_review_id))
        
        # Count the number of reviews after deletion
        count_after_deleting = len(database.get_all_reviews())

        # Assert that the count of reviews decreased by 1 after deletion
        # (The delete was successful)
        assert count_before_deleting == count_after_deleting + 1
    else:
        # Skip the test if there are no reviews in the database
        pytest.skip("No reviews found in the database for deletion test")
