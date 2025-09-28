from flask import Blueprint, jsonify

from core.middleware import token_required


bp = Blueprint('/', __name__, url_prefix='/')


@bp.route('/', methods=['GET'])
@token_required
def read_root():
    return jsonify({
        'msg': '{{ cookiecutter.project_name }} protected'
    }), 200

