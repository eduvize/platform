import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.validation_service import ValidationService
from domain.dto.ai.assertion_result import AssertionResultDto

@pytest.fixture
def mock_user_service():
    return AsyncMock()

@pytest.fixture
def validation_service(mock_user_service):
    return ValidationService(user_service=mock_user_service)

@patch("app.services.validation_service.AssertionPrompt", autospec=True)
@patch("app.services.validation_service.set_key", autospec=True)
@patch("app.services.validation_service.get_key", autospec=True)
@pytest.mark.asyncio
async def test_perform_assertion_with_cache_hit(mock_get_key, mock_set_key, mock_assertion_prompt, validation_service):
    """
    Test the assertion logic when there is a cache hit.
    
    Assertions:
    1. Ensure `get_key` is called with the correct cache key.
    2. Ensure `AssertionResult` is built from cached data and returned without generating a new assertion.
    3. Ensure the prompt is not called.
    """
    # Mock data
    cached_result = AssertionResultDto(assertion=True, reason="Correct").model_dump_json()
    mock_get_key.return_value = cached_result
    mock_prompt_instance = MagicMock()
    mock_assertion_prompt.return_value = mock_prompt_instance
    mock_prompt_instance.get_assertion.return_value = (True, "Correct")
    
    result = await validation_service.perform_assertion(statement="Is the sky blue?")
    
    # Assertions
    mock_get_key.assert_called_once_with("assertion_Is the sky blue?")  # 1
    assert result.assertion == True  # 2
    assert result.reason == "Correct"  # 2
    mock_set_key.assert_not_called()  # No need to set cache when there's a hit
    mock_prompt_instance.get_assertion.assert_not_called()  # 3

@patch("app.services.validation_service.AssertionPrompt", autospec=True)
@patch("app.services.validation_service.set_key", autospec=True)
@patch("app.services.validation_service.get_key", autospec=True)
@pytest.mark.asyncio
async def test_perform_assertion_with_cache_miss(mock_get_key, mock_set_key, mock_assertion_prompt, validation_service):
    """
    Test the assertion logic when there is a cache miss.
    
    Assertions:
    1. Ensure `get_key` is called with the correct cache key and returns None.
    2. Ensure a new assertion is generated using `AssertionPrompt`.
    3. Ensure the result is stored in the cache.
    4. Ensure the correct `AssertionResult` is returned.
    """
    # Mock data
    mock_get_key.return_value = None
    mock_prompt_instance = MagicMock()
    mock_assertion_prompt.return_value = mock_prompt_instance
    mock_prompt_instance.get_assertion.return_value = (False, "Incorrect")
    
    result = await validation_service.perform_assertion(statement="Is the sky green?")
    
    # Assertions
    mock_get_key.assert_called_once_with("assertion_Is the sky green?")  # 1
    mock_prompt_instance.get_assertion.assert_called_once_with(statement="Is the sky green?")  # 2
    mock_set_key.assert_called_once()  # 3
    assert result.assertion == False  # 4
    assert result.reason == "Incorrect"  # 4
