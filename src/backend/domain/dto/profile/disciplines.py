from pydantic import BaseModel
from domain.schema.profile.disciplines import UserProfileBackendBase, UserProfileDatabaseBase, UserProfileDevopsBase, UserProfileFrontendBase

class UserProfileFrontend(UserProfileFrontendBase):
    pass

class UserProfileBackend(UserProfileBackendBase):
    pass

class UserProfileDatabase(UserProfileDatabaseBase):
    pass

class UserProfileDevops(UserProfileDevopsBase):
    pass