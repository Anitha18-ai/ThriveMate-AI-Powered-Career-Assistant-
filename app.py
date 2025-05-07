import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from services.resume_analyzer import analyze_resume, calculate_ats_score
from services.job_recommender import search_jobs
from services.career_chat import get_career_advice
from utils.firebase_utils import init_firebase
from utils.text_extraction import extract_text_from_file
import config

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "thrivemateappsecretkey")

# Initialize Firebase - with fallback to None if it fails
try:
    firebase_app, storage, db = init_firebase()
except Exception as e:
    logger.warning(f"Firebase initialization failed: {str(e)}. Continuing without Firebase.")
    firebase_app, storage, db = None, None, None

@app.route('/')
def index():
    return render_template(
        'index.html',
        firebase_api_key=os.environ.get("FIREBASE_API_KEY", ""),
        firebase_project_id=os.environ.get("FIREBASE_PROJECT_ID", ""),
        firebase_app_id=os.environ.get("FIREBASE_APP_ID", ""),
        title="ThriveMate - AI Career Assistant"
    )

@app.route('/resume-analyzer')
def resume_analyzer():
    return render_template(
        'resume_analyzer.html',
        firebase_api_key=os.environ.get("FIREBASE_API_KEY", ""),
        firebase_project_id=os.environ.get("FIREBASE_PROJECT_ID", ""),
        firebase_app_id=os.environ.get("FIREBASE_APP_ID", ""),
        title="Resume Analyzer - ThriveMate"
    )

@app.route('/job-recommender')
def job_recommender():
    return render_template(
        'job_recommender.html',
        firebase_api_key=os.environ.get("FIREBASE_API_KEY", ""),
        firebase_project_id=os.environ.get("FIREBASE_PROJECT_ID", ""),
        firebase_app_id=os.environ.get("FIREBASE_APP_ID", ""),
        title="Job Recommender - ThriveMate"
    )

@app.route('/career-chat')
def career_chat():
    return render_template(
        'career_chat.html',
        firebase_api_key=os.environ.get("FIREBASE_API_KEY", ""),
        firebase_project_id=os.environ.get("FIREBASE_PROJECT_ID", ""),
        firebase_app_id=os.environ.get("FIREBASE_APP_ID", ""),
        title="AI Career Chat - ThriveMate"
    )

# API Routes
@app.route('/api/analyze-resume', methods=['POST'])
def api_analyze_resume():
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['resume']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Extract text from the uploaded file
        text = extract_text_from_file(file)
        
        if not text:
            return jsonify({'error': 'Could not extract text from the file'}), 400
            
        # Analyze the resume text
        analysis_results = analyze_resume(text)
        
        # Calculate ATS score
        ats_score = calculate_ats_score(analysis_results)
        
        # Add ATS score to results
        analysis_results['ats_score'] = ats_score
        
        return jsonify(analysis_results)
    
    except Exception as e:
        logger.exception("Error analyzing resume")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search-jobs', methods=['POST'])
def api_search_jobs():
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Required parameters
        keywords = data.get('keywords', '')
        location = data.get('location', '')
        
        # Optional parameters with defaults
        page = data.get('page', 1)
        page_size = data.get('page_size', 10)
        
        # Search for jobs
        jobs = search_jobs(keywords, location, page, page_size)
        
        return jsonify(jobs)
    
    except Exception as e:
        logger.exception("Error searching jobs")
        return jsonify({'error': str(e)}), 500

@app.route('/api/career-advice', methods=['POST'])
def api_career_advice():
    try:
        data = request.json
        
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
            
        message = data['message']
        
        # Get career advice
        response = get_career_advice(message)
        
        return jsonify({'response': response})
    
    except Exception as e:
        logger.exception("Error getting career advice")
        return jsonify({'error': str(e)}), 500

# Handle 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html', title="404 - Page Not Found"), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
