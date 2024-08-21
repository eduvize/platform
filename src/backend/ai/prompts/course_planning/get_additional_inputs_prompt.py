from ai.prompts.base_prompt import BasePrompt
from .provide_additional_inputs_tool import ProvideAdditionalInputsTool
from domain.dto.courses import CoursePlanDto
from domain.enums.course_enums import CourseMotivation, CurrentSubjectExperience, CourseMaterial
from domain.dto.courses import AdditionalInputs

class GetAdditionalInputsPrompt(BasePrompt):
    def setup(self) -> None:
        self.use_tool(ProvideAdditionalInputsTool, force=True)
    
    def get_inputs(
        self,
        plan: CoursePlanDto,
        profile_text: str
    ) -> AdditionalInputs:
        from ai.models.gpt_4o import GPT4o
        
        self.set_system_prompt(f"""
Review a student application request to enroll an online education platform for Software Engineering.
You are expected to provide follow-up questions to the student to get a comprehensive understanding of their needs and expectations so course material can be created accordingly.
The answers to these questions will be handed off to a course planner who will create a course outline based on the student's responses.

An ideal set of questions will provide additional insight into what the student is looking to achieve with this course, information around their motivations, and to drill into specifics about their understanding of the subject at hand.
If the student provided any additional information about their motivations or experience, it is a good idea to orient a few questions around those details.
You will not ask questions that can already be derived from the student's profile (like proficiency in a language or library), what their preferred learning style or time commitment is, what learning resources they use, or about subjects not directly related to the course subject.
It's important that you do not go off course with your questions: do not attempt to ask the student if they would like to learn more about a related subject.

Select and Multiselect:
- Do not add parantheses to selection options.
- If you specify 'Other' as an option, you must provide a follow-up question to gather more information.

If any of your questions are rule based, you can specify them in the tool's schema.

You will make these questions as easy to fill out as possible, leveraging selections and multiple-choice questions where possible.
""")
        
        self.add_agent_message(f"""
I've pulled the user's profile information. Here is what I have:
{profile_text}                            
""")
        
        plan_description = _get_course_plan_description(plan)
        
        self.add_user_message(plan_description)
        self.add_agent_message("Excellent, I will analyze what you have provided and determine if I have any follow-up questions in order to make this course work for you.")
        
        model = GPT4o()
        model.get_responses(self)
        
        calls = self.get_tool_calls(ProvideAdditionalInputsTool)
        
        if not calls:
            return []
        
        return calls[-1].result
        
def _get_course_plan_description(plan: CoursePlanDto) -> str:
    motivation_strs = []
    current_experience_str = ""
    
    for x in plan.motivations:
        if x == CourseMotivation.CAREER:
            motivation_strs.append("I want to advance my career")
        elif x == CourseMotivation.CERTIFICATION:
            motivation_strs.append("I'm going for a certification")
        elif x == CourseMotivation.PROJECT:
            motivation_strs.append("I'm working on a project that requires this knowledge")
        elif x == CourseMotivation.SKILL_ENHANCEMENT:
            motivation_strs.append("I'm looking to enhance my existing skillset")
        elif x == CourseMotivation.OTHER:
            if plan.other_motivation_details:
                motivation_strs.append(plan.other_motivation_details)
            else:
                motivation_strs.append("I have other reasons for wanting to learn this subject")
                
    if plan.experience == CurrentSubjectExperience.NEW:
        current_experience_str = "I have no experience with this subject."
    elif plan.experience == CurrentSubjectExperience.REFRESH:
        current_experience_str = "I have some experience with this subject, but I need a refresher."
    elif plan.experience == CurrentSubjectExperience.KNOWLEDGEABLE:
        current_experience_str = "I feel like I already have a lot of knowledge about this subject."
    elif plan.experience == CurrentSubjectExperience.EXISTING:
        current_experience_str = "I have existing knowledge about this subject, but I want to learn more."
        
    if plan.experience_details:
        current_experience_str += f" {plan.experience_details}"
    
    motivations_str = "- " + "\n- ".join(motivation_strs)

    return f"""
I would like to learn {plan.subject}.

My motivation behind this desire:
{motivations_str}

{current_experience_str}
"""