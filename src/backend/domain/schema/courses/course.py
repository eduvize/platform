from sqlmodel import SQLModel
from .module import ModuleBase

class CourseBase(SQLModel):
    title: str
    description: str
    
    modules: list[ModuleBase]