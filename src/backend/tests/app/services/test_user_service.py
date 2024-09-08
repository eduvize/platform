from io import BytesIO
import pytest
from unittest.mock import AsyncMock, patch
from app.services.user_service import UserService, UserCreationError
from common.storage import StoragePurpose
from domain.enums.auth import OAuthProvider
from domain.dto.profile import UserProfileDto
from app.repositories import UserRepository
from app.services.user_onboarding_service import UserOnboardingService
from fastapi import UploadFile

@pytest.fixture
def mock_user_repo():
    return AsyncMock(spec=UserRepository)

@pytest.fixture
def mock_onboarding_service():
    return AsyncMock(spec=UserOnboardingService)

@pytest.fixture
def user_service(mock_user_repo, mock_onboarding_service):
    return UserService(user_repo=mock_user_repo, user_onboarding_service=mock_onboarding_service)

@patch("app.services.user_service.is_email_validation_enabled", return_value=False)
@pytest.mark.asyncio
async def test_create_user_success(mock_is_email_validation_enabled, user_service, mock_user_repo):
    """
    Test the successful creation of a user.
    
    Assertions:
    1. Ensure the repository is queried to check if the email and username are already in use.
    2. Ensure a user is created in the repository with the correct attributes.
    3. Ensure the onboarding service sends an email if email validation is enabled.
    """
    # Setup mock return values
    mock_user_repo.get_user.side_effect = [None, None]  # No existing user (email and username checks)
    mock_user_repo.create_user.return_value = AsyncMock()
    
    # Mock is_email_validation_enabled to return True
    mock_is_email_validation_enabled.return_value = True

    # Run the method
    await user_service.create_user("test@example.com", "testuser", "hashed_password")

    # Assertions
    mock_user_repo.get_user.assert_any_await("email", "test@example.com")  # 1
    mock_user_repo.get_user.assert_any_await("username", "testuser")  # 1
    mock_user_repo.create_user.assert_awaited_once_with(
        email_address="test@example.com",
        username="testuser",
        password_hash="hashed_password",
        set_email_validated=False
    )  # 2
    user_service.onboarding_service.send_verification_email.assert_awaited_once()  # 3

@pytest.mark.asyncio
async def test_create_user_email_in_use(user_service, mock_user_repo):
    """
    Test user creation fails when email is already in use.
    
    Assertions:
    1. Ensure the repository is queried for the email.
    2. Ensure UserCreationError is raised if email is already in use.
    """
    mock_user_repo.get_user.side_effect = [AsyncMock(), None]  # Existing email

    with pytest.raises(UserCreationError):
        await user_service.create_user("test@example.com", "testuser", "hashed_password")

    mock_user_repo.get_user.assert_any_await("email", "test@example.com")  # 1
    mock_user_repo.get_user.assert_any_await("username", "testuser")  # 1

@patch("app.services.user_service.import_from_url", autospec=True)
@patch("app.services.user_service.get_public_object_url", autospec=True)
@pytest.mark.asyncio
async def test_create_external_user_success(mock_get_public_object_url, mock_import_from_url, user_service, mock_user_repo):
    """
    Test the successful creation of an external user.
    
    Assertions:
    1. Ensure the repository is queried for existing user by email.
    2. Ensure the avatar URL is processed and uploaded.
    3. Ensure a user is created in the repository with external auth.
    4. Ensure the user's avatar URL is updated.
    """
    mock_import_from_url.return_value = "avatar-object-id"
    mock_get_public_object_url.return_value = "http://example.com/avatar.jpg"
    mock_user_repo.get_user.return_value = None  # No existing email
    mock_user_repo.create_user.return_value = AsyncMock(id="user-id")
    mock_user_repo.create_external_auth.return_value = None
    mock_user_repo.set_avatar_url.return_value = None

    # Run the method
    await user_service.create_external_user(
        provider=OAuthProvider.GITHUB,
        user_id="external-id",
        email_address="test@example.com",
        avatar_url="http://example.com/avatar.jpg"
    )

    # Assertions
    mock_user_repo.get_user.assert_awaited_once_with("email", "test@example.com")  # 1
    mock_user_repo.create_user.assert_awaited_once()  # 3
    mock_user_repo.create_external_auth.assert_awaited_once_with(user_id="user-id", provider="github", external_id="external-id")  # 3
    mock_user_repo.set_avatar_url.assert_awaited_once_with(user_id="user-id", avatar_url="http://example.com/avatar.jpg")  # 4

@patch("app.services.user_service.upload_object", autospec=True)
@patch("app.services.user_service.get_public_object_url", autospec=True)
@pytest.mark.asyncio
async def test_upload_avatar(mock_get_public_object_url, mock_upload_object, user_service, mock_user_repo):
    """
    Test the avatar upload process.
    
    Assertions:
    1. Ensure the user is retrieved by ID.
    2. Ensure the avatar file is uploaded and URL is set correctly.
    3. The upload_object function is called with the correct arguments.
    """
    # Mock the user and the file
    mock_user_repo.get_user.return_value = AsyncMock(id="user-id")
    mock_file = AsyncMock(spec=UploadFile)
    mock_file.file = BytesIO(b"dummy file content")
    mock_file.filename = "avatar.png"
    mock_get_public_object_url.return_value = "http://example.com/avatar.png"
    mock_upload_object.return_value = "object-id"

    # Run the method
    avatar_url = await user_service.upload_avatar(user_id="user-id", file=mock_file)

    # Assertions
    mock_user_repo.get_user.assert_awaited_once_with("id", "user-id", ['profile.*'])  # 1
    user_service.user_repo.set_avatar_url.assert_awaited_once_with(user_id="user-id", avatar_url="http://example.com/avatar.png")  # 2
    mock_upload_object.assert_awaited_once_with(StoragePurpose.AVATAR, mock_file.file, ".png")