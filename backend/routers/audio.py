"""
WebSocket endpoint for real-time audio streaming and STT processing.
"""

import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from services.stt_service import transcribe_audio
from services.ai_agent import process_transcription

router = APIRouter()


@router.websocket("/audio/stream")
async def audio_stream(websocket: WebSocket):
    """
    WebSocket endpoint for streaming audio from the mobile app.

    Flow:
    1. Client connects and sends audio chunks as binary or base64 JSON
    2. Audio is forwarded to STT engine for transcription
    3. Transcribed text is processed by AI Agent
    4. Resolved order items are sent back to client
    """
    await websocket.accept()
    session_id = None

    try:
        while True:
            raw = await websocket.receive_text()
            message = json.loads(raw)

            msg_type = message.get("type")
            session_id = message.get("session_id", session_id)

            if msg_type == "audio_chunk":
                audio_data = message.get("data", "")

                # Step 1: Transcribe audio
                transcription = await transcribe_audio(audio_data)

                if transcription:
                    # Send partial transcription to client
                    await websocket.send_json({
                        "type": "transcription_partial",
                        "text": transcription,
                        "is_final": False,
                    })

            elif msg_type == "end_stream":
                # Step 2: Process full transcription through AI Agent
                final_text = message.get("final_text", "")
                order_result = await process_transcription(
                    text=final_text,
                    session_id=session_id,
                )

                await websocket.send_json({
                    "type": "order_resolved",
                    "order": order_result,
                })

    except WebSocketDisconnect:
        print(f"Session {session_id} disconnected")
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "code": "STREAM_ERROR",
            "message": str(e),
        })
