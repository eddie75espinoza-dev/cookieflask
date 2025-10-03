import re
from typing import Any, Dict, List, Union


# Sensitive header patterns to filter
SENSITIVE_HEADERS = [
    'Authorization',
    'X-Api-Key',
    'X-API-Key',
    'Cookie',
    'Set-Cookie',
    'X-Auth-Token',
    'X-CSRF-Token',
    'Proxy-Authorization'
]

# Sensitive field patterns in JSON data
SENSITIVE_FIELDS = [
    'password',
    'passwd',
    'pwd',
    'secret',
    'token',
    'api_key',
    'apikey',
    'access_token',
    'refresh_token',
    'private_key',
    'client_secret',
    'auth',
    'authorization'
]

# Regex patterns for sensitive data
JWT_PATTERN = re.compile(r'eyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+')
API_KEY_PATTERN = re.compile(r'\b[A-Za-z0-9]{32,}\b')
BEARER_PATTERN = re.compile(r'Bearer\s+[\S]+', re.IGNORECASE)


def sanitize_headers(headers: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize sensitive headers by replacing their values.
    
    Args:
        headers: Dictionary of HTTP headers.
    
    Returns:
        Dictionary with sensitive headers masked.
    """
    sanitized = headers.copy()
    
    for header_name in SENSITIVE_HEADERS:
        # Case-insensitive header matching
        for key in list(sanitized.keys()):
            if key.lower() == header_name.lower():
                sanitized[key] = '[FILTERED]'
    
    return sanitized


def sanitize_json_data(data: Union[Dict, List, Any]) -> Union[Dict, List, Any]:
    """
    Recursively sanitize sensitive fields in JSON data.
    
    Args:
        data: JSON data structure (dict, list, or primitive).
    
    Returns:
        Sanitized copy of the data structure.
    """
    if data is None:
        return None
    
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            # Check if key matches sensitive field patterns
            if any(sensitive.lower() in key.lower() for sensitive in SENSITIVE_FIELDS):
                sanitized[key] = '[FILTERED]'
            else:
                # Recursively sanitize nested structures
                sanitized[key] = sanitize_json_data(value)
        return sanitized
    
    elif isinstance(data, list):
        return [sanitize_json_data(item) for item in data]
    
    elif isinstance(data, str):
        # Sanitize JWT tokens in string values
        if JWT_PATTERN.search(data):
            data = JWT_PATTERN.sub('[JWT_TOKEN]', data)
        # Sanitize Bearer tokens
        if BEARER_PATTERN.search(data):
            data = BEARER_PATTERN.sub('Bearer [FILTERED]', data)
        return data
    
    else:
        return data


def sanitize_url(url: str) -> str:
    """
    Sanitize sensitive information from URLs (query parameters, tokens).
    
    Args:
        url: URL string to sanitize.
    
    Returns:
        Sanitized URL string.
    """
    # Remove common sensitive query parameters
    sensitive_params = ['token', 'api_key', 'apikey', 'access_token', 'key', 'secret']
    
    for param in sensitive_params:
        # Match parameter in query string (case-insensitive)
        # Use a callback to preserve the original case of the parameter name
        def replace_param(match):
            prefix = match.group(1)
            param_name = match.group(2)
            return f'{prefix}{param_name}=[FILTERED]'
        
        pattern = re.compile(rf'([?&])({param})=[^&]*', re.IGNORECASE)
        url = pattern.sub(replace_param, url)
    
    return url


def sanitize_log_data(log_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize complete log data structure.
    
    This function handles the entire log data structure typically used
    in Flask request/response logging, including headers, JSON data,
    URLs, and query parameters.
    
    Args:
        log_data: Complete log data dictionary.
    
    Returns:
        Fully sanitized log data dictionary.
    """
    sanitized = log_data.copy()
    
    # Sanitize headers if present
    if 'headers' in sanitized and isinstance(sanitized['headers'], dict):
        sanitized['headers'] = sanitize_headers(sanitized['headers'])
    
    # Sanitize JSON data if present
    if 'json_data' in sanitized and sanitized['json_data'] is not None:
        sanitized['json_data'] = sanitize_json_data(sanitized['json_data'])
    
    # Sanitize URL if present
    if 'url' in sanitized and isinstance(sanitized['url'], str):
        sanitized['url'] = sanitize_url(sanitized['url'])
    
    # Sanitize query parameters if present
    if 'args' in sanitized and isinstance(sanitized['args'], dict):
        sanitized['args'] = sanitize_json_data(sanitized['args'])
    
    # Sanitize response data if present (could contain sensitive info)
    if 'response_data' in sanitized and isinstance(sanitized['response_data'], str):
        try:
            # Try to parse as JSON and sanitize
            import json
            response_json = json.loads(sanitized['response_data'])
            sanitized_response = sanitize_json_data(response_json)
            sanitized['response_data'] = json.dumps(sanitized_response)
        except (json.JSONDecodeError, TypeError):
            # If not JSON, sanitize as string
            sanitized['response_data'] = sanitize_json_data(sanitized['response_data'])
    
    return sanitized