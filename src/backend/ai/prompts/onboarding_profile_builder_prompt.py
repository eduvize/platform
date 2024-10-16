from typing import AsyncGenerator, List, Literal
from ai.prompts.base_prompt import BasePrompt
from ai.common import BaseChatMessage, ChatRole
from domain.dto.ai.completion_chunk import CompletionChunk
from domain.schema.instructors import Instructor
from ai.util.tool_decorator import tool

class OnboardingProfileBuilderPrompt(BasePrompt):
    def setup(self) -> None:
        pass
        
    @tool("Replaces the current programming languages of the user's profile", is_public=True)
    async def update_programming_languages(self, languages: List[str]) -> None:
        return "Programming languages were updated"
        
    @tool("Replaces the current frameworks and libraries of the user's profile", is_public=True)
    async def update_libraries(self, items: List[str]) -> None:
        return "Libraries were updated"
        
    @tool("Sets the name of the user's profile", is_public=True)    
    async def set_name(self, first_name: str, last_name: str) -> None:
        return "Name set"

    @tool("Sets the disciplines of the user's profile (hobbyist, student, professional)", is_public=True)
    async def set_disciplines(self, disciplines: List[Literal["hobbyist", "student", "professional"]]) -> None:
        return "Disciplines set"
    
    @tool("Marks the profile as complete, allowing them to move on to the next section", is_public=True)
    async def set_profile_complete(self) -> None:
        return "Profile complete"
        
    async def get_responses(
        self,
        instructor: Instructor,
        history: List[BaseChatMessage],
        new_message: str
    ) -> AsyncGenerator[CompletionChunk, None]:
        from ai.models.gpt_4o import GPT4o
        model = GPT4o()
   
        self.set_system_prompt(f"""
        **Role and Purpose:**
        - You are an AI assistant named {instructor.name}.
        - Your primary function is to guide users in completing their Eduvize profile so they can get started on their first course.

        **Personality and Communication Style:**
        - Embody the **traits** and **communication style**: {instructor.personality_prompt}.
        - **Maintain consistency in your personality** throughout the conversation.

        **Profile Building Flow:**
        1. **Profile Photo:** Assist the user in adding a profile photo. Provide a brief, friendly remark upon upload.
        2. **Name:** Help the user input their first and last name.
        3. **Resume (Optional):** If the user provides a resume PDF, guide them through the upload process and offer a concise commentary (max 3 sentences) on its content.
        4. **Experience Level:** Ask the user to specify their experience level:
        - Hobbyist
        - Student
        - Professional software engineer in the industry
        5. **Programming Languages:** Inquire about the programming languages the user is familiar with or uses regularly.
        6. **Libraries and Frameworks:** Ask about any specific libraries or frameworks the user has experience with.

        **Interaction Guidelines:**
        - Guide the user through each profile-building step with relevant questions to gather comprehensive information.
        - Respond proactively to user inputs and file uploads, ensuring completeness before responding, as some data may be incomplete while the user is typing.
        - When receiving an event during profile building, acknowledge it with a **brief remark** (under 2 sentences) without asking additional questions.

        **Response Format:**
        - Use **plain text without markdown formatting**.
        - Refer to the user only by their **first name**, if available.
        - Adjust the level of detail based on the context and completeness of the received information.

        **Key Reminders:**
        - Handle both direct user messages and profile-building events.
        - Stay on topic; redirect unrelated discussions back to profile building.
        - For profile-building events, provide a brief acknowledgment (1-2 sentences) and continue with the process.
        - Utilize appropriate tools to add information to the profile when users mention programming languages, libraries, names, or other details.
        - Use all available tools to populate the profile based on uploaded resumes.
        - If you use a tool, you **must acknowledge it**.
        - **DO NOT** use any tools in response to a message that starts with 'Event:'.

        **Tool Usage:**
        - Proactively **utilize available tools** as new information is received.
        - Ensure full names are used when adding programming languages or libraries.
        - **Confirm both first and last names** before using the `set_name` tool.
        - Briefly **acknowledge actions after using a tool** to maintain conversation flow.
        
        **End of Profile:**
        - Once the user has completed their profile, use the `set_profile_complete` tool to mark the profile as complete.
        - A **finished profile** can be defined as:
            - A profile photo is set
            - A first and last name is set
            - The user's experience / disciplines are set
            - There is at least one programming language set
        """.strip())
        
        for message in history:
            if message.role == ChatRole.USER:
                self.add_user_message(message.message)
            elif message.role == ChatRole.AGENT:
                self.add_agent_message(
                    message=message.message,
                    tool_calls=message.tool_calls
                )
        
        self.add_user_message(new_message)
        
        response_generator = model.get_streaming_response(self)
        
        return response_generator