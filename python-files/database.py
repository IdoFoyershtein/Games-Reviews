from pymongo import MongoClient
from bson.objectid import ObjectId
import os

# Use environment variable for MongoDB URI or default to Docker Compose service name
mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://mongo:27017/')

# Connect to MongoDB
client = MongoClient(mongodb_uri)

# Accessing a specific database called 'appdb' within the MongoDB server
db = client['games_reviews_db']

# Accessing a collection named 'reviews' within the 'appdb' database
reviews = db['reviews']

# Function to save a user's review and rating to the database
def save_to_database(user_review, user_rating):
    
    reviews.insert_one({'review': user_review, 'rating': user_rating})

    # Return a success message
    return "review added to database successfully!"

# Function to retrieve all reviews from the database
def get_all_reviews():
    return list(reviews.find())

# Function to calculate the average rating of all reviews in the database
def get_avg_rate():
    
    avg_rate = 0.0
    count = 0

    # Iterate through each review in the collection
    for review in get_all_reviews():
        avg_rate += review['rating']
        count += 1

    # Calculate the average rating if there are reviews in the database
    if count != 0:
        avg_rate = round(avg_rate / count, 1)
    else:
        avg_rate = 0

    return avg_rate

# Function to delete a review from the database based on its ID
def delete_review_from_database(review_id):

    reviews.delete_one({"_id": ObjectId(review_id)})

    # Return a success message
    return "review deleted from database successfully!"

# Function to search reviews in the database
def search_reviews_in_database(query):
    # Find reviews containing the search query
    search_results = list(reviews.find({"review": {"$regex": query, "$options": "i"}}))
    
    # Convert ObjectId to string
    for review in search_results:
        review['_id'] = str(review['_id'])

    # Count the total occurrences of the query in the db
    total_occurrences = 0
    for review in search_results:
        total_occurrences += review['review'].lower().count(query.lower())

    return search_results, total_occurrences
