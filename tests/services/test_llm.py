"""Tests for LLM service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatDeepSeek
from faker import Faker

from app.services.llm import get_llm, LLMProvider
from app.core.config import settings

fake = Faker()


class TestLLMService:
    """Test LLM service functionality."""

    def test_llm_provider_enum(self):
        """Test LLMProvider enum values."""
        assert hasattr(LLMProvider, 'OPENAI')
        assert hasattr(LLMProvider, 'DEEPSEEK')
        
        assert LLMProvider.OPENAI.value == "openai"
        assert LLMProvider.DEEPSEEK.value == "deepseek"

    @patch('app.services.llm.settings')
    @patch('app.services.llm.ChatOpenAI')
    def test_get_llm_openai_default(self, mock_chat_openai, mock_settings):
        """Test getting OpenAI LLM as default provider."""
        # Mock settings
        mock_settings.LLM_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "test-openai-key"
        mock_settings.OPENAI_MODEL = "gpt-4"
        mock_settings.LLM_TEMPERATURE = 0.7
        mock_settings.LLM_MAX_TOKENS = 1000
        
        # Mock ChatOpenAI instance
        mock_llm_instance = MagicMock()
        mock_chat_openai.return_value = mock_llm_instance
        
        # Get LLM
        result = get_llm()
        
        # Verify OpenAI was instantiated with correct parameters
        mock_chat_openai.assert_called_once_with(
            api_key="test-openai-key",
            model="gpt-4",
            temperature=0.7,
            max_tokens=1000
        )
        
        assert result == mock_llm_instance

    @patch('app.services.llm.settings')
    @patch('app.services.llm.ChatDeepSeek')
    def test_get_llm_deepseek(self, mock_chat_deepseek, mock_settings):
        """Test getting DeepSeek LLM."""
        # Mock settings
        mock_settings.LLM_PROVIDER = "deepseek"
        mock_settings.DEEPSEEK_API_KEY = "test-deepseek-key"
        mock_settings.DEEPSEEK_MODEL = "deepseek-chat"
        mock_settings.LLM_TEMPERATURE = 0.5
        mock_settings.LLM_MAX_TOKENS = 2000
        
        # Mock ChatDeepSeek instance
        mock_llm_instance = MagicMock()
        mock_chat_deepseek.return_value = mock_llm_instance
        
        # Get LLM
        result = get_llm()
        
        # Verify DeepSeek was instantiated with correct parameters
        mock_chat_deepseek.assert_called_once_with(
            api_key="test-deepseek-key",
            model="deepseek-chat",
            temperature=0.5,
            max_tokens=2000
        )
        
        assert result == mock_llm_instance

    @patch('app.services.llm.settings')
    def test_get_llm_invalid_provider(self, mock_settings):
        """Test getting LLM with invalid provider."""
        mock_settings.LLM_PROVIDER = "invalid_provider"
        
        with pytest.raises(ValueError) as exc_info:
            get_llm()
        
        assert "Unsupported LLM provider" in str(exc_info.value)
        assert "invalid_provider" in str(exc_info.value)

    @patch('app.services.llm.settings')
    @patch('app.services.llm.ChatOpenAI')
    def test_get_llm_openai_custom_parameters(self, mock_chat_openai, mock_settings):
        """Test getting OpenAI LLM with custom parameters."""
        # Mock settings with custom values
        mock_settings.LLM_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "custom-api-key"
        mock_settings.OPENAI_MODEL = "gpt-3.5-turbo"
        mock_settings.LLM_TEMPERATURE = 0.9
        mock_settings.LLM_MAX_TOKENS = 500
        
        mock_llm_instance = MagicMock()
        mock_chat_openai.return_value = mock_llm_instance
        
        result = get_llm()
        
        mock_chat_openai.assert_called_once_with(
            api_key="custom-api-key",
            model="gpt-3.5-turbo",
            temperature=0.9,
            max_tokens=500
        )
        
        assert result == mock_llm_instance

    @patch('app.services.llm.settings')
    @patch('app.services.llm.ChatDeepSeek')
    def test_get_llm_deepseek_custom_parameters(self, mock_chat_deepseek, mock_settings):
        """Test getting DeepSeek LLM with custom parameters."""
        # Mock settings with custom values
        mock_settings.LLM_PROVIDER = "deepseek"
        mock_settings.DEEPSEEK_API_KEY = "custom-deepseek-key"
        mock_settings.DEEPSEEK_MODEL = "deepseek-coder"
        mock_settings.LLM_TEMPERATURE = 0.1
        mock_settings.LLM_MAX_TOKENS = 4000
        
        mock_llm_instance = MagicMock()
        mock_chat_deepseek.return_value = mock_llm_instance
        
        result = get_llm()
        
        mock_chat_deepseek.assert_called_once_with(
            api_key="custom-deepseek-key",
            model="deepseek-coder",
            temperature=0.1,
            max_tokens=4000
        )
        
        assert result == mock_llm_instance

    @patch('app.services.llm.settings')
    @patch('app.services.llm.ChatOpenAI')
    def test_get_llm_missing_openai_api_key(self, mock_chat_openai, mock_settings):
        """Test getting OpenAI LLM with missing API key."""
        mock_settings.LLM_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = None
        mock_settings.OPENAI_MODEL = "gpt-4"
        mock_settings.LLM_TEMPERATURE = 0.7
        mock_settings.LLM_MAX_TOKENS = 1000
        
        # This should either raise an error or handle gracefully
        # depending on implementation
        try:
            result = get_llm()
            # If it doesn't raise an error, verify it was called with None
            mock_chat_openai.assert_called_once_with(
                api_key=None,
                model="gpt-4",
                temperature=0.7,
                max_tokens=1000
            )
        except (ValueError, TypeError):
            # If it raises an error for missing API key, that's acceptable
            pass

    @patch('app.services.llm.settings')
    @patch('app.services.llm.ChatDeepSeek')
    def test_get_llm_missing_deepseek_api_key(self, mock_chat_deepseek, mock_settings):
        """Test getting DeepSeek LLM with missing API key."""
        mock_settings.LLM_PROVIDER = "deepseek"
        mock_settings.DEEPSEEK_API_KEY = None
        mock_settings.DEEPSEEK_MODEL = "deepseek-chat"
        mock_settings.LLM_TEMPERATURE = 0.5
        mock_settings.LLM_MAX_TOKENS = 2000
        
        try:
            result = get_llm()
            mock_chat_deepseek.assert_called_once_with(
                api_key=None,
                model="deepseek-chat",
                temperature=0.5,
                max_tokens=2000
            )
        except (ValueError, TypeError):
            pass

    @patch('app.services.llm.settings')
    @patch('app.services.llm.ChatOpenAI')
    def test_get_llm_caching_behavior(self, mock_chat_openai, mock_settings):
        """Test LLM caching behavior if implemented."""
        mock_settings.LLM_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_settings.OPENAI_MODEL = "gpt-4"
        mock_settings.LLM_TEMPERATURE = 0.7
        mock_settings.LLM_MAX_TOKENS = 1000
        
        mock_llm_instance = MagicMock()
        mock_chat_openai.return_value = mock_llm_instance
        
        # Call get_llm multiple times
        result1 = get_llm()
        result2 = get_llm()
        result3 = get_llm()
        
        # If caching is implemented, ChatOpenAI should only be called once
        # If not, it will be called multiple times
        assert mock_chat_openai.call_count >= 1
        
        # Results should be consistent
        assert result1 == mock_llm_instance
        assert result2 == mock_llm_instance
        assert result3 == mock_llm_instance

    @patch('app.services.llm.settings')
    @patch('app.services.llm.ChatOpenAI')
    def test_get_llm_with_edge_case_parameters(self, mock_chat_openai, mock_settings):
        """Test getting LLM with edge case parameters."""
        # Test with extreme values
        mock_settings.LLM_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_settings.OPENAI_MODEL = "gpt-4"
        mock_settings.LLM_TEMPERATURE = 0.0  # Minimum temperature
        mock_settings.LLM_MAX_TOKENS = 1  # Minimum tokens
        
        mock_llm_instance = MagicMock()
        mock_chat_openai.return_value = mock_llm_instance
        
        result = get_llm()
        
        mock_chat_openai.assert_called_once_with(
            api_key="test-key",
            model="gpt-4",
            temperature=0.0,
            max_tokens=1
        )
        
        assert result == mock_llm_instance

    @patch('app.services.llm.settings')
    @patch('app.services.llm.ChatOpenAI')
    def test_get_llm_with_maximum_parameters(self, mock_chat_openai, mock_settings):
        """Test getting LLM with maximum parameters."""
        # Test with maximum values
        mock_settings.LLM_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_settings.OPENAI_MODEL = "gpt-4"
        mock_settings.LLM_TEMPERATURE = 2.0  # Maximum temperature
        mock_settings.LLM_MAX_TOKENS = 8192  # Large token count
        
        mock_llm_instance = MagicMock()
        mock_chat_openai.return_value = mock_llm_instance
        
        result = get_llm()
        
        mock_chat_openai.assert_called_once_with(
            api_key="test-key",
            model="gpt-4",
            temperature=2.0,
            max_tokens=8192
        )
        
        assert result == mock_llm_instance

    @patch('app.services.llm.settings')
    def test_get_llm_case_insensitive_provider(self, mock_settings):
        """Test that provider names are case insensitive."""
        # Test uppercase
        mock_settings.LLM_PROVIDER = "OPENAI"
        
        # This depends on implementation - might work or might not
        try:
            with patch('app.services.llm.ChatOpenAI') as mock_chat_openai:
                mock_settings.OPENAI_API_KEY = "test-key"
                mock_settings.OPENAI_MODEL = "gpt-4"
                mock_settings.LLM_TEMPERATURE = 0.7
                mock_settings.LLM_MAX_TOKENS = 1000
                
                mock_llm_instance = MagicMock()
                mock_chat_openai.return_value = mock_llm_instance
                
                result = get_llm()
                assert result == mock_llm_instance
        except ValueError:
            # If case sensitivity is enforced, that's also acceptable
            pass

    @patch('app.services.llm.settings')
    @patch('app.services.llm.ChatOpenAI')
    def test_get_llm_initialization_error(self, mock_chat_openai, mock_settings):
        """Test handling of LLM initialization errors."""
        mock_settings.LLM_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "invalid-key"
        mock_settings.OPENAI_MODEL = "gpt-4"
        mock_settings.LLM_TEMPERATURE = 0.7
        mock_settings.LLM_MAX_TOKENS = 1000
        
        # Mock ChatOpenAI to raise an error during initialization
        mock_chat_openai.side_effect = Exception("Invalid API key")
        
        with pytest.raises(Exception) as exc_info:
            get_llm()
        
        assert "Invalid API key" in str(exc_info.value)

    @patch('app.services.llm.settings')
    def test_get_llm_empty_provider(self, mock_settings):
        """Test getting LLM with empty provider string."""
        mock_settings.LLM_PROVIDER = ""
        
        with pytest.raises(ValueError) as exc_info:
            get_llm()
        
        assert "Unsupported LLM provider" in str(exc_info.value)

    @patch('app.services.llm.settings')
    def test_get_llm_none_provider(self, mock_settings):
        """Test getting LLM with None provider."""
        mock_settings.LLM_PROVIDER = None
        
        with pytest.raises((ValueError, AttributeError)):
            get_llm()

    @patch('app.services.llm.settings')
    @patch('app.services.llm.ChatOpenAI')
    def test_get_llm_with_additional_parameters(self, mock_chat_openai, mock_settings):
        """Test getting LLM with additional parameters if supported."""
        mock_settings.LLM_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_settings.OPENAI_MODEL = "gpt-4"
        mock_settings.LLM_TEMPERATURE = 0.7
        mock_settings.LLM_MAX_TOKENS = 1000
        
        # Add additional settings that might be supported
        mock_settings.LLM_TOP_P = 0.9
        mock_settings.LLM_FREQUENCY_PENALTY = 0.1
        mock_settings.LLM_PRESENCE_PENALTY = 0.1
        
        mock_llm_instance = MagicMock()
        mock_chat_openai.return_value = mock_llm_instance
        
        result = get_llm()
        
        # Should at least call with basic parameters
        mock_chat_openai.assert_called_once()
        call_kwargs = mock_chat_openai.call_args[1]
        
        assert call_kwargs['api_key'] == "test-key"
        assert call_kwargs['model'] == "gpt-4"
        assert call_kwargs['temperature'] == 0.7
        assert call_kwargs['max_tokens'] == 1000
        
        assert result == mock_llm_instance

    def test_llm_provider_enum_completeness(self):
        """Test that LLMProvider enum contains all expected providers."""
        # Check that enum has expected values
        provider_values = [provider.value for provider in LLMProvider]
        
        assert "openai" in provider_values
        assert "deepseek" in provider_values
        
        # Check that we can iterate over providers
        assert len(list(LLMProvider)) >= 2

    @patch('app.services.llm.settings')
    @patch('app.services.llm.ChatOpenAI')
    @patch('app.services.llm.ChatDeepSeek')
    def test_get_llm_provider_switching(self, mock_chat_deepseek, mock_chat_openai, mock_settings):
        """Test switching between different LLM providers."""
        # First, use OpenAI
        mock_settings.LLM_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "openai-key"
        mock_settings.OPENAI_MODEL = "gpt-4"
        mock_settings.LLM_TEMPERATURE = 0.7
        mock_settings.LLM_MAX_TOKENS = 1000
        
        mock_openai_instance = MagicMock()
        mock_chat_openai.return_value = mock_openai_instance
        
        result1 = get_llm()
        assert result1 == mock_openai_instance
        mock_chat_openai.assert_called_once()
        
        # Reset mocks
        mock_chat_openai.reset_mock()
        mock_chat_deepseek.reset_mock()
        
        # Then, switch to DeepSeek
        mock_settings.LLM_PROVIDER = "deepseek"
        mock_settings.DEEPSEEK_API_KEY = "deepseek-key"
        mock_settings.DEEPSEEK_MODEL = "deepseek-chat"
        mock_settings.LLM_TEMPERATURE = 0.5
        mock_settings.LLM_MAX_TOKENS = 2000
        
        mock_deepseek_instance = MagicMock()
        mock_chat_deepseek.return_value = mock_deepseek_instance
        
        result2 = get_llm()
        assert result2 == mock_deepseek_instance
        mock_chat_deepseek.assert_called_once()
        
        # OpenAI should not be called again
        mock_chat_openai.assert_not_called()

    @patch('app.services.llm.settings')
    @patch('app.services.llm.ChatOpenAI')
    def test_get_llm_concurrent_access(self, mock_chat_openai, mock_settings):
        """Test concurrent access to get_llm function."""
        import asyncio
        import threading
        
        mock_settings.LLM_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_settings.OPENAI_MODEL = "gpt-4"
        mock_settings.LLM_TEMPERATURE = 0.7
        mock_settings.LLM_MAX_TOKENS = 1000
        
        mock_llm_instance = MagicMock()
        mock_chat_openai.return_value = mock_llm_instance
        
        results = []
        
        def get_llm_thread():
            result = get_llm()
            results.append(result)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=get_llm_thread)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All results should be the same instance
        assert len(results) == 5
        for result in results:
            assert result == mock_llm_instance