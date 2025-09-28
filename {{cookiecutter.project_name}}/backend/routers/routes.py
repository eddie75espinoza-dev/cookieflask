from flask import Blueprint, jsonify
{%- if cookiecutter.use_db == "yes" %}
from sqlalchemy import text

from core.config import ENVIRONMENT
from db.database import db
{%- endif %}

from core.middleware import token_required


bp = Blueprint('/', __name__, url_prefix='/')


@bp.route('/', methods=['GET'])
@token_required
def read_root():
    return jsonify({
        'msg': '{{ cookiecutter.project_name }} protected'
    }), 200

{%- if cookiecutter.use_db == "yes" %}

