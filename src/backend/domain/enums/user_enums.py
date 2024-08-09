from enum import Enum


class UserSkillType(Enum):
    PROGRAMMING_LANGUAGE = 1
    LIBRARY = 2
    
class UserLearningCapacity(Enum):
    HOBBY = "hobby"
    STUDENT = "student"
    PROFESSIONAL = "professional"
    
class UserDiscipline(Enum):
    FRONTEND = 1
    BACKEND = 2
    DATABASE = 3
    DEVOPS = 4