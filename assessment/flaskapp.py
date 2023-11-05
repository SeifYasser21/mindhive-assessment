# Import the required libraries and modules
from flask import Flask, render_template, request, jsonify
import json
import ml_model

# Create a Flask web application instance
app = Flask(__name__)

# Define a route for the home page
@app.route('/')
def index():
    """
    This route renders the HTML template for the home page.
    """
    return render_template('index.html')

# Define a route for retrieving product recommendations
@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    """
    This route handles POST requests for retrieving product recommendations based on user input.

    It takes the user's input, calls the 'ml_model.get_recommendations' function, and returns the recommendations.

    Returns:
        JSON response containing product recommendations or an error message.
    """
    user_input = request.form.get('user_input')
    recommendation_func = ml_model.get_recommendations(user_input)
    
    if "Product ID" not in recommendation_func:
        # If no recommendations are found, return an error message
        result = {
            "result": "No recommendations found. Please use a valid keyword and try again",
        }
        return jsonify(result)
    else:
        # If recommendations are found, return them as JSON data
        return recommendation_func

# Run the Flask app when this script is executed
if __name__ == '__main__':
    app.run(debug=True)
