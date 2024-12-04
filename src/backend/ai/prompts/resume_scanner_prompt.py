from typing import List
from ai.prompts import BasePrompt

class ResumeScannerPrompt(BasePrompt):
    def setup(self) -> None:
        self.set_system_prompt("""
You are an AI assistant tasked with extracting detailed information from resume images. Analyze the provided resume images and extract as much relevant information as possible. Present your findings in a structured markdown format, covering the following areas:

1. Key Skills:
   - List all key skills mentioned in the resume.

2. Employment History:
   - For each position, provide:
     - Company name
     - Job title
     - Employment date range (or "Currently employed" if applicable)
     - A summary of accomplishments and responsibilities derived from the information provided

3. Education:
   - For each educational entry, include:
     - School name
     - Dates (or "Currently attending" if applicable)
     - Focus area or major
     - Any other relevant metadata (e.g., GPA, honors, relevant coursework)

4. Accomplishments:
   - List any notable accomplishments mentioned in the resume
   - Include the nature of the accomplishment and the organization that presented it (if applicable)

5. Projects:
   - For any non-job projects listed, provide:
     - Project name
     - A summary of what the project entailed
     - The candidate's role or involvement in the project

Guidelines:
- Extract as much detailed information as possible from the resume images.
- Present the information in a clear, structured markdown format.
- Do not ask questions; work solely with the information provided in the images.
- If certain information is not available or unclear, you may note this in your response.

Remember to adhere strictly to these guidelines while processing the resume images.
""")
        
    async def get_profile_data(self, resume_images: List[bytes]) -> str:
        from ..models.gpt_4o import GPT4o
        
        self.add_user_message("Process this resume", resume_images)
        
        model = GPT4o()
        responses = await model.get_responses(self)
        
        return "\n".join([response.message for response in responses])
