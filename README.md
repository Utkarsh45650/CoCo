# COCO — AI Desk Companion

COCO is a modular Python AI companion prototype designed
for children aged 5–8.

## Features

- Groq-hosted conversational AI
- Keyboard input
- Optional microphone input using Vosk
- Local speech generation using Piper
- Temporary in-memory conversation history
- Configurable model paths and behaviour
- Graceful handling of optional audio failures

## Requirements

- Raspberry Pi 4 or compatible Linux computer
- Python 3.10 or newer
- Internet access for Groq API requests
- Groq API key
- Audio output device
- Optional compatible microphone input device

## Setup

1. Create and activate a Python virtual environment.
2. Install requirements.txt.
3. Copy .env.example to .env.
4. Add your Groq API key to .env.
5. Download the Piper voice model.
6. Download and extract the Vosk model.
7. Run the application.

## Start

    source .venv/bin/activate
    python main.py

## Commands

- /help
- /reset
- /quit

## Privacy

Conversation history is kept in memory during the session.
The application does not intentionally persist conversations.
Messages submitted to Groq are processed by a hosted service.

## Safety

This is a prototype. It is not a substitute for adult
supervision, professional advice, or emergency services.