from typing import Optional

from pydantic_core import ValidationError
from ai.common import BaseTool
from domain.dto.profile import UserProfileDisciplineDto, UserSkillDto
from domain.dto.profile.hobby import HobbyProjectDto, UserProfileHobbyDto
from domain.dto.profile.student import UserProfileSchoolDto, UserProfileStudentDto
from domain.dto.profile.professional import UserProfileProfessionalDto, UserProfileEmploymentDto
from domain.dto.user import UserProfileDto
from .models import ProfileScan, Discipline
from domain.enums.user_enums import UserDiscipline, UserLearningCapacity, UserSkillType

class ProvideProfileTool(BaseTool):
    def __init__(self):
        super().__init__("provide_profile", "Provides the user with the processed profile information")
        
        profile_schema = ProfileScan.model_json_schema()
        
        self.use_schema(profile_schema)
        
    def process(self, arguments: ProfileScan) -> str:
        learning_capacities = []
        student: Optional[UserProfileStudentDto] = None
        hobby: Optional[UserProfileHobbyDto] = None
        professional: Optional[UserProfileProfessionalDto] = None

        print(arguments)
        
        try:
            scan = ProfileScan(**arguments)
            
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
            
            self.result = UserProfileDto.model_construct(
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
        except ValidationError as e:
            errors_str = "\n".join([f"{error['loc'][0]}: {error['msg']}" for error in e.errors()])
            print(errors_str)
            return f"Error: {errors_str}"
        except AttributeError as e:
            print(e)
            return f"Error: {e}"
        except Exception as e:
            print(e)
            return f"Error: {e}"
        
        return "Success"
    
def get_discipline_translation(discipline: Discipline) -> UserDiscipline:
    return {
        Discipline.FRONTEND: UserDiscipline.FRONTEND,
        Discipline.BACKEND: UserDiscipline.BACKEND,
        Discipline.DATABASE: UserDiscipline.DATABASE,
        Discipline.DEVOPS: UserDiscipline.DEVOPS
    }[discipline]