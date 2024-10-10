import pytest
from uuid import UUID
import base64
from unittest.mock import AsyncMock, MagicMock
from app.services.instructor_service import InstructorService
from domain.schema.instructors import Instructor
from domain.schema.user import User

# Mock data
mock_instructor_id = UUID('12345678-1234-5678-1234-567812345678')
mock_user_id = UUID('87654321-4321-8765-4321-876543210987')
mock_instructor = Instructor(id=mock_instructor_id, name="John Doe", image_url="data:image/png;base64,abc123")
mock_user = User(id=mock_user_id, default_instructor_id=mock_instructor_id)

@pytest.fixture
def instructor_service():
    instructor_repo_mock = AsyncMock()
    user_service_mock = AsyncMock()
    return InstructorService(instructor_repository=instructor_repo_mock, user_service=user_service_mock)

@pytest.mark.asyncio
async def test_get_all_instructors(instructor_service):
    # Arrange
    instructor_service.instructor_repository.get_all_instructors.return_value = [mock_instructor]

    # Act
    result = await instructor_service.get_all_instructors()

    # Assert
    assert len(result) == 1
    assert result[0] == mock_instructor
    instructor_service.instructor_repository.get_all_instructors.assert_called_once()

@pytest.mark.asyncio
async def test_get_instructor_by_id(instructor_service):
    # Arrange
    instructor_service.instructor_repository.get_instructor_by_id.return_value = mock_instructor

    # Act
    result = await instructor_service.get_instructor_by_id(mock_instructor_id)

    # Assert
    assert result == mock_instructor
    instructor_service.instructor_repository.get_instructor_by_id.assert_called_once_with(mock_instructor_id)

@pytest.mark.asyncio
async def test_get_user_instructor(instructor_service):
    # Arrange
    instructor_service.user_service.get_user.return_value = mock_user
    instructor_service.instructor_repository.get_instructor_by_id.return_value = mock_instructor

    # Act
    result = await instructor_service.get_user_instructor(mock_user_id)

    # Assert
    assert result == mock_instructor
    instructor_service.user_service.get_user.assert_called_once_with("id", mock_user_id)
    instructor_service.instructor_repository.get_instructor_by_id.assert_called_once_with(mock_instructor_id)

@pytest.mark.asyncio
async def test_get_instructor_profile_photo(instructor_service, monkeypatch):
    # Arrange
    mock_get_key = AsyncMock(return_value=None)
    mock_set_key = AsyncMock()
    monkeypatch.setattr("app.services.instructor_service.get_key", mock_get_key)
    monkeypatch.setattr("app.services.instructor_service.set_key", mock_set_key)

    # Create a small, valid PNG image as a data URI
    png_data = base64.b64encode(
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0bIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    ).decode()
    mock_instructor_with_png = Instructor(id=mock_instructor_id, name="John Doe", image_url=f"data:image/png;base64,{png_data}")
    instructor_service.instructor_repository.get_instructor_by_id.return_value = mock_instructor_with_png

    # Act
    result = await instructor_service.get_instructor_profile_photo(mock_instructor_id)

    # Assert
    expected_png_data = base64.b64decode(png_data)
    assert result == expected_png_data

