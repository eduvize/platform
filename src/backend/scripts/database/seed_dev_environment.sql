-- Create table for Users
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    pending_verification BOOLEAN NOT NULL DEFAULT FALSE,
    verification_code TEXT,
    verification_sent_at_utc TIMESTAMP,
    created_at_utc TIMESTAMP NOT NULL DEFAULT now(),
    last_login_at_utc TIMESTAMP
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

-- Create table for professional skills
CREATE TABLE IF NOT EXISTS user_profiles_professional_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_profile_professional_id UUID NOT NULL REFERENCES user_profiles_professional(id),
    skill_id UUID NOT NULL REFERENCES user_profiles_skills(id)
);

-- Create table for mapping disciplines and proficiency levels to user profiles
CREATE TABLE IF NOT EXISTS user_profiles_disciplines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_profile_id UUID NOT NULL REFERENCES user_profiles(id),
    discipline_type INT NOT NULL,
    proficiency INT
);

-- Create table for Curriculums
CREATE TABLE IF NOT EXISTS curriculums (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    view_count INT NOT NULL,
    enrollment_count INT NOT NULL,
    created_at_utc TIMESTAMP NOT NULL DEFAULT now()
);

-- Create table for Curriculum Reviews
CREATE TABLE IF NOT EXISTS curriculum_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    curriculum_id UUID NOT NULL REFERENCES curriculums(id),
    user_id UUID NOT NULL REFERENCES users(id),
    rating DOUBLE PRECISION NOT NULL,
    review TEXT NOT NULL,
    created_at_utc TIMESTAMP NOT NULL DEFAULT now()
);

-- Create table for Curriculum Enrollment
CREATE TABLE IF NOT EXISTS curriculum_enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    curriculum_id UUID NOT NULL REFERENCES curriculums(id),
    user_id UUID NOT NULL REFERENCES users(id),
    created_at_utc TIMESTAMP NOT NULL DEFAULT now()
);

-- Create table for Lessons
CREATE TABLE IF NOT EXISTS lessons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    curriculum_id UUID NOT NULL REFERENCES curriculums(id),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    curriculum_index INT NOT NULL
);

-- Create table for Exercises
CREATE TABLE IF NOT EXISTS exercises (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lesson_id UUID NOT NULL REFERENCES lessons(id),
    user_id UUID NOT NULL REFERENCES users(id),
    instructions TEXT NOT NULL,
    expectations TEXT NOT NULL
);

-- Create table for Exercise Submissions
CREATE TABLE IF NOT EXISTS exercise_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exercise_id UUID NOT NULL REFERENCES exercises(id),
    content TEXT NOT NULL,
    created_at_utc TIMESTAMP NOT NULL DEFAULT now()
);

-- Create table for User Curriculums
CREATE TABLE IF NOT EXISTS user_curriculums (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    curriculum_id UUID NOT NULL REFERENCES curriculums(id),
    instructor_notes TEXT NOT NULL,
    current_lesson_id UUID NOT NULL REFERENCES lessons(id)
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