import os
from dotenv import load_dotenv


load_dotenv()


class CONFIG:
    SECRET_KEY = os.getenv('SECRET_KEY')
    HOST = os.getenv('HOST')
    PORT = int(os.getenv('PORT'))
    BASE_URL = os.getenv('BASE_URL')
    TOKEN_SECRET_KEY = os.getenv('SECRET_KEY')
    SUB = os.getenv('SUB') # Identificador usuario token

    {%- if cookiecutter.use_db == "yes" %}

    SQLALCHEMY_DATABASE_URI = (
        f'postgresql://{os.getenv("POSTGRES_USER")}:'
        f'{os.getenv("POSTGRES_PASSWORD")}@'
        f'{os.getenv("POSTGRES_HOST")}:{os.getenv("POSTGRES_PORT")}/'
        f'{os.getenv("POSTGRES_DB")}'
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
    APP_CONFIG = DevelopmentConfig
elif ENVIRONMENT == 'production':
    APP_CONFIG = ProductionConfig
elif ENVIRONMENT == 'staging':
    APP_CONFIG = StagingConfig