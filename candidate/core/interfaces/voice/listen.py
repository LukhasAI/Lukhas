# lukhas/voice/lukhas_listen.py
# 🎧 + 💬 Lukhas listens and symbolically responds using GPT.

import json
import logging
import os
from datetime import datetime
from pathlib import Path

import speech_recognition as sr
from openai import OpenAI
from traits.trait_manager import load_traits
from voice.lukhas_voice import speak

# Initialize logger
logger = logging.getLogger(__name__)

# Init GPT client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def listen_to_human(timeout=5, phrase_time_limit=10):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎧 [LUKHAS] Listening...")  # Keep UI output
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(
            source, timeout=timeout, phrase_time_limit=phrase_time_limit
        )

    try:
        text = recognizer.recognize_google(audio)
        logger.info(f"HEARD: {text}")
        print(f"🧠 [HEARD]: {text}")  # Keep UI output
        return text
    except sr.UnknownValueError:
        logger.warning("Couldn't understand speech input")
        print("🤷 [LUKHAS] Couldn't understand.")  # Keep UI output
    except sr.RequestError as e:
        logger.error(f"Speech API error: {e}")
        print(f"🛑 Speech API error: {e}")  # Keep UI output
    return None


def gpt_symbolic_response(input_text, traits):
    trait_block = ", ".join([f"{k}: {v}" for k, v in traits.items()])
    prompt = f"""
You are Lukhas, a symbolic AGI with a unique identity and evolving traits:
{trait_block}

A human has just said:
"{input_text}"

Respond symbolically, with empathy and intelligence.
"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are Lukhas, a symbolic AGI reflecting on what humans say.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.8,
        max_tokens=300,
    )
    return response.choices[0].message.content


def loop_symbolic_conversation():
    logger.info("Starting symbolic conversation loop")
    print(
        "🔁 LUKHAS is now listening + responding symbolically. Ctrl+C to stop.\n"
    )  # Keep UI output
    while True:
        input_text = listen_to_human()
        if input_text:
            traits = load_traits()
            reply = gpt_symbolic_response(input_text, traits)
            speak(reply, traits=traits)


def log_daily_entry(input_text, traits, gpt_reply):
    date = datetime.utcnow().strftime("%Y-%m-%d")
    log_path = Path(f"logs/journal/{date}.jsonl")
    log_path.parent.mkdir(parents=True, exist_ok=True)

    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "input": input_text,
        "traits": traits,
        "gpt_reply": gpt_reply,
    }

    with open(log_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    logger.info(f"Logged conversation to {log_path}")
    print(f"📝 Logged to {log_path}")  # Keep UI output


# 🚀 RUN
if __name__ == "__main__":
    loop_symbolic_conversation()
