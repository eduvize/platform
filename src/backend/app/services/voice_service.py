import base64
import re
from typing import AsyncIterator
from elevenlabs import AsyncElevenLabs, VoiceSettings
from config import get_elevenlabs_api_key, get_openai_key
from openai import AsyncOpenAI
import io
import tempfile
import os

class VoiceService:
    elevenlabs: AsyncElevenLabs
    
    def __init__(self):
        self.elevenlabs = AsyncElevenLabs(api_key=get_elevenlabs_api_key())
        self.openai = AsyncOpenAI(api_key=get_openai_key())
        
    async def get_speech_stream(self, text: str, voice_id: str) -> AsyncIterator[bytes]:
        """
        Generate a Text-to-Speech stream using the ElevenLabs API, removing markdown formatting.

        Args:
            text (str): The text to be converted to speech (may contain markdown).
            voice_id (str): The ID of the voice to use.

        Returns:
            AsyncIterator[bytes]: An async iterator of audio bytes.
        """
        # Remove markdown formatting
        clean_text = self.remove_markdown(text)
        
        return self.elevenlabs.text_to_speech.convert(
            voice_id=voice_id,
            optimize_streaming_latency="0",
            output_format="mp3_22050_32",
            text=clean_text,
            model_id="eleven_turbo_v2",
            voice_settings=VoiceSettings(
                stability=0.1,
                similarity_boost=0.3,
                style=0.2
            )
        )
        
    @staticmethod
    def remove_markdown(text: str) -> str:
        """
        Remove markdown formatting from the given text.

        Args:
            text (str): The text containing markdown formatting.

        Returns:
            str: The text with markdown formatting removed.
        """
        # Remove bold and italic
        text = re.sub(r'\*{1,2}(.*?)\*{1,2}', r'\1', text)
        
        # Remove links
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        # Remove headers
        text = re.sub(r'^#{1,6}\s', '', text, flags=re.MULTILINE)
        
        # Remove code blocks
        text = re.sub(r'```[\s\S]*?```', '', text)
        
        # Remove inline code
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        # Remove blockquotes
        text = re.sub(r'^\s*>\s', '', text, flags=re.MULTILINE)
        
        return text.strip()

    async def get_base64_chunk(self, text: str, voice_id: str) -> str:
        """
        Collects all the bytes from the speech stream and returns a base64 encoded string.

        Args:
            text (str): The text to be converted to speech
            voice_id (str): The ID of the voice to use

        Returns:
            str: A base64 encoded string of the audio bytes
        """
        speech_stream = await self.get_speech_stream(text, voice_id)
        audio_bytes = b''
        async for chunk in speech_stream:
            audio_bytes += chunk
        return base64.b64encode(audio_bytes).decode("utf-8")

    async def speech_to_text(self, audio_data_b64: str) -> str:
        """
        Process speech-to-text on audio data coming from the browser.

        Args:
            audio_data_b64 (str): The audio data in base64 format.

        Returns:
            str: The transcribed text from the audio.

        Raises:
            Exception: If there's an error in processing the audio data.
        """
        try:
            audio_data = base64.b64decode(audio_data_b64)
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
                temp_audio_file.write(audio_data)
                temp_audio_file_path = temp_audio_file.name

            # Use the temporary file for transcription
            with open(temp_audio_file_path, "rb") as audio_file:
                result = await self.openai.audio.transcriptions.create(
                    file=audio_file,
                    response_format="text",
                    model="whisper-1",
                )

            # Clean up the temporary file
            os.unlink(temp_audio_file_path)

            return result
        except Exception as e:
            raise Exception(f"Error in speech-to-text processing: {str(e)}")
