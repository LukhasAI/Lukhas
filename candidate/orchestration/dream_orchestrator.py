import json
import os
import sys
import time
from queue import Queue
from threading import Thread

from openai import OpenAI

# --- Caching ---
CACHE_DIR = "candidate/orchestration/.cache"
os.makedirs(CACHE_DIR, exist_ok=True)


def get_cache_path(seed: str) -> str:
    import hashlib

    seed_hash = hashlib.md5(seed.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{seed_hash}.json")


def read_from_cache(seed: str) -> dict | None:
    cache_path = get_cache_path(seed)
    if os.path.exists(cache_path):
        try:
            with open(cache_path) as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return None
    return None


def write_to_cache(seed: str, data: dict):
    cache_path = get_cache_path(seed)
    try:
        with open(cache_path, "w") as f:
            json.dump(data, f)
    except OSError:
        pass  # Fail silently if cache write fails


# --- End Caching ---


class DreamOrchestrator:
    """
    Orchestrates the creation and persistence of multi-sensory "dreams".
    """

    def __init__(self):
        self.memory_log_path = "candidate/memory/dream_log.jsonl"
        try:
            self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            # A bit of welcome feedback for the Node.js process
            print("DreamOrchestrator initialized with OpenAI client.", file=sys.stderr)
        except Exception as e:
            print(f"Error initializing OpenAI client: {e}", file=sys.stderr)
            self.openai_client = None

    def _simulate_lukhas_memory_query(self, seed: str) -> list[str]:
        print(f"Simulating LUKHAS memory query for: {seed}", file=sys.stderr)
        if "star" in seed.lower():
            return ["celestial", "solitude", "light", "navigation"]
        if "city" in seed.lower():
            return ["structure", "society", "networks", "future"]
        return ["creation", "thought", "abstract"]

    def _simulate_lukhas_guardian_check(self, text: str) -> bool:
        print("Simulating LUKHAS guardian check for text.", file=sys.stderr)
        return "unsafe" not in text.lower()

    def _get_dream_manifest_from_gpt(self, seed: str, concepts: list[str]) -> dict:
        print("Generating Dream Manifest with GPT-4...", file=sys.stderr)
        if not self.openai_client:
            raise Exception("OpenAI client not initialized.")

        system_prompt = """
        You are a dream architect for the LUKHAS AI. Your purpose is to translate a user's "dream seed" into a structured JSON object called a "Dream Manifest". This manifest will be used to generate a multi-sensory, abstract, 3D visual experience. You must respond ONLY with a valid JSON object.

        The JSON object must have two top-level keys: "narrative" and "visuals".
        1.  "narrative": A short, poetic, dream-like sentence (max 25 words).
        2.  "visuals": An object with these keys:
            - "geometry": (string) Choose one: "sphere", "torus", "icosahedron", "cone", "box".
            - "movement": (string) Choose one: "gentle rotation", "pulsating", "drifting".
            - "colors": (array of 3 strings) Provide 3 hex color codes. The first is the background, the others are for the object/lights.
            - "particle_count": (integer) A number between 500 and 8000.
        """
        user_prompt = (
            f'Dream Seed: "{seed}"\nRelated LUKHAS Concepts: {", ".join(concepts)}'
        )

        response = self.openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)

    def _get_texture_url_from_dalle(self, narrative: str, result_queue: Queue):
        print("Generating texture with DALL-E 3...", file=sys.stderr)
        try:
            if not self.openai_client:
                raise Exception("OpenAI client not initialized.")
            prompt = f"An abstract, dreamlike, seamless texture representing the feeling of: '{narrative}'"
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size="1024x1024",
                quality="standard",
            )
            result_queue.put(("texture", response.data[0].url))
        except Exception as e:
            result_queue.put(("texture", e))

    def _get_audio_url_from_tts(self, narrative: str, result_queue: Queue):
        print("Generating audio with TTS...", file=sys.stderr)
        try:
            if not self.openai_client:
                raise Exception("OpenAI client not initialized.")
            response = self.openai_client.audio.speech.create(
                model="tts-1", voice="nova", input=narrative
            )
            audio_filename = f"dream_{int(time.time())}.mp3"
            audio_filepath = os.path.join(
                "lukhas_website", "public", "audio", audio_filename
            )
            os.makedirs(os.path.dirname(audio_filepath), exist_ok=True)
            response.stream_to_file(audio_filepath)
            result_queue.put(("audio", f"/audio/{audio_filename}"))
        except Exception as e:
            result_queue.put(("audio", e))

    def weave_dream(self, dream_seed: str) -> dict:
        print(f"Weaving a new dream for seed: '{dream_seed}'", file=sys.stderr)

        cached_manifest = read_from_cache(dream_seed)
        if cached_manifest:
            print("Found cached manifest.", file=sys.stderr)
            return cached_manifest

        concepts = self._simulate_lukhas_memory_query(dream_seed)
        manifest_core = self._get_dream_manifest_from_gpt(dream_seed, concepts)
        if not self._simulate_lukhas_guardian_check(manifest_core["narrative"]):
            raise Exception("Guardian check failed for generated narrative.")

        result_queue = Queue()
        texture_thread = Thread(
            target=self._get_texture_url_from_dalle,
            args=(manifest_core["narrative"], result_queue),
        )
        audio_thread = Thread(
            target=self._get_audio_url_from_tts,
            args=(manifest_core["narrative"], result_queue),
        )

        texture_thread.start()
        audio_thread.start()

        results = {}
        for _ in range(2):
            key, value = result_queue.get()
            if isinstance(value, Exception):
                raise value
            results[key] = value

        texture_thread.join()
        audio_thread.join()

        final_manifest = {
            "narrative": manifest_core["narrative"],
            "visuals": manifest_core["visuals"],
            "audio_url": results["audio"],
            "texture_url": results["texture"],
            "dream_id": f"dream_real_{int(time.time())}",
        }

        write_to_cache(dream_seed, final_manifest)
        print("Dream manifest generated successfully.", file=sys.stderr)
        return final_manifest

    def store_dream(self, manifest: dict) -> str:
        memory_id = f"mem_{int(time.time())}"
        print(
            f"Storing dream {manifest.get('dream_id')} with memory ID {memory_id}",
            file=sys.stderr,
        )
        try:
            with open(self.memory_log_path, "a") as f:
                manifest_to_store = {
                    **manifest,
                    "memory_id": memory_id,
                    "stored_at": time.time(),
                }
                f.write(json.dumps(manifest_to_store) + "\n")
            print(
                f"Successfully stored dream {manifest.get('dream_id')}.",
                file=sys.stderr,
            )
            return memory_id
        except Exception as e:
            print(f"Error storing dream: {e}", file=sys.stderr)
            raise


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Dream Weaver Orchestrator")
    parser.add_argument(
        "--store",
        action="store_true",
        help="Store a dream manifest instead of weaving a new one.",
    )
    args = parser.parse_args()

    orchestrator = DreamOrchestrator()

    try:
        if args.store:
            manifest_data = json.load(sys.stdin)
            memory_id = orchestrator.store_dream(manifest_data)
            print(json.dumps({"success": True, "memoryId": memory_id}))
        else:
            dream_seed_input = sys.stdin.readline().strip()
            if not dream_seed_input:
                dream_seed_input = "a test dream for direct execution"
            dream_manifest = orchestrator.weave_dream(dream_seed_input)
            print(json.dumps(dream_manifest))
    except Exception as e:
        print(f"An error occurred in the orchestrator: {e}", file=sys.stderr)
        sys.exit(1)
