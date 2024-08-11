from datetime import date
import uuid
from domain.dto.profile.professional import UserProfileProfessionalDto
from domain.dto.profile.student import UserProfileStudentDto
from domain.dto.profile.hobby import HobbyReason, UserProfileHobbyDto
from domain.enums.user_enums import UserLearningCapacity, UserSkillType, UserDiscipline
from domain.dto.profile import UserProfileDto, UserSkillDto

PROFICIENCY_MAPPING = {
    1: "a beginner",
    2: "intermediate",
    3: "advanced",
    4: "an expert"
}

DISCIPLINE_MAPPING = {
    UserDiscipline.FRONTEND: "frontend development",
    UserDiscipline.BACKEND: "backend development",
    UserDiscipline.DATABASE: "database syntax and management",
    UserDiscipline.DEVOPS: "devops practices"
}

HOBBY_REASON_MAPPING = {
    HobbyReason.CHALLENGING: "I like to challenge myself by building hobby projects",
    HobbyReason.CREATIVE_OUTLET: "It's a creative outlet for me",
    HobbyReason.DIVERSIFY_SKILLS: "I use hobby projects to diversify my skills",
    HobbyReason.ENTERTAINING: "I find working on hobby projects entertaining",
    HobbyReason.LEARN_NEW_TECHNOLOGY: "I use hobby projects to learn new technologies",
    HobbyReason.MAKE_MONEY: "I try to make money off of my hobby projects"
}

SKILL_TYPE_MAPPING = {
    UserSkillType.PROGRAMMING_LANGUAGE: "language",
    UserSkillType.LIBRARY: "library"
}

def get_user_profile_text(user_profile: UserProfileDto):
    """
    Returns a string representation of a user profile

    Args:
        user_profile (UserProfileDto): The user profile to generate the string for
        
    Returns:
        str: The string representation of the user profile
    """
    print(user_profile)
    stack_parts = []
    
    for discipline in user_profile.disciplines:
        start_str = f"I'm {PROFICIENCY_MAPPING.get(discipline.proficiency, 'familiar')} with {DISCIPLINE_MAPPING.get(discipline.discipline_type, 'Unknown')}"
        
        if discipline.notes:
            stack_parts.append(f"{start_str}. {discipline.notes}")
        else:
            stack_parts.append(start_str)
    
    stack_str = "\n- ".join(stack_parts)
    
    if user_profile.professional:
        total_professional_yoe = sum([
            ((employer.end_date if not employer.is_current else date.today()) - employer.start_date).days / 365
            for employer in user_profile.professional.employers
            if employer.start_date and (employer.end_date or employer.is_current)
        ])
    else:
        total_professional_yoe = 0
        
    yoe_str = f"I have {int(total_professional_yoe)} years of professional experience" if total_professional_yoe > 0 else "I do not have any professional experience in the field"
    
    basic_info = f"""
# {user_profile.first_name} {user_profile.last_name}
{user_profile.bio}

{yoe_str}
## Stack
- {stack_str}
"""

    hobby_text = get_hobby_text(user_profile.hobby) if user_profile.hobby else ""
    education_text = get_education_text(user_profile.student) if user_profile.student else ""
    professional_text = get_professional_text(user_profile.professional) if user_profile.professional else ""
    skills_text = get_skills_text(user_profile)
    
    return f"""
{basic_info}
{skills_text}
{hobby_text}
{education_text}
{professional_text}"""

def get_hobby_text(hobby: UserProfileHobbyDto):
    reasons_str = "\n- ".join([HOBBY_REASON_MAPPING.get(reason, 'Unknown') for reason in hobby.reasons])
    projects_str = "\n".join([
        f"""
#### {project.project_name}
{project.purpose if project.purpose else ""}
##### Description
{project.description}"""
        for project in hobby.projects
    ])
    
    return f"""
## Programming for fun
### Motivations
- {reasons_str}
### Projects
{projects_str}""";
    
def get_education_text(education: UserProfileStudentDto):
    attendance_str = "I am currently attending" if education.is_current else f"I attendeded from {education.start_month} to {education.end_month}"
    
    schools_str = "\n".join([
        f"""
### {school.school_name}
{attendance_str}
Focus: {school.focus}"""
        for school in education.schools
    ])
    
    return f"""
## Education
{schools_str}""";
    
def get_professional_text(professional: UserProfileProfessionalDto):
    employers_str = "\n".join([
        f"""
### {employer.company_name}
My role was **{employer.position}**
{(f"I worked here from {employer.start_date} to {employer.end_date}" if not employer.is_current else "I currently work here")}
*{employer.description}*"""
        for employer in professional.employers
    ])
    
    return f"""
## Professional Experience
{employers_str}""";
    
def get_skills_text(profile: UserProfileDto):
    skills_parts = []
        
    for skill in profile.skills:
        id_uuid = uuid.UUID(skill.id)
        
        proficiency = f"I consider myself as {PROFICIENCY_MAPPING.get(skill.proficiency, 'somewhat familiar')} with this {SKILL_TYPE_MAPPING.get(skill.skill_type, 'skill')}"
        usages = []
        
        if profile.hobby and id_uuid in profile.hobby.skills:
            usages.append("in hobby projects")
            
        if profile.student and any([id_uuid in school.skills for school in profile.student.schools]):
            schools = [school.school_name for school in profile.student.schools if id_uuid in school.skills]
            usages.append(f"during my studies at {' and '.join(schools)}")
            
        if profile.professional and any([id_uuid in employer.skills for employer in profile.professional.employers]):
            employers = [employer.company_name for employer in profile.professional.employers if id_uuid in employer.skills]
            usages.append(f"during my role at {' and '.join(employers)}")

        if not usages:
            usage_str = "However, I have not used this skill in any professional, hobby, or educational setting"
        else:
            usage_str = ", ".join(usages)
            usage_str = f"I have used this skill {usage_str}"
            
        notes_str = f"\n{skill.notes}" if skill.notes else ""
        
        skills_parts.append(f"""
#### {skill.skill}
{proficiency}
{usage_str}{notes_str}""")
        
            
    skills_str = "\n".join(skills_parts)
    
    return f"""
### My Skills
{skills_str}""";