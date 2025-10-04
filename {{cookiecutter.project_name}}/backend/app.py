import json
import uuid
from flask import Flask, jsonify, g, request
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
{%- if cookiecutter.use_db == "yes" %}
from flask_migrate import Migrate
{%- endif %}
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from core.config import APP_CONFIG, init_sentry
from logs import logs_config
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

    @app.before_request
    def log_request_info():
        """
        Log incoming request information with sensitive data filtered.
        
        This function runs before each request and logs:
        - Request ID (unique identifier)
        - HTTP method
        - URL (with sensitive query params filtered)
        - Headers (with Authorization and other sensitive headers filtered)
        - Query parameters (with sensitive values filtered)
        - JSON body (with sensitive fields filtered)
        """
        g.request_id = str(uuid.uuid4())
        
        # Build raw log data
        log_data = {
            "request_id": g.request_id,
            "method": request.method,
            "url": request.url,
            "headers": dict(request.headers),
            "args": request.args.to_dict(),
            "json_data": request.get_json(silent=True)
        }
        
        logs_config.logger.info(f"Request: {json.dumps(log_data)}")

    @app.after_request
    def log_response_info(response):
        """
        Log outgoing response information with sensitive data filtered.
        
        This function runs after each request and logs:
        - Request ID (correlation with request)
        - Status code
        - Response headers (with sensitive headers filtered)
        - Response body (with sensitive data filtered)
        
        Args:
            response: Flask response object.
        
        Returns:
            Unmodified response object.
        """
        log_data = {
            "request_id": g.get('request_id', 'unknown'),
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "response_data": response.get_data(as_text=True)
        }
        
        logs_config.logger.info(f"Response: {json.dumps(log_data)}")
        
        return response
    
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
