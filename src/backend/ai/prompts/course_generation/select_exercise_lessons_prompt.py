import logging
from ai.prompts.base_prompt import BasePrompt
from domain.schema.courses.course import Course
from domain.schema.courses.lesson import Lesson
from .provide_exercise_lessons_tool import ProvideExerciseLessonsTool

class SelectExerciseLessonsPrompt(BasePrompt):
    def setup(self) -> None:
        pass
        
    async def get_best_lessons(self, course: Course, max_lessons: int) -> list[Lesson]:
        """
        Gets the best lessons from the given list of lessons.
        """
        from ai.models.gpt_4o import GPT4o
        model = GPT4o()
        
        self.set_system_prompt(f"""
You are a **software engineering tutor** who has been tasked with selecting the best lessons from an online course to create exercises for a student
to work on in order to apply what they have been learning. You will be presented with a list of modules and their lessons.
Your job is to select **up to {max_lessons} from the course that you think will be the most effective for the student to work on.

It's important that you include up to **{max_lessons} lessons**. This will ensure that the student gets a well-rounded experience and covers all the key topics in the course.
""")
        
        course_str = f"**Course Name**: {course.title}"
        
        for module in course.modules:
            course_str += f"\n\n- **Module**: {module.title}\n\t- **Lessons**:"
            
            for lesson in module.lessons:
                course_str += f"\n\t\t- {lesson.title} (ID: {lesson.id}): {lesson.description}"
                
        logging.info(course_str)
                
        self.add_user_message(f"""
{course_str}

Select up to **{max_lessons} lessons** that you think will be the most effective for the student to work on. Use your tool to provide the full list of IDs.
""")
    
        self.use_tool(ProvideExerciseLessonsTool, force=True)
        
        await model.get_responses(self)
        
        tool_call = self.get_tool_call(ProvideExerciseLessonsTool)
        
        if tool_call is None:
            return []
        
        return [
            lesson
            for module in course.modules
            for lesson in module.lessons
            if str(lesson.id) in tool_call.result.lesson_ids
        ]