-- Create schema for Users
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

-- Create schema for User Profiles
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    first_name TEXT,
    last_name TEXT,
    bio TEXT,
    github_username TEXT,
    avatar_url TEXT,
    last_updated_at_utc TIMESTAMP NOT NULL DEFAULT now()
);

-- Create schema for skills
CREATE TABLE IF NOT EXISTS user_profiles_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_profile_id UUID NOT NULL REFERENCES user_profiles(id),
    skill_type INT NOT NULL,
    skill TEXT NOT NULL,
    proficiency INT,
    notes TEXT
);

-- Create schema for the hobby portion of the user profile
CREATE TABLE IF NOT EXISTS user_profiles_hobby (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_profile_id UUID NOT NULL REFERENCES user_profiles(id)
);

-- Create schema for hobby reasons
CREATE TABLE IF NOT EXISTS user_profiles_hobby_reasons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_profile_hobby_id UUID NOT NULL REFERENCES user_profiles_hobby(id),
    reason TEXT NOT NULL
);

-- Create schema for hobby projects
CREATE TABLE IF NOT EXISTS user_profiles_hobby_projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_profile_hobby_id UUID NOT NULL REFERENCES user_profiles_hobby(id),
    project_name TEXT NOT NULL,
    description TEXT NOT NULL,
    purpose TEXT
);

-- Create the schema for the student portion of the user profile
CREATE TABLE IF NOT EXISTS user_profiles_student (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_profile_id UUID NOT NULL REFERENCES user_profiles(id)
);

-- Create the schema for the professional portion of the user profile
CREATE TABLE IF NOT EXISTS user_profiles_professional (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_profile_id UUID NOT NULL REFERENCES user_profiles(id)
);

-- Create schema for the frontend portion of the user profile
CREATE TABLE IF NOT EXISTS user_profiles_frontend (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_profile_id UUID NOT NULL REFERENCES user_profiles(id)
);

-- Create the schema for the backend portion of the user profile
CREATE TABLE IF NOT EXISTS user_profiles_backend (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_profile_id UUID NOT NULL REFERENCES user_profiles(id)
);

-- Create the schema for the database portion of the user profile
CREATE TABLE IF NOT EXISTS user_profiles_database (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_profile_id UUID NOT NULL REFERENCES user_profiles(id)
);

-- Create the schema for the devops portion of the user profile
CREATE TABLE IF NOT EXISTS user_profiles_devops (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_profile_id UUID NOT NULL REFERENCES user_profiles(id)
);

-- Create schema for User Skills
CREATE TABLE IF NOT EXISTS user_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    skill_type INT NOT NULL,
    skill TEXT NOT NULL,
    proficiency INT,
    notes TEXT,
    created_at_utc TIMESTAMP NOT NULL DEFAULT now()
);

-- Create schema for Curriculums
CREATE TABLE IF NOT EXISTS curriculums (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    view_count INT NOT NULL,
    enrollment_count INT NOT NULL,
    created_at_utc TIMESTAMP NOT NULL DEFAULT now()
);

-- Create schema for Curriculum Reviews
CREATE TABLE IF NOT EXISTS curriculum_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    curriculum_id UUID NOT NULL REFERENCES curriculums(id),
    user_id UUID NOT NULL REFERENCES users(id),
    rating DOUBLE PRECISION NOT NULL,
    review TEXT NOT NULL,
    created_at_utc TIMESTAMP NOT NULL DEFAULT now()
);

-- Create schema for Curriculum Enrollment
CREATE TABLE IF NOT EXISTS curriculum_enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    curriculum_id UUID NOT NULL REFERENCES curriculums(id),
    user_id UUID NOT NULL REFERENCES users(id),
    created_at_utc TIMESTAMP NOT NULL DEFAULT now()
);

-- Create schema for Lessons
CREATE TABLE IF NOT EXISTS lessons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    curriculum_id UUID NOT NULL REFERENCES curriculums(id),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    curriculum_index INT NOT NULL
);

-- Create schema for Exercises
CREATE TABLE IF NOT EXISTS exercises (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lesson_id UUID NOT NULL REFERENCES lessons(id),
    user_id UUID NOT NULL REFERENCES users(id),
    instructions TEXT NOT NULL,
    expectations TEXT NOT NULL
);

-- Create schema for Exercise Submissions
CREATE TABLE IF NOT EXISTS exercise_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exercise_id UUID NOT NULL REFERENCES exercises(id),
    content TEXT NOT NULL,
    created_at_utc TIMESTAMP NOT NULL DEFAULT now()
);

-- Create schema for User Curriculums
CREATE TABLE IF NOT EXISTS user_curriculums (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    curriculum_id UUID NOT NULL REFERENCES curriculums(id),
    instructor_notes TEXT NOT NULL,
    current_lesson_id UUID NOT NULL REFERENCES lessons(id)
);

-- Create schema for Chat Sessions
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    curriculum_id UUID,
    lesson_id UUID,
    exercise_id UUID,
    created_at_utc TIMESTAMP NOT NULL DEFAULT now()
);

-- Create schema for Chat Messages
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id),
    is_user BOOLEAN NOT NULL,
    content TEXT NOT NULL,
    created_at_utc TIMESTAMP NOT NULL DEFAULT now()
);

-- Create schema for Chat Tool Calls
CREATE TABLE IF NOT EXISTS chat_tool_calls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES chat_messages(id),
    tool_call_id TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    json_arguments TEXT NOT NULL,
    result TEXT NOT NULL
);