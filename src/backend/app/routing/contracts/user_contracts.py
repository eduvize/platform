from typing import Optional
from domain.dto.profile import UserProfileDto

class UpdateProfilePayload(UserProfileDto):
    avatar_file_id: Optional[str] = None