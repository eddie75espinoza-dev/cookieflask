import jwt
from flask import request, jsonify
from functools import wraps

from config import Config
from logs import logs_config


def require_bearer_token(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'msg': 'Authorization header is missing!'}), 401

        if not auth_header.startswith("Bearer "):
            return jsonify({'msg': 'Invalid Authorization header format!'}), 401
        
        token = auth_header.split(" ")[1]

        try:
            decoded_token = jwt.decode(token, Config.TOKEN_SECRET_KEY, algorithms=["HS256"])
            
            if decoded_token.get("sub") != Config.SUB:
                logs_config.logger.info(f"Invalid token data: {decoded_token.get("sub")} | token {token}")
                return jsonify({'msg': 'Invalid token data'}), 403

        except jwt.ExpiredSignatureError as jwt_exc_exp:
            logs_config.logger.error(f"Token has expired - {str(jwt_exc_exp)}")
            return jsonify({'msg': 'Token has expired'}), 401
        
        except jwt.InvalidTokenError as jwt_exc_invalid:
            logs_config.logger.error(f"Invalid token - {str(jwt_exc_invalid)}")
            return jsonify({'msg': 'Invalid token'}), 403
        
        except Exception as exc:
            logs_config.logger.error(f"Unexpected error: {str(exc)}")
            return jsonify({'msg': f'An error occurred: {str(exc)}'}), 500

        return func(*args, **kwargs)
    return decorated
