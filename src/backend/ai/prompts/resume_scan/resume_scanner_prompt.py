from typing import List, Optional
from ai.prompts import BasePrompt
from domain.dto.profile import UserProfileDisciplineDto, UserProfileDto, UserSkillDto
from domain.dto.profile.hobby import HobbyProjectDto, UserProfileHobbyDto
from domain.dto.profile.professional import UserProfileEmploymentDto, UserProfileProfessionalDto
from domain.dto.profile.student import UserProfileSchoolDto, UserProfileStudentDto
from domain.enums.user_enums import UserDiscipline, UserLearningCapacity, UserSkillType
from .models import Discipline, ProfileScan
from .provide_profile_tool import ProvideProfileTool

class ResumeScannerPrompt(BasePrompt):
    def setup(self) -> None:
        self.set_system_prompt("""
You will look through images of a resume and extract information from it.
The information you will look for is denoted in the schema of the provide_profile tool.
You will use the provide_profile tool to send your results back to the user. You will not be able to ask questions.

When filling out the bio and descriptions, you will make it less formal (as in a resume format) and more casual (as in a bio format, first person).
You will keep programming languages and libraries/frameworks granular, only one item each.
You will keep programming languages only to their names and not include frameworks, libraries, or other suffixes.
You will not include development tools in the programming languages or libraries/frameworks lists. These will be ignored.

The following criteria represent when to include a learning capacity:
- Hobby: Any indication of a personal or side project or stated interested in development outside of work or school somewhere in the resume.
- Student: Any education or certifications from an institution in programming or computer science mentioned.
- Professional: Any indication of a job or work experience related to software development or programming.

When filling out start or end dates, if the day is not provided, you will use the first day of the month or end of the month respectively.
Ex: If the resume says "May 2020", you will use "2020-05-01" or "2020-05-31" respectively.
""")
        
        self.use_tool(ProvideProfileTool, force=True)
        
    def get_profile_data(self, resume_images: List[bytes]) -> ProfileScan:
        from ...models.gpt_4o import GPT4o
        
        self.add_user_message("Process this resume", resume_images)
        
        model = GPT4o()
        model.get_responses(self)
        call = self.get_tool_call(ProvideProfileTool)
        
        if not call.result:
            raise Exception("No profile data provided")
        
        learning_capacities = []
        student: Optional[UserProfileStudentDto] = None
        hobby: Optional[UserProfileHobbyDto] = None
        professional: Optional[UserProfileProfessionalDto] = None

        scan = call.result
        
        if scan.schools:
            learning_capacities.append(UserLearningCapacity.STUDENT)
            
            student = UserProfileStudentDto.model_construct(
                schools=[
                    UserProfileSchoolDto.model_construct(
                        school_name=school.name,
                        focus=school.focus,
                        start_date=school.start_month,
                        end_date=school.end_month,
                        is_current=school.is_current,
                        did_finish=school.did_finish
                    )    
                    for school in scan.schools
                ]
            )
            
        if scan.hobby_projects:
            learning_capacities.append(UserLearningCapacity.HOBBY)
            
            hobby = UserProfileHobbyDto.model_construct(
                projects=[
                    HobbyProjectDto.model_construct(
                        project_name=project.project_name,
                        description=project.description,
                        purpose=project.purpose
                    )
                    for project in scan.hobby_projects
                ]
            )
            
        if scan.employers:
            learning_capacities.append(UserLearningCapacity.PROFESSIONAL)
            
            professional = UserProfileProfessionalDto.model_construct(
                employers=[
                    UserProfileEmploymentDto.model_construct(
                        company_name=employer.company_name,
                        position=employer.position,
                        start_date=employer.start_month,
                        end_date=employer.end_month,
                        is_current=employer.is_current,
                        description=employer.description
                    )
                    for employer in scan.employers
                ]
            )
        
        user_profile_dto = UserProfileDto.model_construct(
            first_name=scan.first_name,
            last_name=scan.last_name,
            bio=scan.bio,
            github_username=scan.github_username,
            learning_capacities=learning_capacities,
            hobby=hobby,
            student=student,
            professional=professional,
            disciplines=[
                UserProfileDisciplineDto.model_construct(
                    discipline_type=get_discipline_translation(discipline),
                    proficiency=None
                )
                for discipline in scan.disciplines
            ],
            skills=[
                *[
                    UserSkillDto.model_construct(
                        skill_type=UserSkillType.PROGRAMMING_LANGUAGE,
                        skill=skill,
                        proficiency=None
                    )
                    for skill in scan.programming_languages
                ],
                *[
                    UserSkillDto.model_construct(
                        skill_type=UserSkillType.LIBRARY,
                        skill=skill,
                        proficiency=None
                    )
                    for skill in scan.frameworks
                ],
                *[
                    UserSkillDto.model_construct(
                        skill_type=UserSkillType.LIBRARY,
                        skill=skill,
                        proficiency=None
                    )
                    for skill in scan.libraries
                ]
            ]
        )
        
        return user_profile_dto
    
def get_discipline_translation(discipline: Discipline) -> UserDiscipline:
    return {
        Discipline.FRONTEND: UserDiscipline.FRONTEND,
        Discipline.BACKEND: UserDiscipline.BACKEND,
        Discipline.DATABASE: UserDiscipline.DATABASE,
        Discipline.DEVOPS: UserDiscipline.DEVOPS
    }[discipline]