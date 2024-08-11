from typing import List
import uuid

from sqlmodel import Session, select
from domain.schema.profile.professional import UserProfileEmployment, UserProfileEmploymentSkill, UserProfileProfessional
from domain.dto.profile.professional import UserProfileProfessionalDto
from domain.dto.profile import UserSkillDto, UserProfileDisciplineDto
from domain.schema.user import UserProfile, UserProfileSkill, UserProfileDiscipline
from domain.schema.profile.hobby import (
    UserProfileHobby, 
    UserProfileHobbyProject, 
    UserProfileHobbyReason, 
    UserProfileHobbySkill,
)
from domain.schema.profile.student import (
    UserProfileSchool,
    UserProfileStudent,
    UserProfileSchoolSkill
)
from domain.dto.profile.hobby import UserProfileHobbyDto
from domain.dto.profile.student import UserProfileStudentDto

def map_hobby_data(session: Session, user_profile: UserProfile, dto: UserProfileHobbyDto):
    """
    Rebuilds the hobby data for a user profile

    Args:
        session (Session): The active database session
        user_profile (UserProfile): The user profile to update
        dto (UserProfileHobbyDto): The new hobby data
    """
    skills = user_profile.skills
    hobby = user_profile.hobby
    
    if not hobby:
        # Create it and get the result back with id
        hobby = UserProfileHobby(user_profile_id=user_profile.id)
        session.add(hobby)
        session.commit()
    else:
        # Clear out existing data
        for reason in hobby.reasons:
            session.delete(reason)
        
        for project in hobby.projects:
            session.delete(project)
            
        for skill in hobby.skills:
            session.delete(skill)
            
        session.commit()
    
    # Add the most current set of skills
    for skill in dto.skills:
        matched = next((x for x in skills if x.skill == skill), None)
        
        if matched:
            session.add(
                UserProfileHobbySkill(
                    skill_id=matched.id, 
                    user_profile_hobby_id=hobby.id
                )
            )
        
    # Add the most current set of reasons and projects
    for reason in dto.reasons:
        session.add(
            UserProfileHobbyReason(
                reason=reason.value, 
                user_profile_hobby_id=hobby.id
            )
        )
        
    for project in dto.projects:
        session.add(
            UserProfileHobbyProject(
                project_name=project.project_name, 
                description=project.description, 
                purpose=project.purpose, 
                user_profile_hobby_id=hobby.id
            )
        )
        
    # Save this portion of the data
    session.commit()
    
def map_student_data(session: Session, user_profile: UserProfile, student_dto: UserProfileStudentDto):
    """
    Rebuilds the student data for a user profile

    Args:
        session (Session): The active database session
        user_profile (UserProfile): The user profile to update
        student (UserProfileStudentDto): The new student data
    """
    student = user_profile.student
    
    if not student:
        # Create it and get the result back with id
        student = UserProfileStudent(user_profile_id=user_profile.id)
        session.add(student)
        session.commit()
    
    # Remove the current set of schools
    for school in student.schools:
        if school.skills:
            for skill in school.skills:
                session.delete(skill)
        
        session.delete(school)
    
    # Add the new list
    for school in student_dto.schools:
        new_school = UserProfileSchool(
            user_profile_student_id=user_profile.student.id, 
            school_name=school.school_name,
            focus=school.focus,
            start_date=school.start_date,
            end_date=school.end_date,
            did_finish=school.did_finish,
            is_current=school.is_current
        )
        session.add(new_school)

        if school.skills:
            for skill in school.skills:
                matched = next((x for x in user_profile.skills if x.skill == skill), None)
                
                if matched:
                    session.add(
                        UserProfileSchoolSkill(
                            skill_id=matched.id, 
                            user_profile_school_id=new_school.id
                        )
                    )
        
    # Save the new schools
    session.commit()
    
def map_professional_data(session: Session, user_profile: UserProfile, professional_dto: UserProfileProfessionalDto):
    """
    Rebuilds the professional data for a user profile

    Args:
        session (Session): The active database session
        user_profile (UserProfile): The user profile to update
        professional_dto (UserProfileProfessionalDto): The new professional data
    """
    professional = user_profile.professional
    
    if not professional:
        # Create it and get the result back with id
        professional = UserProfileProfessional(user_profile_id=user_profile.id)
        session.add(professional)
        session.commit()
    else:
        # Clear out existing data
        for employment in professional.employers:
            if employment.skills:
                for skill in employment.skills:
                    session.delete(skill)
            
            session.delete(employment)
        
        session.commit()
    
    # Add the new list
    for job in professional_dto.employers:
        new_employment = UserProfileEmployment(
            company_name=job.company_name, 
            position=job.position, 
            description=job.description, 
            start_date=job.start_date,
            end_date=job.end_date,
            is_current=job.is_current, 
            user_profile_professional_id=professional.id
        )
        session.add(new_employment)
        
        if job.skills:
            for skill in job.skills:
                matched = next((x for x in user_profile.skills if x.skill == skill), None)
                
                if matched:
                    session.add(
                        UserProfileEmploymentSkill(
                            skill_id=matched.id, 
                            user_profile_employment_id=new_employment.id
                        )
                    )
        
    # Save the new employers
    session.commit()
    
def delete_student_data(session: Session, record: UserProfileStudent):
    """
    Deletes all student data for a user profile

    Args:
        session (Session): The active database session
        record (UserProfileStudent): The student record to delete
    """
    for school in record.schools:
        session.delete(school)
    
    session.delete(record)
    session.commit()
    
def delete_professional_data(session: Session, record: UserProfileProfessional):
    """
    Deletes all professional data for a user profile

    Args:
        session (Session): The active database session
        record (UserProfileProfessional): The professional record to delete
    """
    for employment in record.employers:
        for skill in employment.skills:
            session.delete(skill)
        
        session.delete(employment)
    
    session.delete(record)
    session.commit()
    
def delete_hobby_data(session: Session, record: UserProfileHobby):
    """
    Deletes all hobby data for a user profile

    Args:
        session (Session): The active database session
        record (UserProfileHobby): The hobby record to delete
    """
    for skill in record.skills:
        session.delete(skill)
    
    for reason in record.reasons:
        session.delete(reason)
        
    for project in record.projects:
        session.delete(project)
    
    session.delete(record)
    session.commit()
    
def map_skill_data(session: Session, user_profile: UserProfile, skills: List[UserSkillDto]):
    """
    Rebuilds the skill data for a user profile

    Args:
        session (Session): The active database session
        user_profile (UserProfile): The user profile to update
        skills (List[UserSkillDto]): The new skill data
    """
    # Create lists for the current sections that reference the current skills on the profile
    hobby_skills: List[UserProfileHobbySkill] = []
    school_skills: List[UserProfileSchoolSkill] = []
    employment_skills: List[UserProfileEmploymentSkill] = []
    
    # Create a list that will hold the new skill records
    updated_skills: List[UserProfileSkill] = []
    
    # If the profile has hobby data, we'll want to retrieve the skills which reference by ID
    if user_profile.hobby:
        hobby_skills_query = (
            select(UserProfileHobbySkill)
            .where(UserProfileHobbySkill.user_profile_hobby_id == user_profile.hobby.id)
        )
        
        hobby_skills = session.exec(hobby_skills_query).all()
        
    if user_profile.student:
        for school in user_profile.student.schools:
            school_skills_query = (
                select(UserProfileSchoolSkill)
                .where(UserProfileSchoolSkill.user_profile_school_id == school.id)
            )
            
            school_skills.extend(session.exec(school_skills_query).all())
    
    if user_profile.professional:
        for employment in user_profile.professional.employers:
            employment_skills_query = (
                select(UserProfileEmploymentSkill)
                .where(UserProfileEmploymentSkill.user_profile_employment_id == employment.id)
            )
            
            employment_skills.extend(session.exec(employment_skills_query).all())
    
    # Remove the current set of hobby skills
    if user_profile.hobby:
        for hobby_skill in user_profile.hobby.skills:
            session.delete(hobby_skill)
            
    # Remove the current set of school skills
    if user_profile.student:
        for school_skill in school_skills:
            session.delete(school_skill)
            
    # Remove the current set of employment skills
    if user_profile.professional:
        for employment_skill in employment_skills:
            session.delete(employment_skill)
        
    # Remove the current set of profile skills
    for skill in user_profile.skills:
        session.delete(skill)
    
    # Add the new list
    for skill in skills:
        updated_skill = UserProfileSkill(
            user_profile_id=user_profile.id, 
            skill_type=skill.skill_type.value, 
            skill=skill.skill, 
            proficiency=skill.proficiency, 
            notes=skill.notes
        )
        session.add(updated_skill)
        
    # Save the new skills
    session.commit()
    
    # If there were hobby skills, we'll rebuild that relationship now
    if hobby_skills:
        for skill in hobby_skills:
            matched = next((x for x in updated_skills if x.skill == skill.skill_id), None)
            
            if matched:
                session.add(
                    UserProfileHobbySkill(
                        skill_id=matched.id, 
                        user_profile_hobby_id=user_profile.hobby.id
                    )
                )
                
    if school_skills:
        for skill in school_skills:
            matched = next((x for x in updated_skills if x.skill == skill.skill_id), None)
            
            if matched:
                session.add(
                    UserProfileSchoolSkill(
                        skill_id=matched.id, 
                        user_profile_school_id=skill.user_profile_school_id
                    )
                )
                
    if employment_skills:
        for skill in employment_skills:
            matched = next((x for x in updated_skills if x.skill == skill.skill_id), None)
            
            if matched:
                session.add(
                    UserProfileEmploymentSkill(
                        skill_id=matched.id, 
                        user_profile_employment_id=skill.user_profile_employment_id
                    )
                )
        
    session.commit()
        
def map_discipline_data(session: Session, user_profile: UserProfile, disciplines: List[UserProfileDisciplineDto]):
    """
    Rebuilds the discipline data for a user profile

    Args:
        session (Session): The active database session
        user_profile (UserProfile): The user profile to update
        disciplines (List[UserProfileDisciplineDto]): The new discipline data
    """
    # Remove the current set of disciplines
    for discipline in user_profile.disciplines:
        session.delete(discipline)
    
    # Add the new list
    for discipline in disciplines:
        new_discipline = UserProfileDiscipline(
            user_profile_id=user_profile.id, 
            discipline_type=discipline.discipline_type.value, 
            proficiency=discipline.proficiency,
            notes=discipline.notes
        )
        session.add(new_discipline)
        
    # Save the new disciplines
    session.commit()