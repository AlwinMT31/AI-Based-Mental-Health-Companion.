import os
import pandas as pd
import nltk
import requests
from flask import Flask, request, jsonify, render_template
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

# Download NLTK data
nltk.download('punkt')

# Configure OpenRouter API
OPENROUTER_API_KEY = "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"  # Replace with your OpenRouter API key
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

# Initialize Flask app
app = Flask(__name__)

# Load and preprocess CSV data
try:
    data = pd.read_csv('chatbotData.csv')
    data = data.dropna(subset=['input', 'output'])  # Drop rows with NaN
    data = data.drop_duplicates(subset=['input'])  # Keep only unique inputs
    inputs = data['input'].tolist()
    outputs = data['output'].tolist()
    intents = [f"intent_{i}" for i in range(len(inputs))]
    print(f"Loaded {len(inputs)} unique inputs from CSV.")
except Exception as e:
    print(f"Error loading CSV: {e}")
    inputs, outputs, intents = [], [], []

# Train Naive Bayes model with better handling
if inputs:
    model = make_pipeline(TfidfVectorizer(), MultinomialNB())
    model.fit(inputs, intents)
    print("Naive Bayes model trained successfully.")
else:
    print("No data to train model. Using OpenRouter only.")

# OpenRouter API function
def get_openrouter_response(query):
    try:
        payload = {
            "model": "mistralai/mixtral-8x7b-instruct",
            "messages": [
                {"role": "system", "content": "You are an UI/UX design assistance Chatbot."},
                {"role": "user", "content": query}
            ],
            "max_tokens": 500
        }
        print(f"Sending to OpenRouter: {payload}")  # Debug payload
        response = requests.post(OPENROUTER_API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        result = response.json()
        api_response = result['choices'][0]['message']['content'].strip()
        print(f"OpenRouter response: {api_response}")  # Debug API output
        return api_response
    except Exception as e:
        error_msg = f"Sorry, I couldn’t process that. Error: {str(e)}"
        print(error_msg)
        return error_msg

# Route for homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route for chatbot response
@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json['message'].lower()
        print(f"User message: {user_message}")

        if inputs:  # If we have trained data
            predicted_intent = model.predict([user_message])[0]
            intent_index = int(predicted_intent.split('_')[1])
            print(f"Predicted intent: {predicted_intent}, Index: {intent_index}")

            # Check if intent matches CSV and confidence is high
            probas = model.predict_proba([user_message])[0]
            max_proba = max(probas)
            print(f"Prediction confidence: {max_proba}")

            if intent_index < len(outputs) and max_proba > 0.7:  # Threshold for CSV match
                response = outputs[intent_index]
                print(f"Response from CSV: {response}")
            else:
                response = get_openrouter_response(user_message)
                print(f"Response from OpenRouter (low confidence or out of range): {response}")
        else:
            response = get_openrouter_response(user_message)
            print(f"Response from OpenRouter (no CSV data): {response}")

        return jsonify({"response": response})
    except Exception as e:
        error_msg = f"Error processing request: {str(e)}"
        print(error_msg)
        return jsonify({"response": error_msg})

if __name__ == '__main__':
    app.run(debug=True)

    
