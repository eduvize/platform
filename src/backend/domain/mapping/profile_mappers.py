from typing import List
import uuid

from sqlmodel import Session, select, update
from domain.dto.profile import UserSkillDto, UserProfileDisciplineDto
from domain.schema.user import UserProfile, UserProfileSkill, UserProfileDiscipline
from domain.schema.profile.hobby import (
    UserProfileHobby, 
    UserProfileHobbyProject, 
    UserProfileHobbyReason, 
    UserProfileHobbySkill,
)
from domain.dto.profile.hobby import UserProfileHobbyDto
from sqlalchemy.orm import joinedload

def map_hobby_data(session: Session, user_profile_id: uuid.UUID, dto: UserProfileHobbyDto):
    """
    Rebuilds the hobby data for a user profile

    Args:
        session (Session): The active database session
        user_profile_id (uuid.UUID): The ID of the user profile to update
        dto (UserProfileHobbyDto): The new hobby data
    """
    # Retrieve the existing profile skills and hobby data we'll be updating
    skills_query = (
        select(UserProfileSkill)
        .where(UserProfileSkill.user_profile_id == user_profile_id)
    )
    hobby_query = (
        select(UserProfileHobby)
        .where(UserProfileHobby.user_profile_id == user_profile_id)
        .options(
            joinedload(UserProfileHobby.reasons), 
            joinedload(UserProfileHobby.projects)
        )
    )
    
    skills = session.exec(skills_query).all()
    hobby = session.exec(hobby_query).first()
    
    if not hobby:
        # Create it and get the result back with id
        hobby = UserProfileHobby(user_profile_id=user_profile_id)
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
    
    # Create a list that will hold the new skill records
    updated_skills: List[UserProfileSkill] = []
    
    # If the profile has hobby data, we'll want to retrieve the skills which reference by ID
    if user_profile.hobby:
        hobby_skills_query = (
            select(UserProfileHobbySkill)
            .where(UserProfileHobbySkill.user_profile_hobby_id == user_profile.hobby.id)
        )
        
        hobby_skills = session.exec(hobby_skills_query).all()
    
    # Remove the current set of hobby skills
    for hobby_skill in user_profile.hobby.skills:
        session.delete(hobby_skill)
    
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
            proficiency=discipline.proficiency
        )
        session.add(new_discipline)
        
    # Save the new disciplines
    session.commit()