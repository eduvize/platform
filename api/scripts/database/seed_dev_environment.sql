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
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    bio TEXT NOT NULL,
    github_username TEXT,
    avatar_url TEXT,
    last_updated_at_utc TIMESTAMP NOT NULL DEFAULT now()
);

-- Create schema for User Skills
CREATE TABLE IF NOT EXISTS user_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    skill TEXT NOT NULL,
    proficiency INT NOT NULL,
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

-----------------------
--- SEED UTILS --------
-----------------------

-- Function to get user ID by username
CREATE OR REPLACE FUNCTION get_user_id(retrieve_username TEXT)
RETURNS UUID AS $$
DECLARE
    user_id UUID;
BEGIN
    SELECT id INTO user_id FROM users WHERE username = retrieve_username;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'User not found';
    END IF;
    RETURN user_id;
END;
$$ LANGUAGE plpgsql;

-- Function to get curriculum ID by title
CREATE OR REPLACE FUNCTION get_curriculum_id(curriculum_title TEXT)
RETURNS UUID AS $$
DECLARE
    curriculum_id UUID;
BEGIN
    SELECT id INTO curriculum_id FROM curriculums WHERE title = curriculum_title;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Curriculum not found';
    END IF;
    RETURN curriculum_id;
END;
$$ LANGUAGE plpgsql;

-- Function to get lesson ID by title
CREATE OR REPLACE FUNCTION get_lesson_id(lesson_title TEXT)
RETURNS UUID AS $$
DECLARE
    lesson_id UUID;
BEGIN
    SELECT id INTO lesson_id FROM lessons WHERE title = lesson_title;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Lesson not found';
    END IF;
    RETURN lesson_id;
END;
$$ LANGUAGE plpgsql;

-- Function to insert a user profile associae with a user by username
CREATE OR REPLACE FUNCTION insert_user_profile(username TEXT, first_name TEXT, last_name TEXT, bio TEXT, github_username TEXT, avatar_url TEXT)
RETURNS VOID AS $$
DECLARE
    user_id UUID;
BEGIN
    user_id := get_user_id(username);
    INSERT INTO user_profiles (user_id, first_name, last_name, bio, github_username, avatar_url)
    VALUES (user_id, first_name, last_name, bio, github_username, avatar_url);
END;
$$ LANGUAGE plpgsql;

-- Function to insert a user skill associated with a user by username
CREATE OR REPLACE FUNCTION insert_user_skill(username TEXT, skill TEXT, proficiency INT, notes TEXT)
RETURNS VOID AS $$
DECLARE
    user_id UUID;
BEGIN
    user_id := get_user_id(username);
    INSERT INTO user_skills (user_id, skill, proficiency, notes)
    VALUES (user_id, skill, proficiency, notes);
END;
$$ LANGUAGE plpgsql;

-- Function to insert a lesson associated with a curriculum by title
CREATE OR REPLACE FUNCTION insert_lesson(curriculum_title TEXT, lesson_title TEXT, lesson_description TEXT, lesson_index INT)
RETURNS VOID AS $$
DECLARE
    curriculum_id UUID;
BEGIN
    curriculum_id := get_curriculum_id(curriculum_title);
    INSERT INTO lessons (curriculum_id, title, description, curriculum_index)
    VALUES (curriculum_id, lesson_title, lesson_description, lesson_index);
END;
$$ LANGUAGE plpgsql;

-- Function to insert a curriculum enrollment by curriculum title and user username
CREATE OR REPLACE FUNCTION insert_curriculum_enrollment(curriculum_title TEXT, username TEXT)
RETURNS VOID AS $$
DECLARE
    curriculum_id UUID;
    user_id UUID;
BEGIN
    curriculum_id := get_curriculum_id(curriculum_title);
    user_id := get_user_id(username);
    INSERT INTO curriculum_enrollments (curriculum_id, user_id)
    VALUES (curriculum_id, user_id);
END;
$$ LANGUAGE plpgsql;

-- Function to insert exercises by lesson title
CREATE OR REPLACE FUNCTION insert_exercise(lesson_title TEXT, user_username TEXT, instructions TEXT, expectations TEXT)
RETURNS VOID AS $$
DECLARE
    lesson_id UUID;
    user_id UUID;
BEGIN
    lesson_id := get_lesson_id(lesson_title);
    user_id := get_user_id(user_username);
    INSERT INTO exercises (lesson_id, user_id, instructions, expectations)
    VALUES (lesson_id, user_id, instructions, expectations);
END;
$$ LANGUAGE plpgsql;

-- Function to insert a chat session and messages
CREATE OR REPLACE FUNCTION insert_chat_session_and_messages(user_username TEXT, curriculum_title TEXT, lesson_title TEXT, message_texts TEXT[])
RETURNS VOID AS $$
DECLARE
    user_id UUID;
    curriculum_id UUID;
    lesson_id UUID;
    session_id UUID;
    message_text TEXT; -- Explicitly declare the loop variable
BEGIN
    user_id := get_user_id(user_username);
    curriculum_id := get_curriculum_id(curriculum_title);
    lesson_id := get_lesson_id(lesson_title);
    INSERT INTO chat_sessions (user_id, curriculum_id, lesson_id)
    VALUES (user_id, curriculum_id, lesson_id) RETURNING id INTO session_id;
    
    FOREACH message_text IN ARRAY message_texts LOOP
        INSERT INTO chat_messages (session_id, is_user, content)
        VALUES (session_id, (message_text <> 'Loops are used to repeat a block of code multiple times.'), message_text);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Function to get exercise ID by instructions
CREATE OR REPLACE FUNCTION get_exercise_id(instructions_text TEXT)
RETURNS UUID AS $$
DECLARE
    exercise_id UUID;
BEGIN
    SELECT id INTO exercise_id FROM exercises WHERE instructions = instructions_text;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Exercise not found';
    END IF;
    RETURN exercise_id;
END;
$$ LANGUAGE plpgsql;

-----------------------
--- BEGIN TEST DATA ---
-----------------------

-- Insert test data for Users
INSERT INTO users (username, email, password_hash)
VALUES 
('johndoe', 'john.doe@example.com', '$2b$12$JBREC3mPZFlcf/qOzyxHLO93E.77ZJzZtWdqHIgiW92Ugvb/qo.1m');

SELECT insert_user_profile('johndoe', 'John', 'Doe', 'Software Engineer', 'johndoe', 'https://avatars.example.com/johndoe.jpg');

SELECT insert_user_skill('johndoe', 'C#', 4, 'This is my primary language I work in day to day. I am senior level and use .NET Core.');
SELECT insert_user_skill('johndoe', 'React', 4, 'I am very comfortable with React and have built several projects with it leveraging state management like Redux, typescript, and functional components.');

-- Insert test data for Curriculums
INSERT INTO curriculums (title, description, view_count, enrollment_count)
VALUES 
('Introduction to Programming', 'Learn the basics of programming.', 150, 10),
('Advanced Programming', 'Deep dive into advanced topics in programming.', 100, 5);

-- Insert test data for Lessons linked to curriculums
SELECT insert_lesson('Introduction to Programming', 'Lesson 1: Variables', 'Introduction to variables.', 1);
SELECT insert_lesson('Introduction to Programming', 'Lesson 2: Control Structures', 'Understanding loops and conditionals.', 2);
SELECT insert_lesson('Advanced Programming', 'Lesson 1: Memory Management', 'Explore how memory management works.', 1);

-- Insert test data for Curriculum Enrollment
SELECT insert_curriculum_enrollment('Introduction to Programming', 'johndoe');
SELECT insert_curriculum_enrollment('Advanced Programming', 'johndoe');

-- Insert test data for Curriculum Reviews
INSERT INTO curriculum_reviews (curriculum_id, user_id, rating, review)
VALUES 
(get_curriculum_id('Introduction to Programming'), get_user_id('johndoe'), 4.5, 'Great introduction to programming!'),
(get_curriculum_id('Advanced Programming'), get_user_id('johndoe'), 4.8, 'Challenging yet rewarding lessons on advanced topics.');

-- Insert test data for Exercises linked to lessons
SELECT insert_exercise('Lesson 1: Variables', 'johndoe', 'Create a variable.', 'The variable should store an integer.');
SELECT insert_exercise('Lesson 2: Control Structures', 'johndoe', 'Implement a for loop.', 'The loop should iterate at least 10 times.');
SELECT insert_exercise('Lesson 1: Memory Management', 'johndoe', 'Discuss garbage collection.', 'Explain how it impacts performance.');

-- Insert test data for Exercise Submissions using the function
INSERT INTO exercise_submissions (exercise_id, content)
VALUES 
(get_exercise_id('Create a variable.'), 'int number = 10;'),
(get_exercise_id('Implement a for loop.'), 'for (int i = 0; i < 10; i++) { console.log(i); }'),
(get_exercise_id('Discuss garbage collection.'), 'Garbage collection helps manage memory automatically.');

-- Insert test data for User Curriculums
INSERT INTO user_curriculums (user_id, curriculum_id, instructor_notes, current_lesson_id)
VALUES 
(get_user_id('johndoe'), get_curriculum_id('Introduction to Programming'), 'Needs to focus more on practical exercises.', get_lesson_id('Lesson 1: Variables')),
(get_user_id('johndoe'), get_curriculum_id('Advanced Programming'), 'Excellent progress, can handle more complexity.', get_lesson_id('Lesson 1: Memory Management'));

-- Insert test data for Chat Sessions and Messages
SELECT insert_chat_session_and_messages('johndoe', 'Introduction to Programming', 'Lesson 1: Variables', ARRAY['I am having trouble understanding loops.', 'Loops are used to repeat a block of code multiple times.']);