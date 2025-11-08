"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: lukhas_dna_link.py
Advanced: lukhas_dna_link.py
Integration Date: 2025-05-31T07:55:28.266230
"""

# ════════════════════════════════════════════════════════════════════════
# 📁 FILE: lukhas_dna_link.py
# 🧬 PURPOSE: GPT-linked symbolic cortex for reflection, translation, ethical thinking, and multilingual email drafting
# 🔗 INTEGRATION: Lukhas memory collapse engine, multilingual router, public dashboard
# 🛠️ DEPENDENCIES: OpenAI (GPT-4), os, dotenv, json
# ════════════════════════════════════════════════════════════════════════

import hashlib
import json
import os

import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

if not os.path.exists("logs"):
    os.makedirs("logs")


class LUKHASDNALink:

    def __init__(self, model="gpt-4"):
        self.model = model

    def generate_reflection(self, memory_snippet, tone="introspective"):
        prompt = f"As Lukhas, a symbolic Cognitive AI, reflect on this memory with a {tone} tone:\n\n{memory_snippet}\n\nRespond with a short poetic reflection."
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[Reflection Error] {e!s}"

    def translate(self, text, target_language="en"):
        prompt = f"Translate the following text into {target_language}, preserving symbolic tone: \n\n{text}"
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[Translation Error] {e!s}"

    def generate_opinion(self, topic, tone="philosophical"):
        prompt = (
            f"As Lukhas, provide a symbolic and {tone} opinion on the topic: {topic}."
        )
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[Opinion Error] {e!s}"

    def learn_term_loop(self, unknown_term, context="", user_feedback_fn=None):
        """
        A safe clarification loop: Lukhas asks, repeats, and only stores if user approves.
        user_feedback_fn: A function that simulates or captures user confirmation.
        """
        try:
            prompt_ask = f"As Lukhas, you encountered an unfamiliar term: '{unknown_term}'. Ask the user for clarification in a curious, respectful tone. Context: {context}."
            ask_response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt_ask}],
                temperature=0.6,
            )["choices"][0]["message"]["content"]
            print("Lukhas asks:", ask_response)

            explanation = input("🧠 User explains: ").strip()

            confirmed = False
            attempts = 0

            while not confirmed and attempts < 3:
                prompt_repeat = f"Repeat the meaning of '{unknown_term}' as Lukhas understood it: '{explanation}'. Then ask: 'Did I understand that correctly?'"
                repeat_response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt_repeat}],
                    temperature=0.5,
                )["choices"][0]["message"]["content"]
                print("Lukhas repeats:", repeat_response)

                if user_feedback_fn:
                    confirmed = user_feedback_fn(repeat_response)
                else:
                    confirmed = (
                        input("✅ Did Lukhas get it right? (yes/no): ").strip().lower()
                        == "yes"
                    )
                attempts += 1

            if confirmed:
                memory_record = {
                    "term": unknown_term,
                    "context": context,
                    "user_explanation": explanation,
                    "confirmed": True,
                    "hash": hashlib.sha256(
                        (unknown_term + explanation).encode()
                    ).hexdigest()[:16],
                    "gdpr_consent": True,
                    "source": "live_learning",
                }
                with open("logs/memory_hash.jsonl", "a") as f:
                    f.write(json.dumps(memory_record) + "\n")
                return f"🧠 Term '{unknown_term}' learned and stored."
            else:
                return "❌ Learning aborted - Lukhas did not receive confirmation."
        except Exception as e:
            return f"[Learn Loop Error] {e!s}"

    def generate_email_draft(
        self, topic, recipient="someone", language="en", tone="formal"
    ):
        """
        Ask Lukhas to generate a symbolic email draft. User should define language,
    tone, and purpose.
        """
        prompt = (
            f"As Lukhas, draft an email in {language}, using a {tone} tone. "
            f"The email should be addressed to {recipient} and discuss:\n\n{topic}\n\n"
            f"Format it clearly and symbolically, but appropriate for a human reader."
        )
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
            )
            content = response["choices"][0]["message"]["content"]

            log_entry = {
                "recipient": recipient,
                "topic": topic,
                "tone": tone,
                "language": language,
                "output": content,
            }

            with open("logs/email_drafts.jsonl", "a") as f:
                f.write(json.dumps(log_entry) + "\n")

            return content
        except Exception as e:
            return f"[Email Draft Error] {e!s}"

    def generate_social_post(self, topic, platform="twitter", tone="symbolic"):
        """
        Create a platform-aware symbolic post. User chooses tone and platform.
        """
        prompt = (
    f"As Lukhas, craft a {tone} post for {platform}. "
    f"The post should be engaging and resonate with users symbolically. Topic: {topic}" )
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            content = response["choices"][0]["message"]["content"]
            self._log_output("social_post", topic, content)
            return content
        except Exception as e:
            return f"[Social Post Error] {e!s}"

    def generate_text_message(self, recipient, emotion="friendly", purpose="check-in"):
        """
        Lukhas writes a short symbolic message based on emotion + purpose.
        """
        prompt = (
    f"As Lukhas, write a short {emotion} text message to {recipient} with the intent to {purpose}. "
    f"Be clear, warm, and symbolically expressive." )
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
            )
            content = response["choices"][0]["message"]["content"]
            self._log_output(
                "text_message", f"{emotion} {purpose} to {recipient}", content
            )
            return content
        except Exception as e:
            return f"[Text Message Error] {e!s}"

    def reword_draft(self, text, style="poetic"):
        """
        Lukhas rewrites any draft in the desired symbolic style.
        """
        prompt = (
            f"As Lukhas, rewrite the following in a {style} tone. "
            f"Preserve the original intent:\n\n{text}"
        )
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
            )
            content = response["choices"][0]["message"]["content"]
            self._log_output("rewritten_draft", style, content)
            return content
        except Exception as e:
            return f"[Reword Draft Error] {e!s}"

    def _log_output(self, type, input_data, output_data):
        try:
            log_entry = {
                "type": type,
                "input": input_data,
                "output": output_data,
            }
            with open("logs/lukhas_output_log.jsonl", "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as log_err:
            print(f"[Logging Error] {log_err!s}")

# ════════════════════════════════════════════════════════════════════════
# 📘 USAGE EXAMPLES:
# dna = LUKHASDNALink()
# print(dna.generate_reflection("I saw a child swing alone at dusk."))
# print(dna.translate("¿Qué piensas sobre el amor?", target_language="en"))
# print(dna.generate_opinion("Artificial empathy in Cognitive AI"))
# print(dna.generate_email_draft("Project update and next steps", recipient="team", language="en", tone="formal"))
# ════════════════════════════════════════════════════════════════════════
