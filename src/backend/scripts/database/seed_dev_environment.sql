-- Create table for Users
CREATE TABLE IF NOT EXISTS users
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    password_hash TEXT,
    pending_verification BOOLEAN NOT NULL DEFAULT FALSE,
    verification_code TEXT,
    verification_sent_at_utc TIMESTAMP WITHOUT TIME ZONE,
    created_at_utc TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
    last_login_at_utc TIMESTAMP WITHOUT TIME ZONE,
    CONSTRAINT users_pkey PRIMARY KEY (id),
    CONSTRAINT users_email_key UNIQUE (email),
    CONSTRAINT users_username_key UNIQUE (username)
);

-- Create table for Facebook auth
CREATE TABLE IF NOT EXISTS users_external_auth (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    provider_id TEXT NOT NULL,
    external_id TEXT NOT NULL UNIQUE,
    created_at_utc TIMESTAMP NOT NULL DEFAULT now()
);

-- Create table for Google auth
CREATE TABLE IF NOT EXISTS users_google_auth (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    google_id TEXT NOT NULL UNIQUE,
    created_at_utc TIMESTAMP NOT NULL DEFAULT now()
);

-- Create table for User Profiles
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    first_name TEXT,
    last_name TEXT,
    birthdate DATE,
    bio TEXT,
    github_username TEXT,
    avatar_url TEXT,
    last_updated_at_utc TIMESTAMP NOT NULL DEFAULT now()
);

-- Create table for skills
CREATE TABLE IF NOT EXISTS user_profiles_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_profile_id UUID NOT NULL REFERENCES user_profiles(id),
    skill_type INT NOT NULL,
    skill TEXT NOT NULL,
    proficiency INT,
    notes TEXT
);

-- Create table for the hobby portion of the user profile
CREATE TABLE IF NOT EXISTS user_profiles_hobby (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_profile_id UUID NOT NULL REFERENCES user_profiles(id)
);

-- Create table for hobby skills
CREATE TABLE IF NOT EXISTS user_profiles_hobby_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_profile_hobby_id UUID NOT NULL REFERENCES user_profiles_hobby(id),
    skill_id UUID NOT NULL REFERENCES user_profiles_skills(id)
);

-- Create table for hobby reasons
CREATE TABLE IF NOT EXISTS user_profiles_hobby_reasons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_profile_hobby_id UUID NOT NULL REFERENCES user_profiles_hobby(id),
    reason TEXT NOT NULL
);

-- Create table for hobby projects
CREATE TABLE IF NOT EXISTS user_profiles_hobby_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_profile_hobby_id UUID NOT NULL REFERENCES user_profiles_hobby(id),
    project_name TEXT NOT NULL,
    description TEXT NOT NULL,
    purpose TEXT
);

-- Create table for the student portion of the user profile
CREATE TABLE IF NOT EXISTS user_profiles_student (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_profile_id UUID NOT NULL REFERENCES user_profiles(id)
);

-- Create table for schools
CREATE TABLE IF NOT EXISTS user_profiles_schools (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_profile_student_id UUID NOT NULL REFERENCES user_profiles_student(id),
    school_name TEXT NOT NULL,
    start_date DATE,
    end_date DATE,
    focus TEXT,
    did_finish BOOLEAN NOT NULL,
    is_current BOOLEAN NOT NULL
);

-- Create table for school skills
CREATE TABLE IF NOT EXISTS user_profiles_schools_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_profile_school_id UUID NOT NULL REFERENCES user_profiles_schools(id),
    skill_id UUID NOT NULL REFERENCES user_profiles_skills(id)
);

-- Create table for education skills
CREATE TABLE IF NOT EXISTS user_profiles_student_education_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_profile_student_id UUID NOT NULL REFERENCES user_profiles_student(id),
    skill_id UUID NOT NULL REFERENCES user_profiles_skills(id)
);

-- Create table for the professional portion of the user profile
CREATE TABLE IF NOT EXISTS user_profiles_professional (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_profile_id UUID NOT NULL REFERENCES user_profiles(id)
);

-- Create table for employment
CREATE TABLE IF NOT EXISTS user_profiles_employment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_profile_professional_id UUID NOT NULL REFERENCES user_profiles_professional(id),
    company_name TEXT NOT NULL,
    position TEXT NOT NULL,
    description TEXT NOT NULL,
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN NOT NULL
);

-- Create table for skills used at an employer
CREATE TABLE IF NOT EXISTS user_profiles_employment_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_profile_employment_id UUID NOT NULL REFERENCES user_profiles_employment(id),
    skill_id UUID NOT NULL REFERENCES user_profiles_skills(id)
);

-- Create table for mapping disciplines and proficiency levels to user profiles
CREATE TABLE IF NOT EXISTS user_profiles_disciplines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_profile_id UUID NOT NULL REFERENCES user_profiles(id),
    discipline_type INT NOT NULL,
    proficiency INT,
    notes TEXT
);

-- Create table for instructor
CREATE TABLE IF NOT EXISTS user_instructors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    name TEXT NOT NULL,
    avatar_url TEXT NOT NULL,
    is_approved BOOLEAN NOT NULL DEFAULT FALSE,
    created_at_utc TIMESTAMP NOT NULL DEFAULT now()
);

-- Create table for Course
CREATE TABLE IF NOT EXISTS courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    cover_image_url TEXT NOT NULL,
    is_generating BOOLEAN NOT NULL DEFAULT TRUE,
    generation_progress INT NOT NULL DEFAULT 0,
    created_at_utc TIMESTAMP NOT NULL DEFAULT now()
);

-- Create table for Modules
CREATE TABLE IF NOT EXISTS course_modules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL REFERENCES courses(id),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    order INT NOT NULL
);

-- Create table for Lessons
CREATE TABLE IF NOT EXISTS course_lessons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module_id UUID NOT NULL REFERENCES course_modules(id),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    order INT NOT NULL
);

-- Create table for Lesson Sections
CREATE TABLE IF NOT EXISTS course_lesson_sections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lesson_id UUID NOT NULL REFERENCES course_lessons(id),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    content TEXT NOT NULL,
    order INT NOT NULL
);

-- Create table for Chat Sessions
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    curriculum_id UUID,
    lesson_id UUID,
    exercise_id UUID,
    created_at_utc TIMESTAMP NOT NULL DEFAULT now()
);

-- Create table for Chat Messages
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id),
    is_user BOOLEAN NOT NULL,
    content TEXT NOT NULL,
    created_at_utc TIMESTAMP NOT NULL DEFAULT now()
);

-- Create table for Chat Tool Calls
CREATE TABLE IF NOT EXISTS chat_tool_calls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES chat_messages(id),
    tool_call_id TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    json_arguments TEXT NOT NULL,
    result TEXT NOT NULL
);

-- Create playground session table
CREATE TABLE IF NOT EXISTS playground_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type TEXT NOT NULL,
    instance_hostname TEXT,
    created_at_utc TIMESTAMP NOT NULL DEFAULT now()
);