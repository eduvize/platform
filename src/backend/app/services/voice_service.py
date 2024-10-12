import base64
from typing import AsyncIterator
from elevenlabs import AsyncElevenLabs, VoiceSettings
from config import get_elevenlabs_api_key

class VoiceService:
    elevenlabs: AsyncElevenLabs
    
    def __init__(self):
        self.elevenlabs = AsyncElevenLabs(api_key=get_elevenlabs_api_key())

    async def get_speech_stream(self, text: str, voice_id: str) -> AsyncIterator[bytes]:
        """
        Generate a Text-to-Speech URL using the ElevenLabs API.

        Args:
            text (str): The text to be converted to speech.
            voice_id (str, optional): The ID of the voice to use. Defaults to a specific voice ID.

        Returns:
            str: The URL of the generated audio file.

        Raises:
            Exception: If there's an error in generating the TTS URL.
        """
        
        return self.elevenlabs.text_to_speech.convert(
            voice_id=voice_id,
            optimize_streaming_latency="0",
            output_format="mp3_22050_32",
            text=text,
            model_id="eleven_turbo_v2",
            voice_settings=VoiceSettings(
                stability=0.1,
                similarity_boost=0.3,
                style=0.2
            )
        )
        
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
