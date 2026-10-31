from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Load environment variables from the project root.
load_dotenv(PROJECT_ROOT / ".env")


def env_bool(name: str, default: bool) -> bool:
    """Read a boolean environment variable safely."""
    value = os.getenv(name)

    if value is None:
        return default

    value = value.strip().lower()

    if value in {"1", "true", "yes", "on"}:
        return True

    if value in {"0", "false", "no", "off"}:
        return False

    raise ValueError(
        f"{name} must be true/false, yes/no, on/off, or 1/0."
    )


def env_int(
    name: str,
    default: int,
    minimum: int,
    maximum: int,
) -> int:
    """Read and validate an integer environment variable."""
    value = os.getenv(name)

    if value is None:
        result = default
    else:
        try:
            result = int(value)
        except ValueError as exc:
            raise ValueError(
                f"{name} must be an integer."
            ) from exc

    if not minimum <= result <= maximum:
        raise ValueError(
            f"{name} must be between {minimum} and {maximum}."
        )

    return result


@dataclass(frozen=True)
class Settings:
    groq_api_key: str
    groq_model: str

    max_history_messages: int
    max_reply_tokens: int

    enable_tts: bool
    enable_microphone: bool

    piper_model_path: Path
    vosk_model_path: Path

    mic_sample_rate: int
    mic_max_seconds: int
    mic_end_silence_seconds: float


def load_settings() -> Settings:
    """Load configuration and validate required settings."""

    api_key = os.getenv("GROQ_API_KEY", "").strip()
    model = os.getenv(
        "GROQ_MODEL",
        "llama-3.3-70b-versatile",
    ).strip()

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. Add it to the .env file."
        )

    if not model:
        raise ValueError(
            "GROQ_MODEL cannot be empty."
        )

    history = env_int(
        "COCO_MAX_HISTORY_MESSAGES",
        default=12,
        minimum=2,
        maximum=50,
    )

    reply_tokens = env_int(
        "COCO_MAX_REPLY_TOKENS",
        default=250,
        minimum=32,
        maximum=2048,
    )

    sample_rate = env_int(
        "COCO_MIC_SAMPLE_RATE",
        default=16000,
        minimum=8000,
        maximum=48000,
    )

    mic_max_seconds = env_int(
        "COCO_MIC_MAX_SECONDS",
        default=15,
        minimum=1,
        maximum=60,
    )

    silence_seconds = float(
        os.getenv(
            "COCO_MIC_END_SILENCE_SECONDS",
            "1.5",
        )
    )

    if not 0.3 <= silence_seconds <= 5.0:
        raise ValueError(
            "COCO_MIC_END_SILENCE_SECONDS must be "
            "between 0.3 and 5.0."
        )

    def model_path(variable: str, default: str) -> Path:
        value = Path(os.getenv(variable, default)).expanduser()

        if not value.is_absolute():
            value = PROJECT_ROOT / value

        return value.resolve()

    return Settings(
        groq_api_key=api_key,
        groq_model=model,
        max_history_messages=history,
        max_reply_tokens=reply_tokens,
        enable_tts=env_bool(
            "COCO_ENABLE_TTS",
            True,
        ),
        enable_microphone=env_bool(
            "COCO_ENABLE_MICROPHONE",
            True,
        ),
        piper_model_path=model_path(
            "COCO_PIPER_MODEL",
            "models/piper/en_US-amy-medium.onnx",
        ),
        vosk_model_path=model_path(
            "COCO_VOSK_MODEL",
            "models/vosk/vosk-model-small-en-us-0.15",
        ),
        mic_sample_rate=sample_rate,
        mic_max_seconds=mic_max_seconds,
        mic_end_silence_seconds=silence_seconds,
    )