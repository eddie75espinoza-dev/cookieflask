import os
import secrets
from dotenv import load_dotenv


load_dotenv()


class Config:
    SECRET_KEY = secrets.token_urlsafe(32)
    HOST = os.getenv('HOST')
    PORT = int(os.getenv('PORT'))
    BASE_URL=os.getenv('BASE_URL')
    TOKEN_SECRET_KEY=os.getenv('TOKEN_SECRET_KEY')
    SUB = int(os.getenv('SUB')) # Identificador usuario token

    {%- if cookiecutter.use_db == "yes" %}

    SQLALCHEMY_DATABASE_URI = (
        f'postgresql://{os.getenv("POSTGRES_USER")}:'
        f'{os.getenv("POSTGRES_PASSWORD")}@'
        f'{os.getenv("POSTGRES_HOST")}:{os.getenv("POSTGRES_PORT")}/'
        f'{os.getenv("POSTGRES_DB")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    {%- endif %}

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True


class StagingConfig(Config):
    DEBUG = False
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == 'development':
    APP_CONFIG = DevelopmentConfig
elif ENVIRONMENT == 'production':
    APP_CONFIG = ProductionConfig
elif ENVIRONMENT == 'staging':
    APP_CONFIG = StagingConfig