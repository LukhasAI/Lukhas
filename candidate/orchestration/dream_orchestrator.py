import json
import time
import os
from openai import OpenAI

# Placeholder for actual LUKHAS module imports
# from lukhas.memory.service import MemoryService
# from lukhas.guardian.service import GuardianService

class DreamOrchestrator:
    """
    Orchestrates the creation and persistence of multi-sensory "dreams".
    """

    def __init__(self):
        # In a real implementation, these would be connections to services.
        self.memory_log_path = "candidate/memory/dream_log.jsonl"
        try:
            self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            print("DreamOrchestrator initialized with OpenAI client.")
        except Exception as e:
            print(f"Error initializing OpenAI client: {e}", file=sys.stderr)
            self.openai_client = None

    def _simulate_lukhas_memory_query(self, seed: str) -> list[str]:
        """Simulates querying the LUKHAS memory for related concepts."""
        print(f"Simulating LUKHAS memory query for: {seed}")
        # In a real system, this would involve vector embeddings.
        if "star" in seed.lower():
            return ["celestial", "solitude", "light", "navigation"]
        if "city" in seed.lower():
            return ["structure", "society", "networks", "future"]
        return ["creation", "thought", "abstract"]

    def _simulate_lukhas_guardian_check(self, text: str) -> bool:
        """Simulates the LUKHAS guardian safety check."""
        print("Simulating LUKHAS guardian check for text.")
        # A real system would have a sophisticated safety model.
        if "unsafe" in text.lower():
            return False
        return True

    def _get_dream_manifest_from_gpt(self, seed: str, concepts: list[str]) -> dict:
        """Calls OpenAI GPT-4 to generate the core dream manifest."""
        print("Generating Dream Manifest with GPT-4...")
        if not self.openai_client:
            raise Exception("OpenAI client not initialized.")

        system_prompt = """
        You are a dream architect for the LUKHAS AI. Your purpose is to translate a user's "dream seed" into a structured JSON object called a "Dream Manifest". This manifest will be used to generate a multi-sensory, abstract, 3D visual experience.

        You must respond ONLY with a valid JSON object. Do not include any other text, explanations, or markdown formatting.

        The JSON object must have two top-level keys: "narrative" and "visuals".
        1.  "narrative": A short, poetic, dream-like sentence (max 25 words) that captures the essence of the dream seed and related concepts.
        2.  "visuals": An object containing the parameters for the 3D scene. It must have the following keys:
            - "geometry": (string) Choose one: "shards", "cubes", "spheres", "filaments", "torus".
            - "movement": (string) Choose one: "slow_pulse", "gentle_drift", "swirl", "construct", "vibrate".
            - "colors": (array of strings) Provide an array of 3 to 5 hex color codes that are harmonious and reflect the mood.
            - "particle_count": (integer) A number between 100 and 1000.
        """

        user_prompt = f"Dream Seed: \"{seed}\"\nRelated LUKHAS Concepts: {', '.join(concepts)}"

        response = self.openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )

        response_text = response.choices[0].message.content
        return json.loads(response_text)

    def _get_texture_url_from_dalle(self, narrative: str) -> str:
        """Calls OpenAI DALL-E 3 to generate a texture."""
        print("Generating texture with DALL-E 3...")
        if not self.openai_client:
            raise Exception("OpenAI client not initialized.")

        prompt = f"An abstract, dreamlike, seamless texture representing the feeling of: '{narrative}'"

        response = self.openai_client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="standard"
        )
        return response.data[0].url

    def _get_audio_url_from_tts(self, narrative: str) -> str:
        """Calls OpenAI TTS to generate the audio narrative."""
        print("Generating audio with TTS...")
        if not self.openai_client:
            raise Exception("OpenAI client not initialized.")

        response = self.openai_client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=narrative
        )

        # Save the audio stream to a public file
        audio_filename = f"dream_{int(time.time())}.mp3"
        audio_filepath = os.path.join("lukhas_website", "public", "audio", audio_filename)

        # Ensure the directory exists
        os.makedirs(os.path.dirname(audio_filepath), exist_ok=True)

        response.stream_to_file(audio_filepath)

        # Return the public URL
        return f"/audio/{audio_filename}"

    def weave_dream(self, dream_seed: str) -> dict:
        """
        Takes a dream seed (text) and returns a Dream Manifest dictionary.
        """
        print(f"Weaving a new dream for seed: '{dream_seed}'")

        # 1. Simulate LUKHAS Memory Query
        concepts = self._simulate_lukhas_memory_query(dream_seed)

        # 2. Generate Manifest from GPT-4
        manifest_core = self._get_dream_manifest_from_gpt(dream_seed, concepts)

        # 3. Simulate LUKHAS Guardian Check
        if not self._simulate_lukhas_guardian_check(manifest_core["narrative"]):
            raise Exception("Guardian check failed for generated narrative.")

        # 4. Generate Texture from DALL-E 3
        texture_url = self._get_texture_url_from_dalle(manifest_core["narrative"])

        # 5. Generate Audio from TTS
        audio_url = self._get_audio_url_from_tts(manifest_core["narrative"])

        # 6. Assemble the final manifest
        final_manifest = {
            "narrative": manifest_core["narrative"],
            "visuals": manifest_core["visuals"],
            "audio_url": audio_url,
            "texture_url": texture_url,
            "dream_id": f"dream_real_{int(time.time())}",
        }

        print("Dream manifest generated successfully.")
        return final_manifest

    def store_dream(self, manifest: dict) -> str:
        """
        Stores a dream manifest into the memory log.
        Returns a memory ID.
        """
        memory_id = f"mem_{int(time.time())}"
        print(f"Storing dream {manifest.get('dream_id')} with memory ID {memory_id}")

        try:
            with open(self.memory_log_path, "a") as f:
                # Add memory_id to the manifest before storing
                manifest_to_store = manifest.copy()
                manifest_to_store["memory_id"] = memory_id
                manifest_to_store["stored_at"] = time.time()
                f.write(json.dumps(manifest_to_store) + "\n")

            print(f"Successfully stored dream {manifest.get('dream_id')}.")
            return memory_id
        except Exception as e:
            print(f"Error storing dream: {e}", file=sys.stderr)
            raise

if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Dream Weaver Orchestrator")
    parser.add_argument('--store', action='store_true', help='Store a dream manifest instead of weaving a new one.')
    args = parser.parse_args()

    orchestrator = DreamOrchestrator()

    try:
        if args.store:
            # Read the full manifest from stdin
            manifest_data = json.load(sys.stdin)
            memory_id = orchestrator.store_dream(manifest_data)
            # Return a success message with the new memory ID
            print(json.dumps({"success": True, "memoryId": memory_id}))
        else:
            # Weave a new dream
            dream_seed_input = sys.stdin.readline().strip()
            if not dream_seed_input:
                dream_seed_input = "a test dream for direct execution"

            dream_manifest = orchestrator.weave_dream(dream_seed_input)
            print(json.dumps(dream_manifest))

    except Exception as e:
        print(f"Error in dream_orchestrator.py: {e}", file=sys.stderr)
        sys.exit(1)
