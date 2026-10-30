"""Load and validate environment-based configuration."""
import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    groq_api_key: str
    groq_model: str
    max_history_messages: int
    max_reply_tokens: int
    speaker_voice: str
    speaker_speed: int


def load_config() -> Config:
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key or api_key == "replace_with_your_groq_api_key":
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add your Groq key to the .env file."
        )

    try:
        max_history = int(os.getenv("COCO_MAX_HISTORY_MESSAGES", "12"))
        max_tokens = int(os.getenv("COCO_MAX_REPLY_TOKENS", "260"))
        speed = int(os.getenv("COCO_SPEAKER_SPEED", "155"))
    except ValueError as exc:
        raise RuntimeError(
            "History limit, token limit, and speaker speed must be integers."
        ) from exc

    if max_history < 0 or max_tokens < 1 or not 80 <= speed <= 450:
        raise RuntimeError(
            "Invalid config: history must be >= 0, tokens >= 1, speed 80–450."
        )

    return Config(
        groq_api_key=api_key,
        groq_model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip(),
        max_history_messages=max_history,
        max_reply_tokens=max_tokens,
        speaker_voice=os.getenv("COCO_SPEAKER_VOICE", "en-us+f3").strip(),
        speaker_speed=speed,
    )
