from enum import Enum

class CourseMotivation(Enum):
    CAREER = "career"
    SKILL_ENHANCEMENT = "skill_enhancement"
    PROJECT = "project_requirement"
    CERTIFICATION = "certification"
    OTHER = "other"

class CurrentSubjectExperience(Enum):
    NEW = "new"
    EXISTING = "existing"
    REFRESH = "returning"
    KNOWLEDGEABLE = "knowledgeable"
    
class CourseMaterial(Enum):
    READING = "reading_material"
    HANDS_ON_PRACTICE = "hands_on_practice"
    PROJECT = "project_work"

class QuizType(Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"