import pytest
from logs.logs_sanitizer import (
    sanitize_headers,
    sanitize_json_data,
    sanitize_url,
    sanitize_log_data
)


class TestSanitizeHeaders:
    """Test cases for header sanitization."""
    
    def test_sanitize_authorization_header(self):
        """Test that Authorization header is filtered."""
        headers = {
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
            'Content-Type': 'application/json',
            'User-Agent': 'TestClient/1.0'
        }
        
        result = sanitize_headers(headers)
        
        assert result['Authorization'] == '[FILTERED]'
        assert result['Content-Type'] == 'application/json'
        assert result['User-Agent'] == 'TestClient/1.0'
    
    def test_sanitize_headers_case_insensitive(self):
        """Test that header filtering is case-insensitive."""
        headers = {
            'authorization': 'Bearer token123',
            'x-api-key': 'secret-key',
            'COOKIE': 'session=abc123'
        }
        
        result = sanitize_headers(headers)
        
        assert result['authorization'] == '[FILTERED]'
        assert result['x-api-key'] == '[FILTERED]'
        assert result['COOKIE'] == '[FILTERED]'
    
    def test_sanitize_multiple_sensitive_headers(self):
        """Test filtering of multiple sensitive headers."""
        headers = {
            'Authorization': 'Bearer token',
            'X-Auth-Token': 'auth_token',
            'Cookie': 'session=123',
            'Content-Type': 'application/json'
        }
        
        result = sanitize_headers(headers)
        
        assert result['Authorization'] == '[FILTERED]'
        assert result['X-Auth-Token'] == '[FILTERED]'
        assert result['Cookie'] == '[FILTERED]'
        assert result['Content-Type'] == 'application/json'
    
    def test_sanitize_empty_headers(self):
        """Test that empty headers dict is handled correctly."""
        headers = {}
        result = sanitize_headers(headers)
        assert result == {}


class TestSanitizeJsonData:
    """Test cases for JSON data sanitization."""
    
    def test_sanitize_password_field(self):
        """Test that password fields are filtered in JSON."""
        data = {
            'username': 'john_doe',
            'password': 'super_secret_123',
            'email': 'john@example.com'
        }
        
        result = sanitize_json_data(data)
        
        assert result['username'] == 'john_doe'
        assert result['password'] == '[FILTERED]'
        assert result['email'] == 'john@example.com'
    
    def test_sanitize_nested_sensitive_fields(self):
        """Test that nested sensitive fields are filtered."""
        data = {
            'user': {
                'name': 'John',
                'credentials': {
                    'api_key': 'secret123',
                    'password': 'pass123'
                }
            },
            'public_data': 'visible'
        }
        
        result = sanitize_json_data(data)
        
        assert result['user']['name'] == 'John'
        assert result['user']['credentials']['api_key'] == '[FILTERED]'
        assert result['user']['credentials']['password'] == '[FILTERED]'
        assert result['public_data'] == 'visible'
    
    def test_sanitize_jwt_token_in_string(self):
        """Test that JWT tokens in strings are filtered."""
        data = {
            'message': 'Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abc'
        }
        
        result = sanitize_json_data(data)
        
        assert '[JWT_TOKEN]' in result['message']
        assert 'eyJhbGci' not in result['message']
    
    def test_sanitize_bearer_token_in_string(self):
        """Test that Bearer tokens in strings are filtered."""
        data = {
            'auth_header': 'Bearer abc123def456ghi789'
        }
        
        result = sanitize_json_data(data)
        
        assert result['auth_header'] == '[FILTERED]'
        assert 'abc123def456ghi789' not in result['auth_header']
    
    def test_sanitize_list_of_dicts(self):
        """Test sanitization of list containing dictionaries."""
        data = [
            {'username': 'user1', 'password': 'pass1'},
            {'username': 'user2', 'api_key': 'key123'}
        ]
        
        result = sanitize_json_data(data)
        
        assert result[0]['username'] == 'user1'
        assert result[0]['password'] == '[FILTERED]'
        assert result[1]['username'] == 'user2'
        assert result[1]['api_key'] == '[FILTERED]'
    
    def test_sanitize_none_value(self):
        """Test that None values are handled correctly."""
        result = sanitize_json_data(None)
        assert result is None
    
    def test_sanitize_primitive_types(self):
        """Test that primitive types are handled correctly."""
        assert sanitize_json_data(42) == 42
        assert sanitize_json_data(3.14) == 3.14
        assert sanitize_json_data(True) is True
        assert sanitize_json_data("hello") == "hello"
    
    @pytest.mark.parametrize("sensitive_field", [
        'password', 'passwd', 'pwd', 'secret', 'token',
        'api_key', 'apikey', 'access_token', 'refresh_token',
        'private_key', 'client_secret'
    ])
    def test_sanitize_various_sensitive_fields(self, sensitive_field):
        """Test that various sensitive field names are filtered."""
        data = {sensitive_field: 'sensitive_value', 'public': 'public_value'}
        result = sanitize_json_data(data)
        
        assert result[sensitive_field] == '[FILTERED]'
        assert result['public'] == 'public_value'
    
    def test_sanitize_real_world_response_with_access_token(self):
        """Test sanitization of actual response log with access_token."""
        import json
        
        log_data = {
            'request_id': '4b100695-d88c-45cc-84d9-a12647e1a458',
            'status_code': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Content-Length': '320'
            },
            'response_data': json.dumps({
                'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1OTM1MTc2MSwianRpIjoiZjk5YzQ1N2EtMzIxMS00ODgxLThlMjYtZTMyODAzMjNjMDdhIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MywibmJmIjoxNzU5MzUxNzYxLCJjc3JmIjoiZTQwOWQ3N2UtZmU4OS00NWY1LTk2NzktOThmNmFkNDgzMjMxIn0.VAzT8-bck0WCwQVq7_6tipngIurdRUxGdlgs4atUNDg'
            })
        }
        
        result = sanitize_log_data(log_data)
        response = json.loads(result['response_data'])
        
        # access_token should be filtered
        assert response['access_token'] == '[FILTERED]'
        assert 'eyJhbGci' not in result['response_data']

    def test_sanitize_real_world_request_with_long_password(self):
        """Test sanitization of actual request log with long password."""
        log_data = {
            'request_id': '2036f1ee-5862-42de-82c0-21237ed5a970',
            'method': 'POST',
            'url': 'https://api.example.com/auth/login',
            'headers': {
                'X-Real-Ip': '100.00.00.00',
                'Host': '100.00.00.00',
                'Content-Type': 'application/json'
            },
            'args': {},
            'json_data': {
                'username': 'user',
                'password': 'vqO_oeK_EQV-0Ecye3f0QSL50CO4E8zJdpJJhGJD5q0'
            }
        }
        
        result = sanitize_log_data(log_data)
        
        # Password should be filtered
        assert result['json_data']['password'] == '[FILTERED]'
        assert result['json_data']['username'] == 'user'
        assert 'A4tBj8kD9m' not in str(result)


class TestSanitizeUrl:
    """Test cases for URL sanitization."""
    
    def test_sanitize_token_param(self):
        """Test that token parameter is filtered."""
        url = 'https://api.example.com/users?id=123&token=secret123'
        result = sanitize_url(url)
        
        assert 'token=[FILTERED]' in result
        assert 'id=123' in result
        assert 'secret123' not in result
    
    def test_sanitize_multiple_sensitive_params(self):
        """Test that multiple sensitive parameters are filtered."""
        url = 'https://api.example.com/data?id=1&api_key=key456&token=tok789&page=2'
        result = sanitize_url(url)
        
        assert 'api_key=[FILTERED]' in result
        assert 'token=[FILTERED]' in result
        assert 'id=1' in result
        assert 'page=2' in result
        assert 'key456' not in result
        assert 'tok789' not in result
    
    def test_sanitize_url_case_insensitive_params(self):
        """Test that parameter filtering is case-insensitive."""
        url = 'https://api.example.com/data?TOKEN=secret&API_KEY=key'
        result = sanitize_url(url)
        
        assert 'TOKEN=[FILTERED]' in result
        assert 'API_KEY=[FILTERED]' in result
    
    def test_sanitize_url_without_sensitive_params(self):
        """Test URL without sensitive parameters remains unchanged."""
        url = 'https://api.example.com/users?id=123&page=1'
        result = sanitize_url(url)
        
        assert result == url
    
    def test_sanitize_url_without_query_string(self):
        """Test URL without query string remains unchanged."""
        url = 'https://api.example.com/users'
        result = sanitize_url(url)
        
        assert result == url


class TestSanitizeLogData:
    """Test cases for complete log data sanitization."""
    
    def test_sanitize_complete_log_data(self):
        """Test complete log data sanitization."""
        log_data = {
            'request_id': 'abc-123',
            'method': 'POST',
            'url': 'http://localhost:5000/api/users?token=secret',
            'headers': {
                'Authorization': 'Bearer eyJhbGci...',
                'Content-Type': 'application/json'
            },
            'args': {
                'id': '123',
                'api_key': 'secret_key'
            },
            'json_data': {
                'username': 'john',
                'password': 'secret_pass'
            }
        }
        
        result = sanitize_log_data(log_data)
        
        # Check request_id and method are unchanged
        assert result['request_id'] == 'abc-123'
        assert result['method'] == 'POST'
        
        # Check URL is sanitized
        assert 'token=[FILTERED]' in result['url']
        
        # Check headers are sanitized
        assert result['headers']['Authorization'] == '[FILTERED]'
        assert result['headers']['Content-Type'] == 'application/json'
        
        # Check query args are sanitized
        assert result['args']['id'] == '123'
        assert result['args']['api_key'] == '[FILTERED]'
        
        # Check JSON data is sanitized
        assert result['json_data']['username'] == 'john'
        assert result['json_data']['password'] == '[FILTERED]'
    
    def test_sanitize_log_data_with_none_values(self):
        """Test that None values are handled correctly."""
        log_data = {
            'request_id': 'abc-123',
            'json_data': None,
            'headers': None
        }
        
        result = sanitize_log_data(log_data)
        
        assert result['request_id'] == 'abc-123'
        assert result['json_data'] is None
    
    def test_sanitize_response_data_json(self):
        """Test sanitization of JSON response data."""
        import json
        
        log_data = {
            'request_id': 'xyz-456',
            'response_data': json.dumps({
                'user': 'john',
                'token': 'secret_token_123'
            })
        }
        
        result = sanitize_log_data(log_data)
        response = json.loads(result['response_data'])
        
        assert response['user'] == 'john'
        assert response['token'] == '[FILTERED]'
    
    def test_sanitize_response_data_non_json(self):
        """Test sanitization of non-JSON response data."""
        log_data = {
            'request_id': 'xyz-789',
            'response_data': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test'
        }
        
        result = sanitize_log_data(log_data)
        
        assert 'Bearer [FILTERED]' in result['response_data']
        assert 'eyJhbGci' not in result['response_data']
    
    def test_sanitize_log_data_preserves_non_sensitive_data(self):
        """Test that non-sensitive data is preserved."""
        log_data = {
            'request_id': 'test-123',
            'method': 'GET',
            'url': 'http://api.example.com/data?page=1&limit=10',
            'headers': {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            'json_data': {
                'name': 'Test User',
                'email': 'test@example.com'
            }
        }
        
        result = sanitize_log_data(log_data)
        
        assert result['request_id'] == 'test-123'
        assert result['method'] == 'GET'
        assert result['url'] == log_data['url']
        assert result['headers'] == log_data['headers']
        assert result['json_data'] == log_data['json_data']


class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_empty_log_data(self):
        """Test that empty log data is handled correctly."""
        log_data = {}
        result = sanitize_log_data(log_data)
        assert result == {}
    
    def test_deeply_nested_structure(self):
        """Test sanitization of deeply nested structures."""
        data = {
            'level1': {
                'level2': {
                    'level3': {
                        'level4': {
                            'password': 'deep_secret'
                        }
                    }
                }
            }
        }
        
        result = sanitize_json_data(data)
        assert result['level1']['level2']['level3']['level4']['password'] == '[FILTERED]'
    
    def test_mixed_case_sensitive_fields(self):
        """Test that sensitive field matching is case-insensitive."""
        data = {
            'PASSWORD': 'secret1',
            'Password': 'secret2',
            'pAsSwOrD': 'secret3'
        }
        
        result = sanitize_json_data(data)
        
        assert result['PASSWORD'] == '[FILTERED]'
        assert result['Password'] == '[FILTERED]'
        assert result['pAsSwOrD'] == '[FILTERED]'
    
    def test_partial_field_name_match(self):
        """Test that partial matches of sensitive fields are filtered."""
        data = {
            'user_password': 'secret',
            'client_secret_key': 'secret',
            'access_token_value': 'secret'
        }
        
        result = sanitize_json_data(data)
        
        assert result['user_password'] == '[FILTERED]'
        assert result['client_secret_key'] == '[FILTERED]'
        assert result['access_token_value'] == '[FILTERED]'


@pytest.fixture
def sample_log_data():
    """Fixture providing sample log data for testing."""
    return {
        'request_id': 'test-request-123',
        'method': 'POST',
        'url': 'http://localhost:5000/api/login?redirect=/dashboard',
        'headers': {
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
        },
        'json_data': {
            'username': 'testuser',
            'password': 'testpass123',
            'remember_me': True
        }
    }


def test_sanitize_with_fixture(sample_log_data):
    """Test sanitization using fixture data."""
    result = sanitize_log_data(sample_log_data)
    
    assert result['headers']['Authorization'] == '[FILTERED]'
    assert result['json_data']['password'] == '[FILTERED]'
    assert result['json_data']['username'] == 'testuser'
    assert result['json_data']['remember_me'] is True