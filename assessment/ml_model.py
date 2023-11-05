import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import random
import json

def get_recommendations(user_input):
    # Load the dataset
    data = pd.read_csv('mini-product-recommender-dataset.csv')

    # Drop rows with missing values in Product Name and Price
    data = data.dropna(subset=['Product Name', 'Price'])

    # Fill missing values in Description and Category
    data['Description'].fillna('Unknown', inplace=True)
    data['Category'].fillna('Others', inplace=True)

    # Convert non-string columns to strings
    data['Product ID'] = data['Product ID'].astype(str)
    data['Price'] = data['Price'].astype(str)

    # Combine Product Name, Description, and Category for better recommendation
    data['Content'] = data['Product Name'] + " " + data['Description'] + " " + data['Category']

    # Tokenize and preprocess the user input
    user_input = " ".join(user_input.split())  # Remove extra spaces

    # Check if the user input keywords exist in any relevant column
    matching_rows = data[data.apply(lambda row: any(keyword.lower() in ' '.join(row).lower() for keyword in user_input.split()), axis=1)]

    if not matching_rows.empty:
        # User input exists, proceed with recommendations

        # Initialize a list for recommendations
        recommendations = []

        # Filter rows where any of the search keywords are found in the 'Content' column
        filtered_data = data[data.apply(lambda row: any(keyword.lower() in row['Content'].lower() for keyword in user_input.split()), axis=1)]

        if not filtered_data.empty:
            # Create a TF-IDF vectorizer
            tfidf_vectorizer = TfidfVectorizer()

            # Fit and transform the product descriptions
            tfidf_matrix = tfidf_vectorizer.fit_transform(filtered_data['Content'])

            # Transform user input
            user_tfidf = tfidf_vectorizer.transform([user_input])

            # Calculate cosine similarity for all product descriptions
            cosine_similarities = linear_kernel(user_tfidf, tfidf_matrix)

            # Get product indices with the highest similarity
            similar_indices = cosine_similarities[0].argsort()[:-4:-1]

            recommendations.extend(filtered_data.iloc[similar_indices].to_dict('records'))

        # Remove duplicates based on 'Product ID' in recommendations
        seen_ids = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec['Product ID'] not in seen_ids:
                seen_ids.add(rec['Product ID'])
                unique_recommendations.append(rec)

        recommendations = unique_recommendations

        # Check if we have fewer than 3 recommendations
        if len(recommendations) < 3:
            # Find more recommendations based on category, description, and name
            additional_recommendations = []

            # Category-based recommendations
            category_matches = data[data['Category'].isin([rec['Category'] for rec in recommendations])]
            additional_recommendations.extend(category_matches.to_dict('records'))

            # Description-based recommendations
            description_matches = data[data.apply(lambda row: any(keyword.lower() in row['Description'].lower() for keyword in user_input.split()), axis=1)]
            additional_recommendations.extend(description_matches.to_dict('records'))

            # Name-based recommendations
            name_matches = data[data.apply(lambda row: any(keyword.lower() in row['Product Name'].lower() for keyword in user_input.split()), axis=1)]
            additional_recommendations.extend(name_matches.to_dict('records'))

            # Remove duplicates based on 'Product ID' in additional_recommendations
            seen_ids = set()
            unique_additional_recommendations = []
            for rec in additional_recommendations:
                if rec['Product ID'] not in seen_ids:
                    seen_ids.add(rec['Product ID'])
                    unique_additional_recommendations.append(rec)

            # Remove duplicates based on 'Product ID' within additional_recommendations
            additional_recommendations = unique_additional_recommendations

            # Remove any duplicates between recommendations and additional_recommendations
            for rec in additional_recommendations:
                if rec['Product ID'] not in seen_ids:
                    seen_ids.add(rec['Product ID'])
                    recommendations.append(rec)

        # Check if we still have fewer than 3 recommendations
        if len(recommendations) < 3:
            # Calculate how many additional random recommendations are needed
            random_needed = 3 - len(recommendations)

            if random_needed > 0:
                # Check if there are enough products in the dataset
                if len(data) < random_needed:
                    # If there are not enough products, select all available
                    random_indices = list(range(len(data)))
                else:
                    # Otherwise, select random recommendations
                    random_indices = random.sample(range(len(data)), random_needed)

                random_recommendations = data.loc[random_indices].to_dict('records')
                recommendations.extend(random_recommendations)

    else:
        # If there are no exact matches, provide random recommendations
        random_indices = random.sample(range(len(data)), 3)
        recommendations = data.loc[random_indices].to_dict('records')

    # Return the recommendations as a JSON object
    return json.dumps(recommendations, indent=4)

