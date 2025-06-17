from services.resume_analyzer import resume_analysis_route
from services.job_recommender import job_recommendation_route
from services.career_chat import career_chat_route

def register_routes(app):
    app.register_blueprint(resume_analysis_route)
    app.register_blueprint(job_recommendation_route)
    app.register_blueprint(career_chat_route)
