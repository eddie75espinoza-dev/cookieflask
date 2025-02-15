import jwt
from flask import request, jsonify
from functools import wraps

from core.config import APP_CONFIG
from logs import logs_config


def extract_token():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header:
        return None, jsonify({'msg': 'Authorization header is missing!'}), 401

    parts = auth_header.split(maxsplit=1)
    if len(parts) != 2 or parts[0] != 'Bearer':
        return None, jsonify({'msg': 'Invalid Authorization header format!'}), 401

    return parts[1], None, None

def require_bearer_token(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token, error_response, error_code = extract_token()
        if error_response:
            return error_response, error_code

        try:
            decoded_token = jwt.decode(
                token,
                APP_CONFIG.TOKEN_SECRET_KEY,
                algorithms=["HS256"]
            )
            if decoded_token.get("sub") != APP_CONFIG.SUB:
                return jsonify({'msg': 'Invalid token data'}), 403

        except jwt.ExpiredSignatureError:
            return jsonify({'msg': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'msg': 'Invalid token'}), 403
        except Exception as exc:
            logs_config.logger.error(f"Error token {str(exc)}")
            return jsonify({'msg': 'An internal error occurred.'}), 500

        return func(*args, **kwargs)
    return decorated
