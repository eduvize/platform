from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel, field_validator

class Discipline(Enum):
    FRONTEND = "Frontend"
    BACKEND = "Backend"
    DATABASE = "Database"
    DEVOPS = "DevOps"

class HobbyProject(BaseModel):
    project_name: str
    description: str
    purpose: Optional[str] = None
    programming_languages: List[str]
    frameworks: List[str]
    libraries: List[str]
    
class School(BaseModel):
    school_name: str
    focus: Optional[str] = None
    start_month: Optional[date] = None
    end_month: Optional[date] = None
    did_finish: bool
    is_current: bool
    
class Employment(BaseModel):
    company_name: str
    position: str
    start_month: Optional[date] = None
    end_month: Optional[date] = None
    is_current: bool
    description: str

class ProfileScan(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    github_username: Optional[str] = None
    is_hobbyist: bool
    has_educational_background: bool
    has_industry_experience: bool
    disciplines: List[Discipline] = []
    programming_languages: List[str] = []
    frameworks: List[str] = []
    libraries: List[str] = []
    
    hobby_projects: List[HobbyProject] = []
    schools: List[School] = []
    employers: List[Employment] = []