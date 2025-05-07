from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    """User model for storing user account data"""
    id = db.Column(db.Integer, primary_key=True)
    firebase_uid = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    resume_analyses = db.relationship('ResumeAnalysis', backref='user', lazy=True)
    job_searches = db.relationship('JobSearch', backref='user', lazy=True)
    chat_messages = db.relationship('ChatMessage', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.email}>'

class ResumeAnalysis(db.Model):
    """Model for storing resume analysis results"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=True)
    resume_text = db.Column(db.Text, nullable=False)
    skills = db.Column(db.JSON, nullable=True)
    education = db.Column(db.JSON, nullable=True)
    experience = db.Column(db.JSON, nullable=True)
    suggestions = db.Column(db.JSON, nullable=True)
    ats_score = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ResumeAnalysis {self.id} - User {self.user_id}>'

class JobSearch(db.Model):
    """Model for storing job search queries and results"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    keywords = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=True)
    results_count = db.Column(db.Integer, nullable=True)
    saved_jobs = db.Column(db.JSON, nullable=True)  # List of saved job IDs
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<JobSearch {self.keywords} - User {self.user_id}>'

class SavedJob(db.Model):
    """Model for storing saved job listings"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(512), nullable=True)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Add a unique constraint so users can't save the same job twice
    __table_args__ = (db.UniqueConstraint('user_id', 'job_id', name='unique_saved_job'),)
    
    def __repr__(self):
        return f'<SavedJob {self.title} at {self.company} - User {self.user_id}>'

class ChatMessage(db.Model):
    """Model for storing chat messages"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_user_message = db.Column(db.Boolean, default=True)  # True if user sent it, False if AI response
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        sender = "User" if self.is_user_message else "AI"
        return f'<ChatMessage from {sender} - User {self.user_id}>'