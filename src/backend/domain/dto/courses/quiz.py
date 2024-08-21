from domain.enums.course_enums import QuizType
from domain.schema.courses.quiz import QuizBase

class QuizDto(QuizBase):
    title: str
    description: str
    quiz_type: QuizType