import pytest
from unittest.mock import AsyncMock, patch, Mock
from app.services.autocomplete_service import AutocompleteService
from domain.enums.autocomplete_enums import AutocompleteLibrarySubject

# Sample data for testing
disciplines = ["web", "mobile"]
languages = ["python", "javascript"]
valid_subjects = [AutocompleteLibrarySubject.BACKEND.value, AutocompleteLibrarySubject.DEVOPS.value]
invalid_subjects = ["data", "security"]
query = "data"
school_name = "MIT"

@pytest.fixture
def mock_cache():
    with patch('app.services.autocomplete_service.get_set', new_callable=AsyncMock) as mock_get_set, \
         patch('app.services.autocomplete_service.add_to_set', new_callable=AsyncMock) as mock_add_to_set:
        mock_get_set.return_value = []  # Default to empty cache
        yield {
            'get_set': mock_get_set,
            'add_to_set': mock_add_to_set
        }

@pytest.fixture
def mock_prompt():
    with patch('app.services.autocomplete_service.AutocompletePrompt', autospec=True) as mock_prompt_class:
        mock_prompt_instance = mock_prompt_class.return_value
        mock_prompt_instance.get_options = AsyncMock()
        yield mock_prompt_instance

@pytest.mark.asyncio
async def test_get_programming_languages(mock_cache, mock_prompt):
    mock_cache['get_set'].return_value = []
    mock_prompt.get_options.return_value = ["Python", "JavaScript"]

    service = AutocompleteService()
    result = await service.get_programming_languages(disciplines, query)

    mock_cache['get_set'].assert_awaited_once()
    mock_prompt.add_user_message.assert_called_once()
    mock_prompt.get_options.assert_awaited_once()
    mock_cache['add_to_set'].assert_awaited_once()
    assert result == ["Python", "JavaScript"]

@pytest.mark.asyncio
async def test_get_libraries(mock_cache, mock_prompt):
    mock_prompt.get_options.return_value = ["NumPy", "Pandas"]

    service = AutocompleteService()
    result = await service.get_libraries(valid_subjects, languages, query)

    mock_cache['get_set'].assert_awaited_once()
    mock_prompt.add_user_message.assert_called_once()
    mock_prompt.get_options.assert_awaited_once()
    mock_cache['add_to_set'].assert_awaited_once()
    assert result == ["NumPy", "Pandas"]

@pytest.mark.asyncio
async def test_get_libraries_mixed_subjects(mock_cache, mock_prompt):
    mock_prompt.get_options.return_value = ["NumPy", "Pandas"]

    service = AutocompleteService()
    result = await service.get_libraries([*valid_subjects, *invalid_subjects], languages, query)

    mock_cache['get_set'].assert_awaited_once()
    mock_prompt.add_user_message.assert_called_once()
    mock_prompt.get_options.assert_awaited_once()
    mock_cache['add_to_set'].assert_awaited_once()
    assert result == ["NumPy", "Pandas"]

@pytest.mark.asyncio
async def test_get_educational_institutions(mock_cache, mock_prompt):
    mock_prompt.get_options.return_value = ["MIT", "Harvard"]

    service = AutocompleteService()
    result = await service.get_educational_institutions(query)

    mock_cache['get_set'].assert_awaited_once()
    mock_prompt.add_user_message.assert_called_once()
    mock_prompt.get_options.assert_awaited_once()
    mock_cache['add_to_set'].assert_awaited_once()
    assert result == ["MIT", "Harvard"]

@pytest.mark.asyncio
async def test_get_educational_focuses(mock_cache, mock_prompt):
    mock_prompt.get_options.return_value = ["Computer Science", "Physics"]

    service = AutocompleteService()
    result = await service.get_educational_focuses(school_name, query)

    mock_cache['get_set'].assert_awaited_once()
    mock_prompt.add_user_message.assert_called_once()
    mock_prompt.get_options.assert_awaited_once()
    mock_cache['add_to_set'].assert_awaited_once()
    assert result == ["Computer Science", "Physics"]

@pytest.mark.asyncio
async def test_cache_hit(mock_cache, mock_prompt):
    mock_cache['get_set'].return_value = ["Cached Result"]

    service = AutocompleteService()
    result = await service.get_programming_languages(disciplines, query)

    mock_cache['get_set'].assert_awaited_once()
    mock_prompt.add_user_message.assert_not_called()
    mock_prompt.get_options.assert_not_awaited()
    mock_cache['add_to_set'].assert_not_awaited()
    assert result == ["Cached Result"]