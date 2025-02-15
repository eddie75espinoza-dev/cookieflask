from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from core.config import APP_CONFIG
from routers import routes
{%- if cookiecutter.use_db == "yes" %}
from db.database import db
{%- endif %}


ma = Marshmallow()


def create_app():
    app = Flask(__name__)
    app.config.from_object(APP_CONFIG)
    app.json.sort_keys = False
    
    {%- if cookiecutter.use_db == "yes" %}

    db.init_app(app)
    {%- endif %}

    ma.init_app(app)
    JWTManager(app)

    app.register_blueprint(routes.bp)
    
    script_name = APP_CONFIG.BASE_URL
    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
        script_name: app
    })
    
    @app.route("/api")
    def app_info():
        info_data = {
            "name": f"{{ cookiecutter.project_name }}"
        }
        return jsonify(info_data), 200

    return app

    
app = create_app()
