import json
import logging
from ai.prompts.base_prompt import BasePrompt
from .models import CourseOutline, ModuleOutline
from domain.dto.courses import ModuleDto, LessonDto, SectionDto

class GenerateModuleContentPrompt(BasePrompt):
    def setup(self) -> None:
        self.set_system_prompt("""
You are an AI assistant tasked with generating comprehensive and detailed markdown content for educational modules in a software engineering course. Each module consists of multiple lessons, and your goal is to write learning material that aligns with the lesson objectives and the overall module's focus area. The content should be structured, informative, and written in a way that is engaging and easy for students to follow.

The content you generate should:
1. **Be Comprehensive**: Ensure each section covers the topic in depth, providing examples, explanations, and any necessary context.
2. **Use Markdown Formatting**: Properly format the text using markdown, including headers, lists, code blocks, links, and other relevant markdown elements to enhance readability.
3. **Align with Learning Objectives**: Ensure that the content directly supports the lesson's objectives and the overall focus area of the module.
4. **Build on Previous Content**: Retain context from previously generated sections within the same module to ensure continuity and cohesiveness in the learning material.

### Guidelines for Content:
- **Headers**: Use appropriate headers (e.g., `#`, `##`, `###`) to structure the content.
- **Lists**: Use bullet points or numbered lists where applicable to organize information.
- **Code Blocks**: Use fenced code blocks (```) for any code examples.
- **Links**: Include links to external resources when relevant, using markdown link syntax.
- **Explanations**: Provide clear explanations for any technical concepts, breaking down complex ideas into understandable segments.                            
""")
    
    def generate_module_content(
        self, 
        course: CourseOutline, 
        module: ModuleOutline
    ) -> ModuleDto:
        from ai.models.gpt_4o import GPT4o
        
        module_dto = ModuleDto.model_construct(
            title=module.title,
            description=module.description,
            lessons=[]
        )
        model = GPT4o()
 
        key_outcomes_str = "\n".join([f"- {outcome}" for outcome in course.key_outcomes])       
        self.add_user_message(f"""### Course:
- **Subject**: {course.course_subject}
- **Description**: {course.description}

#### Key Outcomes:
{key_outcomes_str}

### Module:
- **Name**: {module_dto.title}
- **Focus Area**: {module.focus_area}
- **Objective**: {module_dto.description}

I will provide you with each lesson in the module. You will focus on one lesson at a time.
""")
        
        for lesson in module.lessons:
            lesson_dto = LessonDto.model_construct(
                title=lesson.title,
                description=lesson.description,
                sections=[]
            )
            
            self.add_user_message(f"""### Lesson:
- **Name**: {lesson_dto.title}
- **Focus Area**: {lesson_dto.description}

I will provide you with the title for each section in this lesson. You will generate comprehensive learning content for each of these, one at a time. Do not include any other commentary in your output.
""")
            
            for section in lesson.sections:
                self.add_user_message(f"""{section.title}
{section.description}                                   
""")
                messages = model.get_responses(self)
                
                content = messages[-1].message
                
                logging.info(content)
                
                lesson_dto.sections.append(
                    SectionDto.model_construct(
                        title=section.title,
                        description=section.description,
                        content=content
                    )
                )

            module_dto.lessons.append(lesson_dto)
                
        return module_dto