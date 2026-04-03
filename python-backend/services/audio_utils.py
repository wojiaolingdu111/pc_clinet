from pathlib import Path


def normalize_audio(input_path: Path, output_path: Path) -> Path:
    output_path.write_bytes(input_path.read_bytes())
    return output_path
