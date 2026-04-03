import json
import logging
import threading
import time
from pathlib import Path

logger = logging.getLogger(__name__)

# XTTS v2 支持的语言代码映射（用户侧语言 → XTTS 语言标识）
LANGUAGE_MAP: dict[str, str] = {
    "zh": "zh-cn",
    "en": "en",
    "ja": "ja",
    "ko": "ko",
    "fr": "fr",
    "de": "de",
    "es": "es",
}

# 内置声音 ID → XTTS v2 预训练说话人名（英文名，合成语言以 language 参数为准）
BUILTIN_SPEAKERS: dict[str, str] = {
    "female_01": "Claribel Dervla",
    "female_02": "Daisy Studious",
    "male_01": "Damien Black",
    "male_02": "Aaron Dreschner",
    "narrator_01": "Maja Ruoho",
}

DEFAULT_SPEAKER = "Claribel Dervla"
MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"


class TtsService:
    def __init__(self, output_dir: Path, media_prefix: str, profile_dir: Path | None = None) -> None:
        self.output_dir = output_dir
        self.media_prefix = media_prefix.rstrip("/")
        self.profile_dir = profile_dir
        self._tts = None
        self._lock = threading.Lock()
        self._load_error: str | None = None

    def is_loaded(self) -> bool:
        return self._tts is not None

    def _get_tts(self):
        """懒加载 XTTS v2 模型，线程安全；首次调用会触发模型下载（约 2 GB）。"""
        if self._tts is not None:
            return self._tts
        if self._load_error:
            raise RuntimeError(f"TTS 引擎加载失败（上次错误）：{self._load_error}")
        with self._lock:
            if self._tts is not None:
                return self._tts
            try:
                from TTS.api import TTS as CoquiTTS  # noqa: PLC0415
                logger.info("正在加载 XTTS v2 模型（首次使用会自动下载约 2 GB，请耐心等待）…")
                self._tts = CoquiTTS(model_name=MODEL_NAME, progress_bar=True)
                logger.info("XTTS v2 模型加载完成。")
                return self._tts
            except ImportError as exc:
                self._load_error = (
                    "未安装 coqui-tts，请在 python-backend 目录下运行：pip install -r requirements.txt"
                )
                logger.error(self._load_error)
                raise RuntimeError(self._load_error) from exc
            except Exception as exc:
                self._load_error = str(exc)
                logger.exception("加载 XTTS v2 模型时出错")
                raise

    def _get_reference_audio(self, voice_id: str) -> str | None:
        """从 Profile JSON 的 local_audio_path 字段读取参考音频本地绝对路径。"""
        if self.profile_dir is None:
            return None
        meta_path = self.profile_dir / f"{voice_id}.json"
        if not meta_path.exists():
            return None
        try:
            metadata = json.loads(meta_path.read_text(encoding="utf-8"))
            return metadata.get("local_audio_path")
        except Exception:
            return None

    def generate(
        self,
        *,
        text: str,
        voice_id: str,
        speed: float,
        language: str,
        output_format: str,
    ) -> dict[str, object]:
        if output_format != "wav":
            raise ValueError("当前仅支持 wav 输出。")

        task_id = f"tts-{int(time.time() * 1000)}"
        file_path = self.output_dir / f"{task_id}.wav"
        start_time = time.time()

        try:
            tts = self._get_tts()
        except Exception as exc:
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(exc),
                "duration_ms": 0,
            }

        lang_code = LANGUAGE_MAP.get(language, "zh-cn")

        try:
            reference_audio = self._get_reference_audio(voice_id)
            if reference_audio and Path(reference_audio).exists():
                # 声音克隆模式：以用户提供的参考音频为条件
                logger.info("声音克隆合成：voice_id=%s, lang=%s", voice_id, lang_code)
                tts.tts_to_file(
                    text=text,
                    speaker_wav=reference_audio,
                    language=lang_code,
                    file_path=str(file_path),
                    speed=speed,
                )
            else:
                # 内置说话人模式
                speaker = BUILTIN_SPEAKERS.get(voice_id, DEFAULT_SPEAKER)
                logger.info("内置说话人合成：speaker=%s, lang=%s", speaker, lang_code)
                tts.tts_to_file(
                    text=text,
                    speaker=speaker,
                    language=lang_code,
                    file_path=str(file_path),
                    speed=speed,
                )
        except Exception as exc:
            logger.exception("TTS 合成失败")
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(exc),
                "duration_ms": int((time.time() - start_time) * 1000),
            }

        return {
            "task_id": task_id,
            "status": "success",
            "audio_path": f"{self.media_prefix}/{file_path.name}",
            "duration_ms": int((time.time() - start_time) * 1000),
            "language": language,
        }
