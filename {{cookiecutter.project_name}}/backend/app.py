from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
{%- if cookiecutter.use_db == "yes" %}
from flask_migrate import Migrate
{%- endif %}
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from core.config import APP_CONFIG, init_sentry
from routers import routes
{%- if cookiecutter.use_db == "yes" %}
from db.database import db, test_connection
{%- endif %}


ma = Marshmallow()


def create_app():
    """
    Create and configure Flask application instance.
    
    This factory function:
    - Initializes Sentry (production only)
    - Configures Flask app with environment settings
    - Configures JWT authentication
    - Registers health check endpoint
    
    Returns:
        Configured Flask application instance.
    """
    # Initialize Sentry first (will only run in production)
    init_sentry(APP_CONFIG)

    app = Flask(__name__)
    app.config.from_object(APP_CONFIG)
    app.json.sort_keys = False
    
    # Initialize extensions
    {%- if cookiecutter.use_db == "yes" %}
    db.init_app(app)
    Migrate(app, db)
    {%- endif %}
    JWTManager(app)
    ma.init_app(app)

    app.register_blueprint(routes.bp)
    
    # Configure URL prefix for API
    script_name = APP_CONFIG.API_BASE_URL
    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
        script_name: app
    })
    
    @app.route("/api")
    def app_info():
        info_data = {
            "name": f"{{ cookiecutter.project_name }}"
        }
        return jsonify(info_data), 200
    
    {%- if cookiecutter.use_db == "yes" %}
    @app.route("/health")
    def health_app():
        is_db_connected = test_connection()
        if is_db_connected is True:
            status_app = 'ok'
            database_status = "Database connection successful!"
            status_code = 200
        else:
            status_app = 'falied'
            _, database_status = is_db_connected
            status_code = 500
        
        return jsonify({
                "status": status_app,
                "internal_services": {
                  "database": database_status
                }
            }), status_code
    {%- endif %}

    return app


# Create application instance    
app = create_app()
