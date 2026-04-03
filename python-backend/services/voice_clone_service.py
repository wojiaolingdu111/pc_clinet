import json
import shutil
import time
from pathlib import Path


class VoiceCloneService:
    def __init__(self, voice_dir: Path, media_prefix: str) -> None:
        self.voice_dir = voice_dir
        self.profile_dir = self.voice_dir / "profiles"
        self.media_prefix = media_prefix.rstrip("/")
        self.profile_dir.mkdir(parents=True, exist_ok=True)

    def get_builtin_voices(self) -> list[dict[str, object]]:
        return [
            {
                "id": "female_01",
                "name": "温柔女声",
                "type": "builtin",
                "language": ["zh"],
                "description": "适合客服、旁白和引导音。",
                "preview_audio": None,
            },
            {
                "id": "female_02",
                "name": "明亮女声",
                "type": "builtin",
                "language": ["zh"],
                "description": "适合短视频和内容播报。",
                "preview_audio": None,
            },
            {
                "id": "male_01",
                "name": "沉稳男声",
                "type": "builtin",
                "language": ["zh"],
                "description": "适合解说和资讯播报。",
                "preview_audio": None,
            },
            {
                "id": "male_02",
                "name": "清晰男声",
                "type": "builtin",
                "language": ["zh"],
                "description": "适合教程和产品介绍。",
                "preview_audio": None,
            },
            {
                "id": "narrator_01",
                "name": "中性旁白",
                "type": "builtin",
                "language": ["zh", "en"],
                "description": "适合故事和说明文案。",
                "preview_audio": None,
            },
        ]

    def get_custom_voices(self) -> list[dict[str, object]]:
        profiles: list[dict[str, object]] = []
        for meta_file in sorted(self.profile_dir.glob("*.json")):
            profiles.append(json.loads(meta_file.read_text(encoding="utf-8")))
        return profiles

    def create_profile(self, *, name: str, audio_path: Path, language: str) -> dict[str, str]:
        voice_profile_id = f"voice-user-{int(time.time() * 1000)}"
        target_audio = self.profile_dir / f"{voice_profile_id}{audio_path.suffix.lower() or '.wav'}"
        shutil.copy2(audio_path, target_audio)

        metadata = {
            "id": voice_profile_id,
            "name": name,
            "type": "custom",
            "language": [language],
            "description": f"参考音频：{audio_path.name}",
            "preview_audio": f"{self.media_prefix}/{target_audio.name}",
            "local_audio_path": str(target_audio.resolve()),
        }
        (self.profile_dir / f"{voice_profile_id}.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return {
            "voice_profile_id": voice_profile_id,
            "status": "success",
        }

    def delete_profile(self, voice_profile_id: str) -> bool:
        meta_path = self.profile_dir / f"{voice_profile_id}.json"
        if not meta_path.exists():
            return False

        metadata = json.loads(meta_path.read_text(encoding="utf-8"))
        preview_audio = metadata.get("preview_audio")
        if preview_audio:
            preview_name = str(preview_audio).rstrip("/").split("/")[-1]
            preview_path = self.profile_dir / preview_name
            if preview_path.exists():
                preview_path.unlink()

        meta_path.unlink()
        return True
