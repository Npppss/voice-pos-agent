"""
Speech-to-Text service — interfaces with Whisper ASR.
"""

import base64
import httpx

from config import settings


async def transcribe_audio(audio_base64: str) -> str | None:
    """
    Send audio data to the Whisper STT service and return transcribed text.

    Args:
        audio_base64: Base64-encoded audio data (PCM 16-bit, 16kHz, mono)

    Returns:
        Transcribed text string, or None if transcription failed.
    """
    try:
        audio_bytes = base64.b64decode(audio_base64)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.STT_SERVICE_URL}/asr",
                files={"audio_file": ("audio.wav", audio_bytes, "audio/wav")},
                params={
                    "task": "transcribe",
                    "language": "id",  # Bahasa Indonesia
                    "output": "json",
                },
            )
            response.raise_for_status()
            result = response.json()
            return result.get("text", "").strip()

    except httpx.HTTPError as e:
        print(f"STT service error: {e}")
        return None
    except Exception as e:
        print(f"STT transcription failed: {e}")
        return None
