import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from services.resume_analyzer import analyze_resume, calculate_ats_score
from services.job_recommender import search_jobs
from services.career_chat import get_career_advice
from utils.firebase_utils import init_firebase
from utils.text_extraction import extract_text_from_file
from models import db, User, ResumeAnalysis, JobSearch, SavedJob, ChatMessage
import config

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "thrivemateappsecretkey")

# Configure database
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    # Initialize database
    db.init_app(app)

    # Create database tables
    with app.app_context():
        db.create_all()
        logger.info("Database tables created")
else:
    logger.warning("DATABASE_URL not found. Running without database functionality.")

# Initialize Firebase - with fallback to None if it fails
try:
    firebase_app, storage, firestore_db = init_firebase()
except Exception as e:
    logger.warning(f"Firebase initialization failed: {str(e)}. Continuing without Firebase.")
    firebase_app, storage, firestore_db = None, None, None

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

# User Management Routes
@app.route('/api/user/create', methods=['POST'])
def create_user():
    try:
        data = request.json
        
        if not data or 'firebase_uid' not in data or 'email' not in data:
            return jsonify({'error': 'Missing required user data'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(firebase_uid=data['firebase_uid']).first()
        if existing_user:
            return jsonify({'message': 'User already exists', 'user_id': existing_user.id}), 200
        
        # Create new user
        new_user = User(
            firebase_uid=data['firebase_uid'],
            email=data['email'],
            display_name=data.get('display_name')
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        logger.info(f"New user created: {new_user.email}")
        return jsonify({'message': 'User created successfully', 'user_id': new_user.id}), 201
    
    except Exception as e:
        db.session.rollback()
        logger.exception("Error creating user")
        return jsonify({'error': str(e)}), 500

# Resume Analysis Routes
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
        
        # Save to database if user is logged in
        user_id = request.form.get('user_id')
        if user_id:
            try:
                # Create a new resume analysis record
                resume_analysis = ResumeAnalysis(
                    user_id=user_id,
                    filename=file.filename,
                    resume_text=text,
                    skills=analysis_results.get('skills', []),
                    education=analysis_results.get('education', []),
                    experience=analysis_results.get('experience', []),
                    suggestions=analysis_results.get('suggestions', []),
                    ats_score=ats_score
                )
                
                db.session.add(resume_analysis)
                db.session.commit()
                
                # Add the database ID to the results
                analysis_results['id'] = resume_analysis.id
                
                logger.info(f"Resume analysis saved for user {user_id}")
            except Exception as e:
                logger.error(f"Error saving resume analysis: {str(e)}")
                db.session.rollback()
                # Continue without saving to database
        
        return jsonify(analysis_results)
    
    except Exception as e:
        logger.exception("Error analyzing resume")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/<int:user_id>/resume-analyses', methods=['GET'])
def get_user_resume_analyses(user_id):
    try:
        analyses = ResumeAnalysis.query.filter_by(user_id=user_id).order_by(ResumeAnalysis.created_at.desc()).all()
        
        results = []
        for analysis in analyses:
            results.append({
                'id': analysis.id,
                'filename': analysis.filename,
                'skills': analysis.skills,
                'education': analysis.education,
                'experience': analysis.experience,
                'ats_score': analysis.ats_score,
                'created_at': analysis.created_at.isoformat()
            })
        
        return jsonify({'analyses': results})
    
    except Exception as e:
        logger.exception("Error getting user resume analyses")
        return jsonify({'error': str(e)}), 500

# Job Search Routes
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
        
        # Save search to database if user is logged in
        user_id = data.get('user_id')
        if user_id and jobs.get('jobs'):
            try:
                # Create a new job search record
                job_search = JobSearch(
                    user_id=user_id,
                    keywords=keywords,
                    location=location or '',
                    results_count=jobs.get('total_jobs', 0)
                )
                
                db.session.add(job_search)
                db.session.commit()
                
                logger.info(f"Job search saved for user {user_id}")
            except Exception as e:
                logger.error(f"Error saving job search: {str(e)}")
                db.session.rollback()
                # Continue without saving to database
        
        return jsonify(jobs)
    
    except Exception as e:
        logger.exception("Error searching jobs")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/<int:user_id>/save-job', methods=['POST'])
def save_job(user_id):
    try:
        data = request.json
        
        if not data or 'job_id' not in data or 'title' not in data or 'company' not in data:
            return jsonify({'error': 'Missing required job data'}), 400
        
        # Check if job is already saved
        existing_job = SavedJob.query.filter_by(user_id=user_id, job_id=data['job_id']).first()
        if existing_job:
            return jsonify({'message': 'Job already saved', 'job_id': existing_job.id}), 200
        
        # Create new saved job
        saved_job = SavedJob(
            user_id=user_id,
            job_id=data['job_id'],
            title=data['title'],
            company=data['company'],
            location=data.get('location', ''),
            description=data.get('description', ''),
            url=data.get('url', '')
        )
        
        db.session.add(saved_job)
        db.session.commit()
        
        logger.info(f"Job saved for user {user_id}: {data['title']} at {data['company']}")
        return jsonify({'message': 'Job saved successfully', 'job_id': saved_job.id}), 201
    
    except Exception as e:
        db.session.rollback()
        logger.exception("Error saving job")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/<int:user_id>/saved-jobs', methods=['GET'])
def get_saved_jobs(user_id):
    try:
        saved_jobs = SavedJob.query.filter_by(user_id=user_id).order_by(SavedJob.saved_at.desc()).all()
        
        results = []
        for job in saved_jobs:
            results.append({
                'id': job.id,
                'job_id': job.job_id,
                'title': job.title,
                'company': job.company,
                'location': job.location,
                'description': job.description,
                'url': job.url,
                'saved_at': job.saved_at.isoformat()
            })
        
        return jsonify({'saved_jobs': results})
    
    except Exception as e:
        logger.exception("Error getting saved jobs")
        return jsonify({'error': str(e)}), 500

# Career Chat Routes
@app.route('/api/career-advice', methods=['POST'])
def api_career_advice():
    try:
        data = request.json
        
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
            
        user_message = data['message']
        
        # Get career advice
        ai_response = get_career_advice(user_message)
        
        # Save chat messages to database if user is logged in
        user_id = data.get('user_id')
        if user_id:
            try:
                # Save user message
                user_chat_message = ChatMessage(
                    user_id=user_id,
                    is_user_message=True,
                    message=user_message
                )
                
                # Save AI response
                ai_chat_message = ChatMessage(
                    user_id=user_id,
                    is_user_message=False,
                    message=ai_response
                )
                
                db.session.add(user_chat_message)
                db.session.add(ai_chat_message)
                db.session.commit()
                
                logger.info(f"Chat messages saved for user {user_id}")
            except Exception as e:
                logger.error(f"Error saving chat messages: {str(e)}")
                db.session.rollback()
                # Continue without saving to database
        
        return jsonify({'response': ai_response})
    
    except Exception as e:
        logger.exception("Error getting career advice")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/<int:user_id>/chat-history', methods=['GET'])
def get_chat_history(user_id):
    try:
        chat_messages = ChatMessage.query.filter_by(user_id=user_id).order_by(ChatMessage.created_at).all()
        
        results = []
        for message in chat_messages:
            results.append({
                'id': message.id,
                'sender': 'user' if message.is_user_message else 'ai',
                'message': message.message,
                'created_at': message.created_at.isoformat()
            })
        
        return jsonify({'chat_history': results})
    
    except Exception as e:
        logger.exception("Error getting chat history")
        return jsonify({'error': str(e)}), 500

# Handle 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html', title="404 - Page Not Found"), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
