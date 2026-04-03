from pathlib import Path
import os
import sys

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from services.tts_service import TtsService
from services.voice_clone_service import VoiceCloneService


class GenerateSpeechPayload(BaseModel):
    text: str = Field(min_length=1)
    voice_id: str = Field(alias="voiceId")
    speed: float = 1.0
    language: str = "zh"
    output_format: str = Field(default="wav", alias="outputFormat")

    model_config = {
        "populate_by_name": True,
    }


class CloneVoicePayload(BaseModel):
    name: str = Field(min_length=1)
    audio_path: str = Field(alias="audioPath")
    language: str = "zh"

    model_config = {
        "populate_by_name": True,
    }


# PyInstaller 冻结模式下 __file__ 指向临时解压目录，
# 可执行文件本身才是安装目录的入口。
ROOT_DIR = (
    Path(sys.executable).resolve().parent
    if getattr(sys, "frozen", False)
    else Path(__file__).resolve().parent
)
APP_DATA_DIR = ROOT_DIR / "app-data"
OUTPUT_DIR = APP_DATA_DIR / "outputs"
VOICE_DIR = APP_DATA_DIR / "voices"
MODEL_DIR = ROOT_DIR / "models"
BACKEND_PORT = int(os.getenv("AITOREDER_BACKEND_PORT", "8765"))
BACKEND_TOKEN = os.getenv("AITOREDER_BACKEND_TOKEN", "").strip()
ALLOWED_ORIGINS = [
    item.strip()
    for item in os.getenv(
        "AITOREDER_CORS_ORIGINS",
        "http://localhost:1420,http://127.0.0.1:1420,http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if item.strip()
]

for target in (APP_DATA_DIR, OUTPUT_DIR, VOICE_DIR, MODEL_DIR):
    target.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="AI ToReder Python Backend", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/media", StaticFiles(directory=APP_DATA_DIR), name="media")

voice_clone_service = VoiceCloneService(voice_dir=VOICE_DIR, media_prefix="/media/voices/profiles")
tts_service = TtsService(
    output_dir=OUTPUT_DIR,
    media_prefix="/media/outputs",
    profile_dir=VOICE_DIR / "profiles",
)


@app.middleware("http")
async def verify_backend_token(request, call_next):
    if BACKEND_TOKEN:
        request_token = request.headers.get("x-aitoreder-token", "")
        if request_token != BACKEND_TOKEN:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    return await call_next(request)


@app.get("/health")
def health() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "mode": "coqui",
        "model_loaded": tts_service.is_loaded(),
    }


@app.get("/voices")
def list_voices() -> dict[str, list[dict[str, object]]]:
    builtin_voices = voice_clone_service.get_builtin_voices()
    custom_voices = voice_clone_service.get_custom_voices()
    return {
        "builtin_voices": builtin_voices,
        "custom_voices": custom_voices,
    }


@app.post("/generate-speech")
def generate_speech(payload: GenerateSpeechPayload) -> dict[str, object]:
    try:
        result = tts_service.generate(
            text=payload.text,
            voice_id=payload.voice_id,
            speed=payload.speed,
            language=payload.language,
            output_format=payload.output_format,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return result


@app.post("/clone-voice")
def clone_voice(payload: CloneVoicePayload) -> dict[str, str]:
    reference = Path(payload.audio_path)
    if not reference.exists():
        raise HTTPException(status_code=400, detail="参考音频不存在。")

    return voice_clone_service.create_profile(
        name=payload.name,
        audio_path=reference,
        language=payload.language,
    )


@app.delete("/voices/{voice_profile_id}")
def delete_voice_profile(voice_profile_id: str) -> dict[str, str]:
    deleted = voice_clone_service.delete_profile(voice_profile_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="profile 不存在。")

    return {"status": "deleted", "voiceProfileId": voice_profile_id}


if __name__ == "__main__":
    import uvicorn

    # 冻结模式下无法用字符串 "app:app" 动态导入，直接传 app 对象
    _app_target = app if getattr(sys, "frozen", False) else "app:app"
    uvicorn.run(_app_target, host="127.0.0.1", port=BACKEND_PORT, reload=False)
