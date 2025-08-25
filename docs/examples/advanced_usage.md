# Advanced Usage Examples

This guide provides examples of how to use the more advanced features of the LUKHAS AI project.

## 1. Conversational AI with the Bridge Module

The `UnifiedOpenAIClient` in the bridge module can be used to have a conversation with the AI.

```python
import asyncio
from candidate.bridge.llm_wrappers.unified_openai_client import UnifiedOpenAIClient

async def main():
    client = UnifiedOpenAIClient(api_key="your-api-key")
    conversation_id = client.create_conversation(user_id="test_user", session_id="test_session")

    while True:
        prompt = input("You: ")
        if prompt.lower() == "exit":
            break

        client.add_message(conversation_id, role="user", content=prompt)
        messages = client.get_conversation_messages(conversation_id)

        response = await client.chat_completion(messages)
        assistant_message = response["choices"][0]["message"]["content"]

        print(f"LUKHAS: {assistant_message}")
        client.add_message(conversation_id, role="assistant", content=assistant_message)

if __name__ == "__main__":
    asyncio.run(main())
```

## 2. Causal Memory with the Memory Module

The `HybridMemoryFold` system can be used to store and retrieve memories with causal links.

```python
import asyncio
from candidate.memory.fold_system.memory_fold import HybridMemoryFold

async def main():
    memory = HybridMemoryFold()

    # Fold in some memories
    cause_id = await memory.fold_in(data={"event": "I ate a sandwich."}, tags=["food", "lunch"])
    effect_id = await memory.fold_in(data={"event": "I am full."}, tags=["feeling", "satiated"])

    # Add a causal link
    await memory.add_causal_link(cause_id=cause_id, effect_id=effect_id, strength=0.9)

    # Trace the causal chain
    chain = await memory.trace_causal_chain(effect_id)
    print(chain)

if __name__ == "__main__":
    asyncio.run(main())
```

## 3. Immersive Voice and Emotion Experience

The `VoiceHub` and `EmotionHub` can be used together to create a more immersive experience.

```python
import asyncio
from candidate.bridge.voice.voice_hub import get_voice_hub
from candidate.emotion.emotion_hub import get_emotion_hub

async def main():
    voice_hub = get_voice_hub()
    await voice_hub.initialize()

    emotion_hub = get_emotion_hub()
    await emotion_hub.initialize()

    # Process a happy message
    emotional_result = await emotion_hub.process_emotional_input({
        "text": "I am so happy today!",
        "user_id": "test_user"
    })

    # Generate a happy voice response
    voice_request = {
        "text": "That's great to hear! I'm happy for you.",
        "context": emotional_result["context_analysis"]
    }
    voice_result = await voice_hub.process_voice_request(voice_request)

    print(voice_result)

    await voice_hub.shutdown()
    await emotion_hub.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```
