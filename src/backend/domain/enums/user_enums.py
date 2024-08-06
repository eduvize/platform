from enum import Enum


class UserSkillType(Enum):
    PROGRAMMING_LANGUAGE = 1
    LIBRARY = 2
    
class UserLearningCapacity(Enum):
    HOBBY = "hobby"
    STUDENT = "student"
    PROFESSIONAL = "professional"
    
class UserDiscipline(Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATABASE = "database"
    DEVOPS = "devops"