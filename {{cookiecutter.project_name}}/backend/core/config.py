import os
from dotenv import load_dotenv


load_dotenv()


class CONFIG:
    # Flask
    HOST = os.getenv('HOST')
    PORT = int(os.getenv('PORT'))
    SECRET_KEY = os.getenv('SECRET_KEY')
    API_BASE_URL=os.getenv('API_BASE_URL')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    TOKEN_API_KEY = os.getenv("TOKEN_API_KEY")

    {%- if cookiecutter.use_db == "yes" %}

    SQLALCHEMY_DATABASE_URI = (
        f'postgresql://{os.getenv("DB_USER")}:'
        f'{os.getenv("DB_PASSWORD")}@'
        f'{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/'
        f'{os.getenv("DB_NAME")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    {%- endif %}

class DevelopmentConfig(CONFIG):
    DEBUG = True
    TESTING = True


class StagingConfig(CONFIG):
    DEBUG = False
    TESTING = False


class ProductionConfig(CONFIG):
    DEBUG = False
    TESTING = False


ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == 'development':
    APP_CONFIG = DevelopmentConfig()
elif ENVIRONMENT == 'production':
    APP_CONFIG = ProductionConfig()
elif ENVIRONMENT == 'staging':
    APP_CONFIG = StagingConfig()