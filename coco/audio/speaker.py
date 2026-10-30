"""Offline text-to-speech using eSpeak NG."""
import shutil
import subprocess


class Speaker:
    def __init__(self, voice: str = "en-us+f3", speed: int = 155) -> None:
        self.voice = voice
        self.speed = speed
        if shutil.which("espeak-ng") is None:
            raise RuntimeError(
                "eSpeak NG is missing. Install it with: sudo apt install espeak-ng"
            )

    def speak(self, text: str) -> None:
        clean_text = " ".join(text.split())
        if not clean_text:
            return
        subprocess.run(
            ["espeak-ng", "-v", self.voice, "-s", str(self.speed), "--stdin"],
            input=clean_text,
            text=True,
            check=True,
            timeout=120,
        )
