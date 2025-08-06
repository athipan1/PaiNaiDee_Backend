import pytest
import json
import os
from unittest.mock import patch, MagicMock
from src.app import create_app
from src.services.talk_service import TalkService


class TestTalkEndpoint:
    
    @pytest.fixture
    def app(self):
        app = create_app("testing")
        return app
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    def test_talk_endpoint_basic_request(self, client):
        """Test basic talk endpoint functionality."""
        data = {
            "sender": "A",
            "receiver": "B", 
            "message": "Hello, can you recommend some attractions in Bangkok?"
        }
        
        response = client.post('/api/talk', 
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert response_data['success'] is True
        assert 'data' in response_data
        assert 'reply' in response_data['data']
        assert isinstance(response_data['data']['reply'], str)
        assert len(response_data['data']['reply']) > 0
    
    def test_talk_endpoint_with_session_id(self, client):
        """Test talk endpoint with session management."""
        data = {
            "sender": "A",
            "receiver": "B",
            "message": "Tell me about Thai food",
            "session_id": "test-session-123"
        }
        
        response = client.post('/api/talk',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert response_data['success'] is True
        assert response_data['data']['session_id'] == "test-session-123"
    
    def test_talk_endpoint_missing_required_fields(self, client):
        """Test validation with missing required fields."""
        test_cases = [
            {},  # Empty request
            {"sender": "A"},  # Missing receiver and message
            {"sender": "A", "receiver": "B"},  # Missing message
            {"message": "Hello"},  # Missing sender and receiver
        ]
        
        for data in test_cases:
            response = client.post('/api/talk',
                                 data=json.dumps(data),
                                 content_type='application/json')
            
            assert response.status_code == 400
            response_data = json.loads(response.data)
            assert response_data['success'] is False
    
    def test_talk_endpoint_invalid_field_lengths(self, client):
        """Test validation with invalid field lengths."""
        # Test message too long
        long_message = "x" * 2001  # Exceeds 2000 character limit
        data = {
            "sender": "A",
            "receiver": "B",
            "message": long_message
        }
        
        response = client.post('/api/talk',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
    
    def test_talk_endpoint_empty_strings(self, client):
        """Test validation with empty strings."""
        data = {
            "sender": "",
            "receiver": "",
            "message": ""
        }
        
        response = client.post('/api/talk',
                             data=json.dumps(data),
                             content_type='application/json')
        
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
    
    def test_get_session_info(self, client):
        """Test getting session information."""
        # First, create a session by sending a message
        data = {
            "sender": "A",
            "receiver": "B",
            "message": "Hello",
            "session_id": "info-test-session"
        }
        
        client.post('/api/talk',
                   data=json.dumps(data),
                   content_type='application/json')
        
        # Then get session info
        response = client.get('/api/talk/session/info-test-session')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert response_data['success'] is True
        assert 'data' in response_data
        assert response_data['data']['exists'] is True
        assert response_data['data']['message_count'] >= 0
    
    def test_get_session_info_nonexistent(self, client):
        """Test getting info for non-existent session."""
        response = client.get('/api/talk/session/nonexistent-session')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert response_data['success'] is True
        assert response_data['data']['exists'] is False
        assert response_data['data']['message_count'] == 0
    
    def test_clear_session(self, client):
        """Test clearing a session."""
        # First, create a session
        data = {
            "sender": "A",
            "receiver": "B",
            "message": "Hello",
            "session_id": "clear-test-session"
        }
        
        client.post('/api/talk',
                   data=json.dumps(data),
                   content_type='application/json')
        
        # Clear the session
        response = client.delete('/api/talk/session/clear-test-session')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        
        # Verify session is cleared
        info_response = client.get('/api/talk/session/clear-test-session')
        info_data = json.loads(info_response.data)
        assert info_data['data']['exists'] is False
    
    def test_clear_nonexistent_session(self, client):
        """Test clearing a non-existent session."""
        response = client.delete('/api/talk/session/nonexistent-session')
        
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert response_data['success'] is False
    
    def test_get_available_roles(self, client):
        """Test getting available role configurations."""
        response = client.get('/api/talk/roles')
        
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert response_data['success'] is True
        assert 'data' in response_data
        assert 'roles' in response_data['data']
        assert 'A' in response_data['data']['roles']
        assert 'B' in response_data['data']['roles']
        
        # Check role structure
        role_a = response_data['data']['roles']['A']
        assert 'name' in role_a
        assert 'personality' in role_a
        assert 'style' in role_a


class TestTalkService:
    
    def test_talk_service_initialization(self):
        """Test TalkService initialization."""
        service = TalkService()
        assert service.max_tokens > 0
        assert service.temperature >= 0
        assert isinstance(service.DEFAULT_ROLES, dict)
        assert 'A' in service.DEFAULT_ROLES
        assert 'B' in service.DEFAULT_ROLES
    
    def test_get_role_prompt(self):
        """Test role prompt generation."""
        service = TalkService()
        
        prompt_a = service._get_role_prompt('A')
        prompt_b = service._get_role_prompt('B')
        prompt_unknown = service._get_role_prompt('unknown')
        
        assert isinstance(prompt_a, str)
        assert isinstance(prompt_b, str)
        assert isinstance(prompt_unknown, str)
        assert len(prompt_a) > 0
        assert len(prompt_b) > 0
        assert 'User' in prompt_a
        assert 'Assistant' in prompt_b
    
    def test_session_context_management(self):
        """Test session context management."""
        service = TalkService()
        session_id = "test-session"
        
        # Initially empty
        context = service._get_session_context(session_id)
        assert context == []
        
        # Add context
        service._update_session_context(session_id, "Hello", "Hi there!", "A", "B")
        context = service._get_session_context(session_id)
        assert len(context) == 2
        assert context[0]['role'] == 'user'
        assert context[1]['role'] == 'assistant'
        assert '[A]:' in context[0]['content']
        assert '[B]:' in context[1]['content']
    
    def test_session_context_trimming(self):
        """Test session context trimming when it gets too long."""
        service = TalkService()
        service.max_context_length = 2  # Set small limit for testing
        session_id = "trim-test-session"
        
        # Add many messages to exceed the limit
        for i in range(5):
            service._update_session_context(
                session_id, f"Message {i}", f"Reply {i}", "A", "B"
            )
        
        context = service._get_session_context(session_id)
        # Should be trimmed to max_context_length * 2 (2 * 2 = 4 messages)
        assert len(context) <= service.max_context_length * 2
    
    def test_fallback_response_generation(self):
        """Test fallback response generation."""
        service = TalkService()
        
        test_cases = [
            ("hello", "greeting"),
            ("Bangkok", "bangkok"),
            ("beach", "beach"),
            ("food", "food"),
            ("random question", "general")
        ]
        
        for message, expected_type in test_cases:
            response = service._generate_fallback_response("A", "B", message)
            assert isinstance(response, str)
            assert len(response) > 0
    
    def test_generate_response_fallback_mode(self):
        """Test response generation in fallback mode (no OpenAI)."""
        service = TalkService()
        service.client = None  # Force fallback mode
        
        result = service.generate_response(
            sender="A",
            receiver="B", 
            message="Hello, tell me about Bangkok",
            session_id="fallback-test"
        )
        
        assert isinstance(result, dict)
        assert 'reply' in result
        assert 'session_id' in result
        assert isinstance(result['reply'], str)
        assert len(result['reply']) > 0
        assert result['session_id'] == "fallback-test"
    
    @patch('src.services.talk_service.OpenAI')
    def test_generate_response_with_openai(self, mock_openai):
        """Test response generation with mocked OpenAI."""
        # Mock OpenAI response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "This is a test response from OpenAI"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Set environment variables to enable OpenAI
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            service = TalkService()
            service.client = mock_client
            
            result = service.generate_response(
                sender="A",
                receiver="B",
                message="Test message",
                session_id="openai-test"
            )
            
            assert isinstance(result, dict)
            assert 'reply' in result
            assert result['reply'] == "This is a test response from OpenAI"
            assert mock_client.chat.completions.create.called
    
    def test_clear_session(self):
        """Test session clearing."""
        service = TalkService()
        session_id = "clear-test"
        
        # Create a session
        service._update_session_context(session_id, "Hello", "Hi", "A", "B")
        assert service.get_session_info(session_id)['exists'] is True
        
        # Clear it
        result = service.clear_session(session_id)
        assert result is True
        assert service.get_session_info(session_id)['exists'] is False
        
        # Try to clear non-existent session
        result = service.clear_session("nonexistent")
        assert result is False
    
    def test_get_session_info(self):
        """Test getting session information."""
        service = TalkService()
        session_id = "info-test"
        
        # Non-existent session
        info = service.get_session_info(session_id)
        assert info['exists'] is False
        assert info['message_count'] == 0
        
        # Create session
        service._update_session_context(session_id, "Hello", "Hi", "A", "B")
        info = service.get_session_info(session_id)
        assert info['exists'] is True
        assert info['message_count'] == 2  # User message + assistant reply
        assert 'max_context' in info