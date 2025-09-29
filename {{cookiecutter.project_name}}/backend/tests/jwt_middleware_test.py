import pytest
from unittest.mock import patch, Mock
import jwt
import datetime
from flask import Flask


from core.middleware import (
    _extract_token,
    _validate_token_as_api_key,
    _log_auth_failure,
    token_required,
    ERROR_MESSAGES
)

# Test constants
TEST_JWT_SECRET_KEY = "test_secret_key_for_jwt_signing_12345"
TEST_SUB = "test-service-api"
TEST_ISS = "test-service-issuer"

# Fixtures
@pytest.fixture
def flask_app():
    """Create Flask test application."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def request_context(flask_app):
    """Create Flask request context."""
    with flask_app.test_request_context():
        yield flask_app

@pytest.fixture
def valid_jwt_token():
    """Generate a valid JWT token for testing."""
    payload = {
        "sub": TEST_SUB,
        "iss": TEST_ISS,
        "iat": datetime.datetime.now(),
        "type": "access",
        "jti": "test-jti-12345"
    }
    return jwt.encode(payload, TEST_JWT_SECRET_KEY, algorithm="HS256")

@pytest.fixture
def invalid_signature_token():
    """Generate a JWT token with invalid signature."""
    payload = {
        "sub": TEST_SUB,
        "iss": TEST_ISS,
        "iat": datetime.datetime.now(),
        "type": "access",
        "jti": "invalid-sig"
    }
    return jwt.encode(payload, "wrong_secret_key", algorithm="HS256")

@pytest.fixture
def malformed_jwt_token():
    """Generate a malformed JWT token."""
    return "invalid.jwt.token"

@pytest.fixture
def test_function():
    """Simple test function to be decorated."""
    def protected_endpoint():
        return {"message": "success"}, 200
    return protected_endpoint


class TestExtractToken:
    """Test _extract_token function."""

    def test_extract_valid_token(self):
        """Test extracting valid token from Authorization header."""
        auth_header = "Bearer valid_token_123"
        result = _extract_token(auth_header)
        assert result == "valid_token_123"

    def test_extract_token_with_spaces(self):
        """Test extracting token with extra spaces."""
        auth_header = "Bearer   token_with_spaces   "
        result = _extract_token(auth_header)
        assert result == "token_with_spaces"

    def test_extract_token_invalid_prefix(self):
        """Test extraction with invalid Bearer prefix."""
        auth_header = "Basic invalid_format"
        result = _extract_token(auth_header)
        assert result is None

    def test_extract_token_empty_after_bearer(self):
        """Test extraction when token is empty after Bearer."""
        auth_header = "Bearer "
        result = _extract_token(auth_header)
        assert result is None

    def test_extract_token_only_spaces_after_bearer(self):
        """Test extraction when only spaces after Bearer."""
        auth_header = "Bearer     "
        result = _extract_token(auth_header)
        assert result is None


class TestValidateTokenAsApiKey:
    """Test _validate_token_as_api_key function."""

    @patch('core.middleware.APP_CONFIG')
    def test_validate_correct_api_key(self, mock_config):
        """Test validation with correct API key."""
        mock_config.TOKEN_API_KEY = "test_api_key"
        result = _validate_token_as_api_key("test_api_key")
        assert result is True

    @patch('core.middleware.APP_CONFIG')
    def test_validate_incorrect_api_key(self, mock_config):
        """Test validation with incorrect API key."""
        mock_config.TOKEN_API_KEY = "test_api_key"
        result = _validate_token_as_api_key("wrong_api_key")
        assert result is False

    @patch('core.middleware.APP_CONFIG')
    def test_validate_empty_config_key(self, mock_config):
        """Test validation when config key is empty."""
        mock_config.TOKEN_API_KEY = ""
        result = _validate_token_as_api_key("some_token")
        assert result is False

    @patch('core.middleware.APP_CONFIG')
    def test_validate_none_config_key(self, mock_config):
        """Test validation when config key is None."""
        mock_config.TOKEN_API_KEY = None
        result = _validate_token_as_api_key("some_token")
        assert result is False


class TestLogAuthFailure:
    """Test _log_auth_failure function."""

    @patch('core.middleware.logs_config')
    def test_log_simple_failure(self, mock_logs_config):
        """Test logging simple authentication failure."""
        _log_auth_failure("Invalid token")
        
        mock_logs_config.logger.warning.assert_called_once_with(
            "Authentication failed: Invalid token"
        )

    @patch('core.middleware.logs_config')
    def test_log_failure_with_safe_details(self, mock_logs_config):
        """Test logging failure with safe details."""
        _log_auth_failure("Invalid format", "header malformed")
        
        mock_logs_config.logger.warning.assert_called_once_with(
            "Authentication failed: Invalid format - header malformed"
        )

    @patch('core.middleware.logs_config')
    def test_log_failure_filters_sensitive_token(self, mock_logs_config):
        """Test that token details are filtered out."""
        _log_auth_failure("Invalid JWT", "token validation failed")
        
        mock_logs_config.logger.warning.assert_called_once_with(
            "Authentication failed: Invalid JWT"
        )


class TestTokenRequiredDecorator:
    """Test token_required decorator."""

    @patch('core.middleware.APP_CONFIG')
    def test_successful_authentication(self, mock_config, request_context, 
                                     valid_jwt_token, test_function):
        """Test successful authentication flow."""
        mock_config.JWT_SECRET_KEY = TEST_JWT_SECRET_KEY
        mock_config.TOKEN_API_KEY = valid_jwt_token
        mock_config.SUB = TEST_SUB
        mock_config.ISS = TEST_ISS
        
        # Create a proper mock request object
        mock_request = Mock()
        mock_request.headers = Mock()
        mock_request.headers.get = Mock(return_value=f"Bearer {valid_jwt_token}")
        
        with patch('core.middleware.request', mock_request):
            decorated_func = token_required(test_function)
            result = decorated_func()
            
            assert result == ({"message": "success"}, 200)

    @patch('core.middleware.APP_CONFIG')
    def test_missing_authorization_header(self, mock_config, request_context, test_function):
        """Test missing Authorization header."""
        # Create proper mock objects
        mock_request = Mock()
        mock_request.headers = Mock()
        mock_request.headers.get = Mock(return_value=None)
        
        mock_response = Mock()
        
        with patch('core.middleware.request', mock_request), \
             patch('core.middleware.jsonify', return_value=mock_response):
            
            decorated_func = token_required(test_function)
            result, status_code = decorated_func()
            
            assert status_code == 401

    @patch('core.middleware.APP_CONFIG')
    def test_invalid_header_format(self, mock_config, request_context, test_function):
        """Test invalid Authorization header format."""
        # Create proper mock objects
        mock_request = Mock()
        mock_request.headers = Mock()
        mock_request.headers.get = Mock(return_value=None)
        
        mock_response = Mock()

        with patch('core.middleware.request', mock_request), \
             patch('core.middleware.jsonify', return_value=mock_response):
            
            mock_request.headers.get.return_value = "Basic invalid_format"
            mock_response.return_value = Mock()
            
            decorated_func = token_required(test_function)
            result, status_code = decorated_func()
            
            assert status_code == 401

    @patch('core.middleware.APP_CONFIG')
    def test_bearer_without_token(self, mock_config, request_context, test_function):
        """Test Bearer without token."""
        # Create proper mock objects
        mock_request = Mock()
        mock_request.headers = Mock()
        mock_request.headers.get = Mock(return_value=None)
        
        mock_response = Mock()

        with patch('core.middleware.request', mock_request), \
             patch('core.middleware.jsonify', return_value=mock_response):
            
            mock_request.headers.get.return_value = "Bearer"
            mock_response.return_value = Mock()
            
            decorated_func = token_required(test_function)
            result, status_code = decorated_func()
            
            assert status_code == 401

    @patch('core.middleware.APP_CONFIG')
    def test_invalid_api_key(self, mock_config, request_context, test_function):
        """Test invalid API key."""
        mock_config.TOKEN_API_KEY = "expected_key"
        
        # Create proper mock objects
        mock_request = Mock()
        mock_request.headers = Mock()
        mock_request.headers.get = Mock(return_value="Bearer wrong_api_key")
        
        mock_response = Mock()
        
        with patch('core.middleware.request', mock_request), \
             patch('core.middleware.jsonify', return_value=mock_response):
            
            decorated_func = token_required(test_function)
            result, status_code = decorated_func()
            
            assert status_code == 403

    @patch('core.middleware.APP_CONFIG')
    def test_invalid_jwt_signature(self, mock_config, request_context, 
                                 invalid_signature_token, test_function):
        """Test invalid JWT signature."""
        mock_config.JWT_SECRET_KEY = TEST_JWT_SECRET_KEY
        mock_config.TOKEN_API_KEY = invalid_signature_token
        
        # Create proper mock objects
        mock_request = Mock()
        mock_request.headers = Mock()
        mock_request.headers.get = Mock(return_value=f"Bearer {invalid_signature_token}")
        
        mock_response = Mock()
        
        with patch('core.middleware.request', mock_request), \
             patch('core.middleware.jsonify', return_value=mock_response):
            
            decorated_func = token_required(test_function)
            result, status_code = decorated_func()
            
            assert status_code == 403

    @patch('core.middleware.APP_CONFIG')
    def test_malformed_jwt_token(self, mock_config, request_context, 
                                malformed_jwt_token, test_function):
        """Test malformed JWT token."""
        mock_config.JWT_SECRET_KEY = TEST_JWT_SECRET_KEY
        mock_config.TOKEN_API_KEY = malformed_jwt_token
        
        # Create proper mock objects
        mock_request = Mock()
        mock_request.headers = Mock()
        mock_request.headers.get = Mock(return_value=f"Bearer {malformed_jwt_token}")
        
        mock_response = Mock()
        
        with patch('core.middleware.request', mock_request), \
             patch('core.middleware.jsonify', return_value=mock_response):
            
            decorated_func = token_required(test_function)
            result, status_code = decorated_func()
            
            assert status_code == 403

    @patch('core.middleware.APP_CONFIG')
    def test_jwt_decode_error(self, mock_config, request_context, test_function):
        """Test JWT DecodeError exception."""
        # Create a token that will cause DecodeError specifically
        malformed_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.invalid_base64_payload.signature"
        
        mock_config.JWT_SECRET_KEY = TEST_JWT_SECRET_KEY
        mock_config.TOKEN_API_KEY = malformed_token
        
        # Create proper mock objects
        mock_request = Mock()
        mock_request.headers = Mock()
        mock_request.headers.get = Mock(return_value=f"Bearer {malformed_token}")
        
        mock_response = Mock()
        
        with patch('core.middleware.request', mock_request), \
             patch('core.middleware.jsonify', return_value=mock_response):
            
            decorated_func = token_required(test_function)
            result, status_code = decorated_func()
            
            assert status_code == 403

    @patch('core.middleware.APP_CONFIG')
    def test_jwt_invalid_token_error(self, mock_config, request_context, test_function):
        """Test JWT InvalidTokenError exception."""
        # Create a token that will cause InvalidTokenError (missing required claim)
        payload = {
            "iat": datetime.datetime.now(),
            "type": "access"
            # Missing required 'sub' and 'iss' fields that JWT decoder requires
        }
        invalid_token = jwt.encode(payload, TEST_JWT_SECRET_KEY, algorithm="HS256")
        
        mock_config.JWT_SECRET_KEY = TEST_JWT_SECRET_KEY
        mock_config.TOKEN_API_KEY = invalid_token
        
        # Create proper mock objects
        mock_request = Mock()
        mock_request.headers = Mock()
        mock_request.headers.get = Mock(return_value=f"Bearer {invalid_token}")
        
        mock_response = Mock()
        
        with patch('core.middleware.request', mock_request), \
             patch('core.middleware.jsonify', return_value=mock_response):
            
            decorated_func = token_required(test_function)
            result, status_code = decorated_func()
            
            assert status_code == 403

    @patch('core.middleware.APP_CONFIG')
    def test_jwt_decode_error_direct(self, mock_config, request_context, test_function):
        """Test JWT DecodeError by mocking jwt.decode directly."""
        valid_token = "some_token_that_passes_api_key_validation"
        
        mock_config.JWT_SECRET_KEY = TEST_JWT_SECRET_KEY
        mock_config.TOKEN_API_KEY = valid_token  # This will pass API key validation
        
        mock_request = Mock()
        mock_request.headers = Mock()
        mock_request.headers.get = Mock(return_value=f"Bearer {valid_token}")
        
        mock_response = Mock()
        
        # Mock jwt.decode to specifically raise DecodeError
        with patch('core.middleware.request', mock_request), \
            patch('core.middleware.jsonify', return_value=mock_response), \
            patch('jwt.decode', side_effect=jwt.DecodeError("Forced decode error")):
            
            decorated_func = token_required(test_function)
            result, status_code = decorated_func()
            
            assert status_code == 403

    @patch('core.middleware.APP_CONFIG')
    @patch('core.middleware.logs_config')
    def test_unexpected_exception(self, mock_logs_config, mock_config, 
                                request_context, test_function):
        """Test handling of unexpected exceptions."""
        # Create proper mock objects
        mock_request = Mock()
        mock_request.headers = Mock()
        mock_request.headers.get = Mock(side_effect=Exception("Unexpected error"))
        
        mock_response = Mock()
        
        with patch('core.middleware.request', mock_request), \
             patch('core.middleware.jsonify', return_value=mock_response):
            
            decorated_func = token_required(test_function)
            result, status_code = decorated_func()
            
            assert status_code == 500
            mock_logs_config.logger.error.assert_called_once()

    def test_preserves_function_metadata(self):
        """Test that decorator preserves original function metadata."""
        def original_function():
            """Original docstring."""
            pass
        
        original_function.__name__ = "test_name"
        
        decorated_func = token_required(original_function)
        
        assert decorated_func.__name__ == "test_name"
        assert decorated_func.__doc__ == "Original docstring."