import math
import struct
import time
import wave
from pathlib import Path


class TtsService:
    def __init__(self, output_dir: Path, media_prefix: str) -> None:
        self.output_dir = output_dir
        self.media_prefix = media_prefix.rstrip("/")

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
        duration_seconds = min(max(len(text) / 12.0, 1.2), 8.0)
        self._write_preview_wave(file_path, duration_seconds=duration_seconds, voice_id=voice_id, speed=speed)

        return {
            "task_id": task_id,
            "status": "success",
            "audio_path": f"{self.media_prefix}/{file_path.name}",
            "duration_ms": int(duration_seconds * 1000),
            "language": language,
        }

    def _write_preview_wave(self, file_path: Path, *, duration_seconds: float, voice_id: str, speed: float) -> None:
        sample_rate = 22050
        amplitude = 16000
        frequency_map = {
            "female_01": 440.0,
            "female_02": 493.88,
            "male_01": 220.0,
            "male_02": 246.94,
            "narrator_01": 329.63,
        }
        base_frequency = frequency_map.get(voice_id, 329.63)
        frequency = base_frequency * max(speed, 0.5)
        total_frames = int(sample_rate * duration_seconds)

        with wave.open(str(file_path), "w") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)

            for frame in range(total_frames):
                t = frame / sample_rate
                envelope = min(1.0, frame / 1200) * min(1.0, (total_frames - frame) / 1600)
                sample = amplitude * envelope * math.sin(2 * math.pi * frequency * t)
                wav_file.writeframesraw(struct.pack("<h", int(sample)))
