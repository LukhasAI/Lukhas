# ════════════════════════════════════════════════════════════════════════
# 📁 FILE: message_hub.py
# 🧠 PURPOSE: Streamlit interface to generate symbolic messages (email, post, text, reword)
# 🔗 CONNECTS TO: lukhas_dna_link.py
# ════════════════════════════════════════════════════════════════════════

import json

# Streamlit support (optional)
try:
    import streamlit as st

    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    print("⚠️ Streamlit not available for UI features")

    # Create mock st for syntax checking
    class MockStreamlit:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None

        sidebar = property(lambda self: self)
        def title(self, *args, **kwargs):
            return None
        def checkbox(self, *args, **kwargs):
            return False
        def selectbox(self, *args, **kwargs):
            return ""
        def text_input(self, *args, **kwargs):
            return ""
        def text_area(self, *args, **kwargs):
            return ""
        def button(self, *args, **kwargs):
            return False
        def tabs(self, *args, **kwargs):
            return [self] * len(args[0])
        def subheader(self, *args, **kwargs):
            return None
        def code(self, *args, **kwargs):
            return None
        def markdown(self, *args, **kwargs):
            return None
        def expander(self, *args, **kwargs):
            return self

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    st = MockStreamlit()

from dna_link import LucasDNALink

st.sidebar.title("⚙️ Settings & Compliance")

with st.sidebar.expander("🛡️ Compliance Settings", expanded=True):
    enforce_gdpr = st.checkbox("Enable GDPR/International Compliance Logging", value=True)
    default_tone = st.selectbox("Default Tone", ["formal", "casual", "symbolic", "poetic"], index=2)
    default_language = st.selectbox("Default Language", ["en", "es", "fr", "de", "pt", "it"], index=0)
    st.markdown("_These defaults apply when tone/language not explicitly set._")

st.title("💬 Lukhas Symbolic Message Hub")

lukhas = LucasDNALink()

tabs = st.tabs(["📧 Email", "📣 Social Post", "💬 Text Message", "📝 Reword Draft"])

# 📧 EMAIL
with tabs[0]:
    st.subheader("Generate Email Draft")
    recipient = st.text_input("Recipient", value="Dr. Elara")
    topic = st.text_area("Topic / Purpose", height=100)
    tone = st.selectbox(
        "Tone",
        ["formal", "casual", "symbolic", "poetic"],
        index=["formal", "casual", "symbolic", "poetic"].index(default_tone),
    )
    language = st.selectbox(
        "Language",
        ["en", "es", "fr", "de", "pt", "it"],
        index=["en", "es", "fr", "de", "pt", "it"].index(default_language),
    )
    if st.button("✉️ Generate Email"):
        result = lukhas.generate_email_draft(topic=topic, recipient=recipient, language=language, tone=tone)
        st.code(result)
        selected_type = "email"

# 📣 SOCIAL POST
with tabs[1]:
    st.subheader("Create Social Media Post")
    topic = st.text_area("Topic", height=100)
    platform = st.selectbox("Platform", ["twitter", "linkedin", "instagram", "facebook"])
    tone = st.selectbox(
        "Tone",
        ["symbolic", "casual", "philosophical", "humorous"],
        index=(
            0
            if default_tone not in ["symbolic", "casual", "philosophical", "humorous"]
            else ["symbolic", "casual", "philosophical", "humorous"].index(default_tone)
        ),
    )
    if st.button("📤 Generate Post"):
        result = lukhas.generate_social_post(topic=topic, platform=platform, tone=tone)
        st.code(result)
        selected_type = "social_post"

# 💬 TEXT MESSAGE
with tabs[2]:
    st.subheader("Write Symbolic Text Message")
    recipient = st.text_input("Recipient Name", value="Ava")
    emotion = st.selectbox("Emotion", ["friendly", "gentle", "reassuring", "uplifting"])
    purpose = st.selectbox("Purpose", ["check-in", "gratitude", "apology", "invite"])
    if st.button("📱 Generate Message"):
        result = lukhas.generate_text_message(recipient=recipient, emotion=emotion, purpose=purpose)
        st.code(result)
        selected_type = "text_message"

# 📝 REWORD DRAFT
with tabs[3]:
    st.subheader("Reword an Existing Draft")
    draft = st.text_area("Paste Original Text", height=120)
    style = st.selectbox(
        "Reword As",
        ["poetic", "formal", "casual", "emotional"],
        index=(
            ["poetic", "formal", "casual", "emotional"].index(default_tone)
            if default_tone in ["poetic", "formal", "casual", "emotional"]
            else 0
        ),
    )
    if st.button("♻️ Reword"):
        result = lukhas.reword_draft(draft, style=style)
        st.code(result)
        selected_type = "reword_draft"

if "result" in locals() and result:
    st.markdown("### 🧠 Memory Options")
    save_memory = st.checkbox("Save this to Lukhas's memory", value=True)
    mark_qrg = st.checkbox("🔬 Apply QRG Stamp (Symbolic Identity Hash)", value=True)
    forgettable = st.checkbox(
        "🧹 User requests Lukhas never use this memory in future context",
        value=False,
    )

    if save_memory:
        import hashlib

        memory_entry = {
            "type": (selected_type if "selected_type" in locals() else "symbolic_message"),
            "content": result,
            "qrg_stamp": (hashlib.sha256(result.encode()).hexdigest()[:16] if mark_qrg else None),
            "forgettable": forgettable,
            "visible_to_user": True,
        }
        try:
            with open("logs/lukhas_memory_log.jsonl", "a") as f:
                f.write(json.dumps(memory_entry) + "\n")
            st.success("✅ Saved to Lukhas memory.")
        except Exception as mem_err:
            st.error(f"[Memory Save Error] {mem_err!s}")

with st.expander("📘 App Overview (for README.md)"):
    st.markdown(
        """
    **Lukhas Symbolic Message Hub**
    - `📧 Email`: Compose multilingual symbolic email drafts with tone control.
    - `📣 Social Post`: Write symbolic posts for various platforms.
    - `💬 Text Message`: Craft short expressive messages by emotion and intent.
    - `📝 Reword Draft`: Rewrite content in alternate tones and styles.

    Settings allow users to define ethical boundaries and comply with GDPR.
    """
    )
