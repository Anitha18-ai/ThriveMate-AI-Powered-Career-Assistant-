from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    firebase_uid = db.Column(db.String(128), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    resume_analyses = db.relationship('ResumeAnalysis', back_populates='user', lazy=True)
    job_searches = db.relationship('JobSearch', back_populates='user', lazy=True)
    saved_jobs = db.relationship('SavedJob', back_populates='user', lazy=True)
    chat_messages = db.relationship('ChatMessage', back_populates='user', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'


class ResumeAnalysis(db.Model):
    __tablename__ = 'resume_analyses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=True)
    resume_text = db.Column(db.Text, nullable=False)
    skills = db.Column(db.JSON, nullable=True, default=[])
    education = db.Column(db.JSON, nullable=True, default=[])
    experience = db.Column(db.JSON, nullable=True, default=[])
    suggestions = db.Column(db.JSON, nullable=True, default=[])
    ats_score = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    user = db.relationship('User', back_populates='resume_analyses')

    def __repr__(self):
        return f'<ResumeAnalysis {self.id} - User {self.user_id}>'


class JobSearch(db.Model):
    __tablename__ = 'job_searches'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    keywords = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=True)
    results_count = db.Column(db.Integer, nullable=True)
    saved_jobs = db.Column(db.JSON, nullable=True, default=[])
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='job_searches')

    def __repr__(self):
        return f'<JobSearch {self.keywords} - User {self.user_id}>'


class SavedJob(db.Model):
    __tablename__ = 'saved_jobs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    job_id = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(512), nullable=True)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='saved_jobs')

    # Unique constraint
    __table_args__ = (db.UniqueConstraint('user_id', 'job_id', name='unique_saved_job'),)

    def __repr__(self):
        return f'<SavedJob {self.title} at {self.company} - User {self.user_id}>'


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    is_user_message = db.Column(db.Boolean, default=True)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='chat_messages')

    def __repr__(self):
        sender = "User" if self.is_user_message else "AI"
        return f'<ChatMessage from {sender} - User {self.user_id}>'
