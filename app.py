from flask import Flask, session
from config import config, Config
from database import init_db, populate_sample_data, update_database_schema
import json
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from routes.auth import auth_bp
from routes.main import main_bp
from routes.team import team_bp
from routes.api import api_bp
from routes.mentor import mentor_bp
from routes.profile import profile_bp

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    config[config_name].init_app(app)
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(team_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(mentor_bp)
    app.register_blueprint(profile_bp)
    
    @app.template_filter('from_json')
    def from_json(value):
        try:
            return json.loads(value) if value else []
        except (ValueError, TypeError):
            return []
    
    @app.context_processor
    def inject_user():
        return dict(
            current_user_id=session.get('user_id'),
            current_username=session.get('username')
        )
    
    @app.errorhandler(404)
    def not_found_error(error):
        return "Page not found", 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return "Internal server error", 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return "Access forbidden", 403
    
    return app

def initialize_database():
    try:
        init_db()
        print("Database tables created.")
        
        print("Updating database schema...")
        update_database_schema()
        print("Database schema updated.")
        
        print("Populating sample data...")
        populate_sample_data()
        print("Sample data populated.")
        
        print("Testing AI evaluator import...")
        try:
            from ai_evaluator import get_evaluator
            evaluator = get_evaluator()
            print(f"AI evaluator loaded successfully: {type(evaluator).__name__}")
        except Exception as e:
            print(f"Warning: AI evaluator import failed: {e}")
            print("The application will still work, but AI evaluation may not function properly.")
        
    except Exception as e:
        print(f"Database initialization error: {e}")
        raise

if __name__ == '__main__':
    app = create_app()
    
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    
    initialize_database()
    
    print(f"Running in {app.config.get('ENV', 'development')} mode")
    print(f"Debug: {app.config.get('DEBUG', False)}")
    print(f"Using mock evaluator: {app.config.get('USE_MOCK_EVALUATOR', True)}")
    
    app.run(
        debug=Config.DEBUG,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000))
    )