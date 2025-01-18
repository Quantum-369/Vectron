from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from test import generate_response
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='static')
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Serve static files
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# Main chat endpoint
@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message")

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Generate response using RAG system
        llm_response = generate_response(user_message)
        
        return jsonify({"response": llm_response})

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Server error",
            "message": "An unexpected error occurred. Please try again later."
        }), 500

if __name__ == "__main__":
    # Create static folder if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
    
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV") == "development"
    
    app.run(host="0.0.0.0", port=port, debug=debug)