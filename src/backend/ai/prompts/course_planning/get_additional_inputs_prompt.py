from ai.prompts.base_prompt import BasePrompt
from .provide_additional_inputs_tool import ProvideAdditionalInputsTool
from domain.dto.courses import CoursePlanDto
from domain.enums.course_enums import CourseMotivation, CurrentSubjectExperience, CourseMaterial
from domain.dto.courses import AdditionalInputs

class GetAdditionalInputsPrompt(BasePrompt):    
    def setup(self) -> None:
        self.use_tool(ProvideAdditionalInputsTool, force=True)
        
        self.set_system_prompt(f"""
You are an AI assistant tasked with reviewing student applications for an online education platform focused on Software Engineering. Your goal is to generate follow-up questions that will help gather specific details about the student's current knowledge gaps and additional relevant information, aiding in the creation of a tailored course syllabus.

**Rules for generating questions:**
1. **Avoid Redundancy**: Ensure that none of your questions repeat those already presented in the student's initial request form.
2. **Limit to 8 Questions**: Generate up to 8 follow-up questions, but only if each question provides significant value.
3. **Use Appropriate Input Types**: Utilize "text," "select," and "multiselect" input types to make questions easy to answer.
4. **Focus on Knowledge Gaps and Context**: Target areas where the student feels they lack understanding or experience, gather relevant information about their background, and specify tools, frameworks, or methodologies related to the subject they want to learn.
5. **No Questions on Learning Pace or Time Commitment**: Do not ask about the student's preferred learning pace or time availability, as the course is designed to be taken at their leisure.
6. **Dependent Fields**: If a question depends on a previous answer, ensure it is logically connected to the student's response.

**Guidelines:**
- **Relevance**: Ensure each question directly relates to the student's desired learning subject and their existing knowledge.
- **Clarity**: Avoid overloading the student with too many questions. Aim for a balance between gathering necessary details and keeping the form concise.
- **Follow-Up**: If "Other" is selected, always include a follow-up question to clarify the student's needs.
- **Rule-Based Questions**: If any of your questions need to follow specific rules, define them clearly in the tool’s schema.
""")
    
    def get_inputs(
        self,
        plan: CoursePlanDto,
        profile_text: str
    ) -> AdditionalInputs:
        from ai.models.gpt_4o import GPT4o
        
        plan_description = get_course_plan_description(plan)
        
        self.add_user_message(f"""### User Profile:
{profile_text}

### Initial Request Form:
{plan_description}

Using the user profile information and the initial request form data, generate follow-up questions to gather more specific details. Ensure no repetition of previous questions, limit to 8 questions only if necessary, and utilize text, select, and multiselect inputs where appropriate.
""")
                    
        model = GPT4o()
        model.get_responses(self)
        
        followup_call = self.get_tool_call(ProvideAdditionalInputsTool)
        
        if not followup_call.result:
            return AdditionalInputs.model_construct(
                inputs=[]
            )
        
        return followup_call.result
    
def get_course_plan_description(plan: CoursePlanDto) -> str:
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

    challenges_str = f"""
Challenges I've faced with this in the past:
{plan.challanges}
""" if plan.challanges else ""

    return f"""
I would like to learn {plan.subject}.

Desired outcome: {plan.desired_outcome}
{challenges_str}
My motivation behind this desire:
{motivations_str}

{current_experience_str}
"""