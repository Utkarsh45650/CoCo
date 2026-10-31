from __future__ import annotations

import json
import math
import time
from pathlib import Path

import numpy as np
import sounddevice as sd
from vosk import KaldiRecognizer, Model


class Microphone:
    def __init__(
        self,
        model_path: Path,
        sample_rate: int = 16000,
        max_seconds: int = 15,
        end_silence_seconds: float = 1.5,
    ):
        self.model_path = Path(model_path)
        self.sample_rate = sample_rate
        self.max_seconds = max_seconds
        self.end_silence_seconds = end_silence_seconds

        self._model: Model | None = None

    def _load_model(self) -> Model:
        if not self.model_path.is_dir():
            raise FileNotFoundError(
                "Vosk model directory not found: "
                f"{self.model_path}"
            )

        if self._model is None:
            self._model = Model(str(self.model_path))

        return self._model

    @staticmethod
    def list_input_devices() -> list[tuple[int, str]]:
        """Return devices that expose at least one input channel."""
        devices = sd.query_devices()

        inputs = []

        for index, device in enumerate(devices):
            if device["max_input_channels"] > 0:
                inputs.append(
                    (index, device["name"])
                )

        return inputs

    def transcribe(self) -> str:
        model = self._load_model()
        devices = self.list_input_devices()

        if not devices:
            raise RuntimeError(
                "No microphone input device is available. "
                "The Raspberry Pi 4's built-in 3.5 mm jack "
                "does not provide microphone input. Use keyboard "
                "mode or connect a compatible USB microphone "
                "or USB headset sound adapter."
            )

        print("\nAvailable microphone input devices:")

        for index, name in devices:
            print(f"  [{index}] {name}")

        default_input = sd.default.device[0]

        selected = None

        if default_input is not None:
            try:
                default_index = int(default_input)

                if any(
                    index == default_index
                    for index, _ in devices
                ):
                    selected = default_index
            except (TypeError, ValueError):
                pass

        if selected is None:
            selected = devices[0][0]

        # Validate the selected device and its sample rate.
        try:
            sd.check_input_settings(
                device=selected,
                channels=1,
                dtype="int16",
                samplerate=self.sample_rate,
            )
        except Exception as exc:
            raise RuntimeError(
                "The selected microphone does not support "
                f"{self.sample_rate} Hz mono input: {exc}"
            ) from exc

        recognizer = KaldiRecognizer(
            model,
            self.sample_rate,
        )

        block_size = 4000
        started_at = time.monotonic()
        last_voice_at = started_at
        speech_detected = False
        result_text = ""

        print(
            "\nListening now. Speak clearly. "
            "Press Ctrl+C to cancel."
        )

        try:
            with sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=block_size,
                device=selected,
                channels=1,
                dtype="int16",
            ) as stream:

                while True:
                    elapsed = time.monotonic() - started_at

                    if elapsed >= self.max_seconds:
                        break

                    data, overflowed = stream.read(block_size)

                    if overflowed:
                        print(
                            "Warning: audio input overflow occurred."
                        )

                    audio = bytes(data)

                    samples = np.frombuffer(
                        audio,
                        dtype=np.int16,
                    )

                    if samples.size:
                        rms = math.sqrt(
                            float(
                                np.mean(
                                    samples.astype(np.float64) ** 2
                                )
                            )
                        )
                    else:
                        rms = 0.0

                    # Simple energy-based silence detection.
                    # Adjust the threshold for your microphone/noise level.
                    if rms > 450:
                        speech_detected = True
                        last_voice_at = time.monotonic()

                    if recognizer.AcceptWaveform(audio):
                        payload = json.loads(
                            recognizer.Result()
                        )

                        text = payload.get("text", "").strip()

                        if text:
                            result_text = text

                    if (
                        speech_detected
                        and time.monotonic() - last_voice_at
                        >= self.end_silence_seconds
                    ):
                        break

                final_payload = json.loads(
                    recognizer.FinalResult()
                )

                final_text = final_payload.get(
                    "text",
                    "",
                ).strip()

                if final_text:
                    result_text = final_text

        except KeyboardInterrupt:
            print("\nMicrophone input cancelled.")
            return ""

        except Exception as exc:
            raise RuntimeError(
                "Microphone capture or transcription failed: "
                f"{exc}"
            ) from exc

        if not speech_detected:
            print(
                "No speech was detected. "
                "Check the microphone and try again."
            )
            return ""

        return result_text.strip()