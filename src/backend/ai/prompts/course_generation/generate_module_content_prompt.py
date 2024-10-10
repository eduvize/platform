from typing import Callable
from ai.prompts.base_prompt import BasePrompt
from .models import CourseOutline, ModuleOutline
from domain.dto.courses import ModuleDto, LessonDto, SectionDto

ProgressCallback = Callable[[int], None] # int represents the current section number

class GenerateModuleContentPrompt(BasePrompt):
    def setup(self) -> None:
        pass
    
    async def generate_module_content(
        self, 
        course: CourseOutline, 
        module: ModuleOutline,
        progress_cb: ProgressCallback = None
    ) -> ModuleDto:
        from ai.models.gpt_4o import GPT4o
        
        module_dto = ModuleDto.model_construct(
            title=module.title,
            description=module.description,
            lessons=[]
        )
        model = GPT4o()
 
        self.set_system_prompt(f"""
You excel at writing comprehensive and detailed software engineering learning material.
You are tasked with creating the content for a module in a course named "{course.course_title}": {course.description}.

Content rules:
1. **Be Comprehensive**: Ensure each section covers the topic in depth, providing examples, explanations, and any necessary context.
2. **Use Markdown Formatting**: Properly format the text using markdown, including headers, lists, code blocks, links, and other relevant markdown elements to enhance readability.
3. **Align with Learning Objectives**: Ensure that the content directly supports the lesson's objectives and the overall focus area of the module.
4. **Build on Previous Content**: Retain context from previously generated sections within the same module to ensure continuity and cohesiveness in the learning material.

Content Markup:
- **Headers**: Use appropriate headers (e.g., `#`, `##`, `###`) to structure the content.
- **Lists**: Use bullet points or numbered lists where applicable to organize information.
- **Code Blocks**: Use fenced code blocks (```) for any code examples.
- **Links**: Include links to external resources when relevant, using markdown link syntax.
- **Explanations**: Provide clear explanations for any technical concepts, breaking down complex ideas into understandable segments.                            
""".strip())
 
        self.add_user_message(f"""
This module is named "{module.title}" and has the following description: {module.description}.
""".strip())
        
        current_section = 0
        for lesson in module.lessons:
            lesson_dto = LessonDto.model_construct(
                title=lesson.title,
                description=lesson.description,
                sections=[]
            )
            
            self.add_user_message(f"""
We will be focusing on the following lesson: {lesson.title}. {lesson.description}                       

As I provide you with sections of this lesson, you will create detailed content for this section in alignment with the lesson objectives.
""".strip())
            
            for section in lesson.sections:
                self.add_user_message(f"""
Please provide content for the following section: {section.title}. {section.description}                    
""".strip())
                messages = await model.get_responses(self)
                
                content = messages[-1].message
                
                self.add_agent_message(content)
                
                lesson_dto.sections.append(
                    SectionDto.model_construct(
                        title=section.title,
                        description=section.description,
                        content=content
                    )
                )
                
                if progress_cb:
                    current_section += 1
                    await progress_cb(current_section)

            module_dto.lessons.append(lesson_dto)
                
        return module_dto