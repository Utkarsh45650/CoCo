from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


class Speaker:
    """
    Generates speech with Piper and plays it using ALSA.

    If speech generation or playback fails, the caller can
    still display the AI response as text.
    """

    def __init__(
        self,
        model_path: Path,
        enabled: bool = True,
    ):
        self.model_path = Path(model_path)
        self.enabled = enabled

    def check_ready(self) -> None:
        if not self.enabled:
            return

        if not self.model_path.is_file():
            raise FileNotFoundError(
                f"Piper model not found: {self.model_path}"
            )

        if not Path(
            str(self.model_path) + ".json"
        ).is_file():
            raise FileNotFoundError(
                "Piper model configuration is missing: "
                f"{self.model_path}.json"
            )

        if shutil.which("aplay") is None:
            raise RuntimeError(
                "'aplay' is unavailable. Install alsa-utils."
            )

    def speak(self, text: str) -> None:
        if not self.enabled:
            return

        text = text.strip()

        if not text:
            return

        self.check_ready()

        # Use a temporary file so playback begins after synthesis.
        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            prefix="coco_",
            delete=False,
        ) as temp_file:
            wav_path = Path(temp_file.name)

        try:
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "piper",
                    "-m",
                    str(self.model_path),
                    "-f",
                    str(wav_path),
                    "--",
                    text,
                ],
                check=True,
                timeout=90,
                capture_output=True,
                text=True,
            )

            subprocess.run(
                [
                    "aplay",
                    "-q",
                    str(wav_path),
                ],
                check=True,
                timeout=120,
                capture_output=True,
                text=True,
            )

        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                "Speech generation or playback timed out."
            ) from exc

        except subprocess.CalledProcessError as exc:
            details = (exc.stderr or "").strip()

            raise RuntimeError(
                "Piper or audio playback failed. "
                f"Details: {details or exc}"
            ) from exc

        finally:
            wav_path.unlink(missing_ok=True)