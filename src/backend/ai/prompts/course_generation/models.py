from typing import Optional
from pydantic import BaseModel, field_validator

class SectionOutline(BaseModel):
    title: str
    long_description_of_content: str

class LessonOutline(BaseModel):
    internal_name: str
    focus_area: str
    title: str
    long_objective_description: str
    sections: list[SectionOutline]
    
    @field_validator("sections", mode="after")
    def verify_sections_exist(cls, value):
        if not value:
            raise ValueError("All lessons must contain sections")
        
        return value

class ModuleOutline(BaseModel):
    internal_name: str
    title: str
    focus_area: str
    long_objective_description: str
    lessons: list[LessonOutline]
    
    @field_validator("lessons", mode="after")
    def verify_lessons_exist(cls, value):
        if not value:
            raise ValueError("All modules must contain lessons")
        
        return value

class CourseOutline(BaseModel):
    course_subject: str
    course_title: str
    long_description: str
    modules: list[ModuleOutline]
    key_outcomes: list[str]
    
    @field_validator("modules", mode="after")
    def verify_modules_exist(cls, value):
        if not value:
            raise ValueError("A course must contain modules")
        
        return value