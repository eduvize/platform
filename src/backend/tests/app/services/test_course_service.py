import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
import uuid
from app.services.course_service import CourseService
from domain.dto.courses import CoursePlanDto, CourseProgressionDto, CourseListingDto
from domain.dto.profile import UserProfileDto
from domain.enums.course_enums import CourseMotivation, CurrentSubjectExperience, CourseMaterial
from common.storage import StoragePurpose
from domain.schema.courses import Course, Lesson, Module, Section, CourseExercise, CourseExerciseObjective
from domain.topics import CourseGenerationTopic
from common.messaging.topics import Topic
from ai.prompts.course_generation.models import CourseOutline, ModuleOutline, LessonOutline, SectionOutline
import asyncio

# Sample data
user_id = str(uuid.uuid4())
course_id = str(uuid.uuid4())
resource_id = uuid.uuid4()
plan = CoursePlanDto(
    subject="React",
    motivations=[
        CourseMotivation.CAREER.value
    ],
    experience=CurrentSubjectExperience.KNOWLEDGEABLE.value,
    materials=[CourseMaterial.READING.value],
    desired_outcome="To build a React app"
)
current_module_id = uuid.uuid4()
current_lesson_id = uuid.uuid4()
course = Course(
    id=course_id, 
    title="Sample Course", 
    description="A sample course", 
    cover_image_url="",
    user_id=uuid.UUID(user_id),
    modules=[
        Module(
            id=current_module_id,
            course_id=course_id,
            title="Module 1",
            description="Learn the basics of React",
            order=0,
            lessons=[
                Lesson(
                    id=current_lesson_id,
                    module_id=current_module_id,
                    title="Lesson 1",
                    description="Introduction to React",
                    order=0,
                    sections=[
                        Section(
                            title="Section 1",
                            description="Introduction to React",
                            content="",
                            order=0
                        )
                    ],
                    exercises=[]
                )
            ]
        )    
    ], 
    current_lesson_id=current_lesson_id
)

def clone_course():
    return Course.model_copy(course)

lesson = Lesson(id=uuid.uuid4(), sections=[])
profile_dto = UserProfileDto(first_name="John", last_name="Doe")

@pytest.fixture
@patch("app.services.course_service.OpenAI", autospec=True)
def course_service(mock_openai):
    user_service = MagicMock()
    course_repo = MagicMock()
    return CourseService(user_service=user_service, course_repo=course_repo)

@pytest.mark.asyncio
@patch("app.services.course_service.GetAdditionalInputsPrompt", autospec=True)
@patch("app.services.course_service.get_user_profile_text", autospec=True)
async def test_get_additional_inputs(mock_get_user_profile_text, mock_prompt, course_service):
    """
    Tests get_additional_inputs method:
    1. Should call user_service.get_user to validate the user.
    2. Should return the additional inputs from the prompt.
    """
    # Mock user service and profile handling
    course_service.user_service.get_user = AsyncMock(return_value=MagicMock(profile=profile_dto))
    mock_get_user_profile_text.return_value = "User Profile Text"
    
    # Mock the prompt to return additional inputs
    mock_prompt_instance = mock_prompt.return_value
    mock_prompt_instance.get_inputs.return_value = {"additional_input": "value"}
    
    result = await course_service.get_additional_inputs(user_id=user_id, plan=plan)
    
    course_service.user_service.get_user.assert_awaited_once_with("id", user_id, ["profile.*"])
    mock_prompt_instance.get_inputs.assert_called_once_with(plan=plan, profile_text="User Profile Text")
    
    assert result == {"additional_input": "value"}

@pytest.mark.asyncio
@patch("app.services.course_service.import_from_url", autospec=True)
@patch("app.services.course_service.get_public_object_url", autospec=True)
@patch("app.services.course_service.GenerateCourseOutlinePrompt", autospec=True)
@patch("app.services.course_service.get_user_profile_text", autospec=True)
@patch("app.services.course_service.KafkaProducer", autospec=True)
async def test_generate_course(
    mock_kafka_inst: Mock, 
    mock_get_user_profile_text: Mock, 
    mock_generate_course_outline_prompt: Mock, 
    mock_get_public_object_url: Mock, 
    mock_import_from_url: Mock, 
    course_service
):
    """
    Tests generate_course method:
    1. Should call user_service.get_user to validate the user.
    2. Should generate the course outline.
    3. Should create the course in the repository and send a message to Kafka.
    """
    # Mock user service and profile handling
    course_service.user_service.get_user = AsyncMock(return_value=MagicMock(profile=profile_dto))
    
    # Mock the outline
    mock_outline = CourseOutline(
        course_subject=plan.subject, 
        course_title="A React Course", 
        description="Learn React from scratch",
        modules=[
            ModuleOutline(
                internal_name="module1",
                title="Module 1",
                focus_area="React Basics",
                description="Learn the basics of React",
                lessons=[
                    LessonOutline(
                        internal_name="lesson1",
                        focus_area="React Basics",
                        title="Lesson 1",
                        description="Introduction to React",
                        sections=[
                            SectionOutline(
                                title="Section 1",
                                description="Introduction to React"
                            )
                        ]
                    )
                ]
            )
        ],
        key_outcomes=[]
    )
    
    # Mock the outline generation and cover image
    mock_prompt_instance = mock_generate_course_outline_prompt.return_value
    mock_prompt_instance.get_outline.return_value = mock_outline
    
    mock_import_from_url.return_value = "cover_image_object_id"
    mock_get_public_object_url.return_value = "public_cover_image_url"
    
    mock_get_user_profile_text.return_value = "User Profile Text"
    
    mock_kafka_producer = Mock()
    mock_kafka_inst.return_value = mock_kafka_producer
    mock_kafka_producer.produce_message = AsyncMock()
    
    course_service.generate_cover_image = AsyncMock(return_value="cover_image_url")
    
    # Mock course repository
    course_service.course_repo.create_course = AsyncMock(return_value=course_id)
    
    # Call the method under test
    await course_service.generate_course(user_id=user_id, plan=plan)
    
    # Assertions
    course_service.user_service.get_user.assert_awaited_once_with("id", user_id, ["profile.*"])
    mock_prompt_instance.get_outline.assert_called_once_with(plan=plan, profile_text="User Profile Text")
    mock_import_from_url.assert_called_once()
    mock_get_public_object_url.assert_called_once_with(StoragePurpose.COURSE_ASSET, "cover_image_object_id")
    
    course_service.course_repo.create_course.assert_called_once()
    
    mock_kafka_producer.produce_message.assert_called_once_with(
        topic=Topic.GENERATE_NEW_COURSE,
        message=CourseGenerationTopic(
            user_id=uuid.UUID(user_id),
            course_id=uuid.UUID(course_id), 
            course_outline=mock_outline
        )
    )

@pytest.mark.asyncio
async def test_mark_lesson_complete_baseline(course_service):
    """
    Tests mark_section_as_completed method:
    1. Should return CourseProgressionDto with correct data when section is completed.
    """
    
    # Mock user and course
    course_service.user_service.get_user = AsyncMock(return_value=MagicMock(id=user_id))
    course_service.course_repo.get_course = AsyncMock(return_value=course)
    
    # Mock repository calls to set lesson progression
    course_service.course_repo.get_next_lesson = AsyncMock(return_value=None)
    course_service.course_repo.set_current_lesson = AsyncMock()
    course_service.course_repo.set_course_completion = AsyncMock()
    
    result = await course_service.mark_lesson_complete(user_id=user_id, course_id=course_id, lesson_id=current_lesson_id)
    
    course_service.user_service.get_user.assert_awaited_once_with("id", user_id)
    course_service.course_repo.get_course.assert_called_once_with(course_id)
    
    assert isinstance(result, CourseProgressionDto)
    
@pytest.mark.asyncio
async def test_mark_lesson_complete_not_current_lesson(course_service):
    """
    Ensures that the mark_lesson_complete method does not mutate the course if the lesson provided is not the current lesson.
    """
    
    # Mock user and course
    course_service.user_service.get_user = AsyncMock(return_value=MagicMock(id=user_id))
    course_service.course_repo.get_course = AsyncMock(return_value=course)
    
    # Mock repository calls to set lesson progression
    course_service.course_repo.set_current_lesson = AsyncMock()
    course_service.course_repo.set_course_completion = AsyncMock()
    
    await course_service.mark_lesson_complete(user_id=user_id, course_id=course_id, lesson_id=uuid.uuid4())
    
    # Verify set_current_lesson and set_course_completion were not called
    course_service.course_repo.set_current_lesson.assert_not_called()
    course_service.course_repo.set_course_completion.assert_not_called()
    
@pytest.mark.asyncio
async def test_mark_lesson_complete_last_lesson(course_service):
    """
    Verifies the set_course_completion method is called when the last lesson is completed.
    """

    cloned_course = clone_course()
    
    # Mock user and course
    course_service.user_service.get_user = AsyncMock(return_value=MagicMock(id=user_id))
    course_service.course_repo.get_course = AsyncMock(return_value=cloned_course)
    course_service.course_repo.get_next_lesson = AsyncMock(return_value=None)
    
    # Mock repository calls to set lesson progression
    course_service.course_repo.set_current_lesson = AsyncMock()
    course_service.course_repo.set_course_completion = AsyncMock()
    
    await course_service.mark_lesson_complete(user_id=user_id, course_id=course_id, lesson_id=current_lesson_id)
    
    # Verify set_course_completion was called
    course_service.course_repo.set_course_completion.assert_called_once_with(course_id)
    
@pytest.mark.asyncio
async def test_mark_lesson_complete_without_completing_exercise(course_service):
    """
    Verifies that a lesson cannot be marked complete when an exercise is unfinished
    """
    
    cloned_course = clone_course()
    
    cloned_course.modules[0].lessons[0].exercises.append(CourseExercise(id=uuid.uuid4(), objectives=[
        CourseExerciseObjective(id=uuid.uuid4(), is_completed=False)
    ]))
    
    # Mock user and course
    course_service.user_service.get_user = AsyncMock(return_value=MagicMock(id=user_id))
    course_service.course_repo.get_course = AsyncMock(return_value=cloned_course)
    
    # Mock repository calls to set lesson progression
    course_service.course_repo.set_current_lesson = AsyncMock()
    course_service.course_repo.set_course_completion = AsyncMock()
    
    # Mock repository calls to get exercise objectives
    course_service.course_repo.get_exercise_objectives = AsyncMock(return_value=[CourseExerciseObjective()])
    
    await course_service.mark_lesson_complete(user_id=user_id, course_id=course_id, lesson_id=current_lesson_id)
    
    # Verify set_current_lesson and set_course_completion were not called
    course_service.course_repo.set_current_lesson.assert_not_called()
    course_service.course_repo.set_course_completion.assert_not_called()

@pytest.mark.asyncio
async def test_get_courses(course_service):
    """
    Tests get_courses method:
    1. Should return a list of CourseListingDto for the user.
    """
    # Mock user and courses
    course_service.user_service.get_user = AsyncMock(return_value=MagicMock(id=user_id))
    course_service.course_repo.get_courses = AsyncMock(return_value=[course])
    
    # Mock lesson count retrieval
    course_service.course_repo.get_lesson_count = AsyncMock(return_value=10)
    
    result = await course_service.get_courses(user_id=user_id)
    
    course_service.user_service.get_user.assert_awaited_once_with("id", user_id)
    course_service.course_repo.get_courses.assert_called_once_with(user_id)
    
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], CourseListingDto)

@pytest.mark.asyncio
async def test_get_course(course_service):
    """
    Tests get_course method:
    1. Should return a specific course for the user.
    """
    # Mock user and course
    course_service.user_service.get_user = AsyncMock(return_value=MagicMock(id=user_id))
    course_service.course_repo.get_course = AsyncMock(return_value=course)
    
    result = await course_service.get_course(user_id=user_id, course_id=course_id)
    
    course_service.user_service.get_user.assert_awaited_once_with("id", user_id)
    course_service.course_repo.get_course.assert_called_once_with(course_id)
    
    assert result == course

@pytest.mark.asyncio
async def test_generate_cover_image(course_service):
    """
    Tests generate_cover_image method:
    1. Should generate an image using OpenAI and return the URL.
    """
    # Mock OpenAI response
    mock_response = MagicMock()
    mock_response.data = [MagicMock(url="generated_image_url")]
    course_service.openai = MagicMock(images=AsyncMock())
    course_service.openai.images.generate = AsyncMock(return_value=mock_response)
    
    result = await course_service.generate_cover_image(subject="Python")
    
    course_service.openai.images.generate.assert_awaited_once_with(
        model="dall-e-3",
        prompt="Icon of Python, dark background, cinema 4d, isomorphic",
        size="1024x1024",
        quality="standard",
        n=1
    )
    
    assert result == "generated_image_url"

@pytest.mark.asyncio
async def test_get_exercises(course_service):
    """
    Tests get_exercises method:
    1. Should return a list of ExercisePlan for the course.
    """
    # Mock course and repository
    mock_course = MagicMock()
    mock_course.modules = [
        MagicMock(title="Module 1", lessons=[
            MagicMock(title="Lesson 1", sections=[MagicMock(content="Lesson 1 content")])
        ])
    ]
    course_service.course_repo.get_course = AsyncMock(return_value=mock_course)

    # Mock GenerateExercisesPrompt
    mock_prompt = MagicMock()
    mock_prompt.get_exercise.return_value = MagicMock()
    with patch("app.services.course_service.GenerateExercisesPrompt", return_value=mock_prompt):
        result = await course_service.get_exercises(course_id=uuid.uuid4())

    course_service.course_repo.get_course.assert_awaited_once()
    assert isinstance(result, list)
    assert len(result) == 1  # One exercise per lesson

@pytest.mark.asyncio
async def test_get_exercise(course_service):
    """
    Tests get_exercise method:
    1. Should return a specific exercise for the given exercise_id.
    """
    mock_exercise = MagicMock()
    course_service.course_repo.get_exercise = AsyncMock(return_value=mock_exercise)

    exercise_id = uuid.uuid4()
    result = await course_service.get_exercise(exercise_id=exercise_id)

    course_service.course_repo.get_exercise.assert_awaited_once_with(exercise_id)
    assert result == mock_exercise

@pytest.mark.asyncio
async def test_set_objective_status(course_service):
    """
    Tests set_objective_status method:
    1. Should call the repository method to set the objective status.
    """
    course_service.course_repo.set_objective_status = AsyncMock()

    exercise_id = uuid.uuid4()
    objective_id = uuid.uuid4()
    is_complete = True

    await course_service.set_objective_status(
        exercise_id=exercise_id,
        objective_id=objective_id,
        is_complete=is_complete
    )

    course_service.course_repo.set_objective_status.assert_awaited_once_with(objective_id, is_complete)