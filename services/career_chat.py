from flask import request, jsonify
import os
import requests
import logging
from typing import List
import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_career_advice(message: str) -> str:
    """
    Get career advice using Hugging Face Inference API with improved prompt.
    """
    logger.info(f"Fetching career advice for message: {message}")

    api_key = os.getenv('HUGGINGFACE_API_KEY', getattr(config, 'HUGGINGFACE_API_KEY', None))
    api_url = getattr(config, 'HUGGINGFACE_API_URL', None)

    if not api_key or not api_url:
        logger.error("Missing Hugging Face API key or URL.")
        return "⚠️ Career assistant is currently unavailable. Please try again later."

    # Stronger, guided prompt
    prompt = (
        "You are a professional career coach with 10+ years of experience helping candidates prepare for job interviews. "
        "Answer the following career-related question with clear guidance, a sample answer (if relevant), actionable advice, and common mistakes to avoid. "
        "Write in a helpful, friendly tone.\n\n"
        f"Question: {message}"
    )

    payload = {
        "inputs": prompt,
        "options": {"wait_for_model": True}
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        logger.info(f"Response from Hugging Face API: {result}")

        if isinstance(result, list) and len(result) > 0 and 'generated_text' in result[0]:
            generated_text = result[0]['generated_text']
            return clean_response(generated_text, prompt)
        else:
            logger.error("Unexpected response format from Hugging Face API.")
            return "❌ Sorry, I couldn't generate a response. Please rephrase your question."

    except requests.exceptions.RequestException as e:
        logger.exception("Request to Hugging Face API failed.")
        return "🚫 Network error occurred. Please try again later."

def clean_response(response_text: str, prompt_text: str) -> str:
    """
    Clean the model's response by removing the prompt and unnecessary prefixes.
    """
    cleaned = response_text.replace(prompt_text, "").strip()

    if cleaned:
        cleaned = cleaned[0].upper() + cleaned[1:]

    return cleaned if cleaned else "I'm here to help! Could you please provide more details about your career question?"

def get_similar_questions(query: str = "") -> List[str]:
    """
    Return sample similar questions to guide the user.
    """
    return [
        "How can I make my resume stand out?",
        "What are the best tips to prepare for interviews?",
        "How do I transition into a different career field?",
        "What skills should I learn for a career in data science?",
        "How can I find job opportunities that match my profile?",
    ]

def career_chat_route(app):
    """
    Register the /career-chat POST route with the Flask app.
    """
    @app.route('/career-chat', methods=['POST'])
    def career_chat():
        try:
            data = request.json
            user_input = data.get('message', '')

            if not user_input:
                return jsonify({'error': 'No message provided'}), 400

            response = get_career_advice(user_input)
            return jsonify({'response': response})

        except Exception as e:
            logger.exception("Error in career chat route")
            return jsonify({'error': str(e)}), 500
