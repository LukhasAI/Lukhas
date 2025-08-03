"""
Enhanced Core TypeScript - Integrated from Advanced Systems
Original: payload_builder.py
Advanced: payload_builder.py
Integration Date: 2025-05-31T07:55:30.623603
"""

"""
╭──────────────────────────────────────────────────────────────────────────────╮
│                    LUCΛS :: SYMBOLIC PAYLOAD BUILDER (v1.0)                 │
│     Create dream-aware, emotion-driven payloads for NIAS simulation         │
│        Author: Gonzo R.D.M & GPT-4o · Linked to core/sample_payloads/       │
╰──────────────────────────────────────────────────────────────────────────────╯
"""

import streamlit as st
import json
from datetime import datetime

st.title("🧠 LUCΛS :: Symbolic Payload Builder")
st.caption("Generate sample payloads for dream delivery, NIAS testing, and consent flow simulations.")

# Define default values
user_id = st.text_input("User ID", value="user_alpha")
message_id = st.text_input("Message ID", value=f"msg_{datetime.utcnow().strftime('%H%M%S')}")
tier = st.selectbox("Tier", [0, 1, 2, 3, 4, 5])
context_tier = st.selectbox("Context Tier", [0, 1, 2, 3, 4, 5])
source_widget = st.text_input("Source Widget", value="dream_widget")

tags = st.text_input("Tags (comma separated)", value="lucidity,soft")
message = st.text_area("Symbolic Message", value="Lukhas, I dreamed I was glowing like a waveform.")

joy = st.slider("Joy", 0.0, 1.0, 0.7)
stress = st.slider("Stress", 0.0, 1.0, 0.1)
calm = st.slider("Calm", 0.0, 1.0, 0.85)
longing = st.slider("Longing", 0.0, 1.0, 0.4)

suggest_voice = st.checkbox("🎙 Suggest Voice Narration", value=True)

# Generate payload
payload = {
    "message_id": message_id,
    "user_id": user_id,
    "tier": tier,
    "context_tier": context_tier,
    "source_widget": source_widget,
    "tags": [tag.strip() for tag in tags.split(",")],
    "emotion_vector": {
        "joy": joy,
        "stress": stress,
        "calm": calm,
        "longing": longing
    },
    "message": message,
    "suggest_voice": suggest_voice,
    "replay_candidate": suggest_voice and calm > 0.8,
    "reflection_score": None,
    "timestamp": datetime.utcnow().isoformat()
}

st.subheader("🧾 Generated Payload")
st.json(payload)

# Save to file
filename = st.text_input("Output filename", value="core/sample_payloads/sample_payload_generated.json")

if st.button("💾 Save Payload to File"):
    try:
        with open(filename, "w") as f:
            json.dump(payload, f, indent=4)
        st.success(f"Saved successfully to {filename}")
    except Exception as e:
        st.error(f"Failed to save payload: {e}")
"""
