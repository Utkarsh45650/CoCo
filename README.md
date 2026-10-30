# COCO — Minimal Groq Voice Prototype

This project has no database, web server, microphone, wake-word detector, or optional services. It accepts typed input in the terminal, sends conversation to Groq, and speaks responses locally through eSpeak NG.

## Structure

```text
coco_minimal/
├── .env.example
├── .gitignore
├── requirements.txt
├── main.py
└── coco/
    ├── __init__.py
    ├── config.py
    ├── ai/
    │   ├── __init__.py
    │   └── groq_client.py
    └── audio/
        ├── __init__.py
        └── speaker.py
```

## Install system dependencies

```bash
sudo apt update
sudo apt install -y python3-venv espeak-ng alsa-utils
```

## Python environment

Run from the project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Configure Groq

Create an API key at https://console.groq.com/keys, then:

```bash
cp .env.example .env
nano .env
```

Replace the placeholder value for `GROQ_API_KEY`. Never commit or share `.env`.

Default model: `llama-3.3-70b-versatile`. Model availability may change; if Groq reports the model is unavailable or decommissioned, select a currently available chat model in Groq Console and update `GROQ_MODEL`.

## Check audio

Connect your headset to the Raspberry Pi itself. SSH does not automatically route Pi audio to the laptop.

```bash
wpctl status
espeak-ng "Hello, this is COCO. The speaker is working."
```

If needed, set the headset as default using its actual sink ID from `wpctl status`:

```bash
wpctl set-default DEVICE_ID
wpctl set-volume @DEFAULT_AUDIO_SINK@ 0.55
```

## Run

```bash
python main.py
```

Type a message and press Enter. Commands: `/reset` clears in-memory conversation history; `/quit` exits.

No chat history is written to disk. The app sends the typed message, the system prompt, and limited in-memory conversation context to Groq. Do not enter real children's personal or sensitive information in this prototype.

## Troubleshooting

- Missing key: check `.env` is in the project root.
- API error: verify API key, internet connectivity, and model availability in Groq Console.
- Missing speech: install `espeak-ng` and run the audio test.
- No headset sound: ensure headset is connected to the Pi and inspect `wpctl status`.
