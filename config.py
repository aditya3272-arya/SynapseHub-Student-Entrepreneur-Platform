import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kidpreneur_secret_key_2024'
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
  
    DATABASE_NAME = os.environ.get('DATABASE_NAME') or 'synapsehub.db'
    
   
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'static/uploads'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16777216))  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
   
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
   
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY') or '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'
    GROQ_API_URL = os.environ.get('GROQ_API_URL') or 'https://api.groq.com/openai/v1/chat/completions'
    GROQ_MODEL = os.environ.get('GROQ_MODEL') or 'llama-3.3-70b-versatile'
    USE_MOCK_EVALUATOR = os.environ.get('USE_MOCK_EVALUATOR', 'True').lower() == 'true'  
    
    @staticmethod
    def init_app(app):
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class DevelopmentConfig(Config):
    DEBUG = True
    USE_MOCK_EVALUATOR = True  

class ProductionConfig(Config):
    DEBUG = False
    USE_MOCK_EVALUATOR = False 

class TestingConfig(Config):
    TESTING = True
    DATABASE_NAME = ':memory:' 
    USE_MOCK_EVALUATOR = True  

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}