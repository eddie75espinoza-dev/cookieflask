import jwt
from flask import request, jsonify
from functools import wraps
from typing import Optional, Tuple, Any, Callable

from core.config import APP_CONFIG
from logs import log_config


BEARER_PREFIX = "Bearer "
EXPECTED_ALGORITHM = "HS256"

# Standardized error messages (no internal details exposed)
ERROR_MESSAGES = {
    'missing_header': 'Authorization required',
    'invalid_format': 'Invalid authorization format',
    'invalid_token': 'Invalid token',
    'access_denied': 'Access denied',
    'server_error': 'Authentication error'
}


def _extract_token(auth_header: str) -> Optional[str]:
    """
    Safely extracts token from Authorization header.
    
    Args:
        auth_header: Authorization header value
        
    Returns:
        Extracted token or None if invalid format
    """
    if not auth_header.startswith(BEARER_PREFIX):
        return None
    
    # Extract token and validate it's not empty
    token = auth_header[len(BEARER_PREFIX):].strip()
    return token if token else None


def _validate_token_as_api_key(token: str) -> bool:
    """
    Validates token against configured API key (TOKEN_API_KEY).
    
    This implements the API key validation where the bearer token
    must match the shared TOKEN_API_KEY configuration.
    
    Args:
        token: Token to validate as API key
        
    Returns:
        True if token matches the configured API key
    """
    if not APP_CONFIG.TOKEN_API_KEY:
        return False
    return token == APP_CONFIG.TOKEN_API_KEY


def _log_auth_failure(reason: str, details: str = "") -> None:
    """
    Securely logs authentication failures without exposing sensitive data.
    
    Filters out sensitive information like tokens, keys, or secrets
    from the log details to prevent security leaks.
    
    Args:
        reason: Primary reason for authentication failure
        details: Additional details (filtered for sensitive data)
    """
    log_message = f"Authentication failed: {reason}"
    
    # Only add details if they don't contain sensitive information
    if details and not any(sensitive in details.lower() for sensitive in ['token', 'key', 'secret']):
        log_message += f" - {details}"
    
    log_config.logger.warning(log_message)


def token_required(func: Callable) -> Callable:
    """
    Decorator that enforces JWT + API Key authentication.
    
    This implements a hybrid authentication system:
    1. Bearer token must match the configured API key (TOKEN_API_KEY)
    2. Same token must be a valid JWT signed with JWT_SECRET_KEY
    3. JWT payload is validated for 'sub' and 'iss' if configured
    
    Authentication flow:
    - Extract Bearer token from Authorization header
    - Validate token as API key against TOKEN_API_KEY
    - Decode token as JWT using JWT_SECRET_KEY for signature verification
    - Validate JWT payload fields (sub, iss) if configured
    
    Security features:
    - Secure logging (no token exposure)
    - Standardized error messages
    - Comprehensive JWT validation options
    - Separation of API key and JWT validation logic
    
    Args:
        func: Function to protect with authentication
        
    Returns:
        Decorated function with JWT + API Key validation
    """
    @wraps(func)
    def decorated(*args, **kwargs) -> Tuple[Any, int]:
        try:
            # Step 1: Validate Authorization header presence
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                _log_auth_failure("Missing Authorization header")
                return jsonify({'msg': ERROR_MESSAGES['missing_header']}), 401

            # Step 2: Extract token safely from header
            token = _extract_token(auth_header)
            if not token:
                _log_auth_failure("Invalid Authorization header format")
                return jsonify({'msg': ERROR_MESSAGES['invalid_format']}), 401

            # Step 3: Validate token as API key
            # This ensures the bearer token matches the shared API key
            if not _validate_token_as_api_key(token):
                _log_auth_failure("Invalid API key")
                return jsonify({'msg': ERROR_MESSAGES['access_denied']}), 403

            # Step 4: Decode and validate JWT structure and signature
            # The same token that serves as API key must also be a valid JWT
            decoded_token = jwt.decode(
                token, 
                APP_CONFIG.JWT_SECRET_KEY, 
                algorithms=[EXPECTED_ALGORITHM],
                options={
                    "verify_signature": True,    # Verify JWT signature
                    "verify_exp": False,         # API keys don't expire
                    "verify_iat": True,          # Verify issued at time
                    "require": ["sub", "iss", "iat", "type"]  # Required JWT fields
                }
            )
            
            # Step 5: Authentication successful - proceed with original function
            return func(*args, **kwargs)

        except jwt.InvalidSignatureError:
            # JWT signature verification failed
            _log_auth_failure("Invalid JWT signature")
            return jsonify({'msg': ERROR_MESSAGES['invalid_token']}), 403
            
        except jwt.DecodeError:
            # JWT structure is malformed
            _log_auth_failure("JWT decode error")
            return jsonify({'msg': ERROR_MESSAGES['invalid_token']}), 403
            
        except jwt.InvalidTokenError as e:
            # Other JWT validation errors
            _log_auth_failure("Invalid JWT token", str(e))
            return jsonify({'msg': ERROR_MESSAGES['invalid_token']}), 403
            
        except Exception as error:
            # Unexpected errors - log for debugging but don't expose details
            log_config.logger.error(
                f"Unexpected authentication error: {type(error).__name__}: {str(error)}"
            )
            return jsonify({'msg': ERROR_MESSAGES['server_error']}), 500

    return decorated
