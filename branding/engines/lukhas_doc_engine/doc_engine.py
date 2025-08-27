#!/usr/bin/env python3
"""
LUKHAS AI Document Engine - Database Integrated
Premium document generation with integrated knowledge base
Trinity Framework ⚛️🧠🛡️ integrated consciousness technology documentation
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from database_integration import db


class DocEngine:
    """
    LUKHAS AI document generation engine with database integration:
    - Knowledge base from integrated database
    - Real-time content storage and retrieval
    - Trinity Framework document templates
    - Cross-system content utilization
    """

    def __init__(self):
        self.base_path = Path(__file__).parent
        self.templates_path = self.base_path / "templates"
        self.formats_path = self.base_path / "formats"
        self.generators_path = self.base_path / "generators"
        self.knowledge_base_path = self.base_path / "knowledge_base"

        # Trinity Framework integration
        self.trinity_identity = "⚛️ Authentic consciousness technology identity"
        self.trinity_consciousness = "🧠 LUKHAS AI consciousness technology platform"
        self.trinity_guardian = "🛡️ Ethical consciousness technology protection"

        # Log engine initialization
        db.log_system_activity("doc_engine", "engine_init", "Document engine initialized", 1.0)

    def generate_document(self, doc_type: str, content: str, title: str = "Generated Document",
                         tone: str = "user-friendly") -> dict:
        """Generate document with Trinity Framework and database integration"""

        # Get related content from knowledge base
        related_content = db.get_content_by_type("knowledge_base", 3)
        knowledge_context = ""
        if related_content:
            knowledge_context = "\n\n## Related Knowledge:\n"
            for item in related_content:
                knowledge_context += f"- {item['title']}\n"

        trinity_header = f"""
# {self.trinity_identity}

{self.trinity_consciousness}

{self.trinity_guardian}

---

"""

        # Add consciousness technology branding and knowledge context
        enhanced_content = trinity_header + content.replace(
            "AI", "consciousness technology"
        ).replace(
            "artificial intelligence", "consciousness technology"
        ) + knowledge_context

        # Calculate voice coherence (basic implementation)
        voice_coherence = self._calculate_voice_coherence(enhanced_content)

        # Save generated document to database
        doc_id = db.save_generated_content(
            system_name="doc_engine",
            content_type=doc_type,
            title=title,
            content=enhanced_content,
            voice_coherence=voice_coherence
        )

        # Log generation activity
        db.log_system_activity("doc_engine", "document_generated",
                              f"Generated {doc_type}: {title}", voice_coherence)

        return {
            "id": doc_id,
            "title": title,
            "content": enhanced_content,
            "doc_type": doc_type,
            "voice_coherence": voice_coherence,
            "knowledge_items_used": len(related_content),
            "trinity_integrated": True
        }

    def _calculate_voice_coherence(self, content: str) -> float:
        """Calculate voice coherence score for generated content"""
        trinity_terms = ["⚛️", "🧠", "🛡️", "consciousness technology", "Trinity Framework"]
        lukhas_terms = ["LUKHAS AI", "consciousness", "quantum-inspired", "bio-inspired"]

        total_words = len(content.split())
        if total_words == 0:
            return 0.0

        trinity_count = sum(content.count(term) for term in trinity_terms)
        lukhas_count = sum(content.count(term) for term in lukhas_terms)

        coherence = ((trinity_count * 10) + (lukhas_count * 5)) / total_words * 100
        return min(coherence, 100.0)

    def get_knowledge_base(self, topic: str = None, limit: int = 20) -> list:
        """Get knowledge base content from integrated database"""
        if topic:
            # Get content related to topic
            all_content = db.get_all_content(100)
            related = [c for c in all_content if topic.lower() in c["content"].lower()]
            knowledge = related[:limit]
        else:
            knowledge = db.get_all_content(limit)

        # Log knowledge base access
        db.log_system_activity("doc_engine", "knowledge_accessed",
                              f"Accessed {len(knowledge)} knowledge items", len(knowledge))

        return knowledge

    def get_available_formats(self) -> list:
        """Get all available document formats from consolidated systems"""
        formats = [
            "landing_page", "blog_post", "api_docs", "marketing_copy",
            "video_script", "social_media", "technical_docs", "knowledge_base",
            "enterprise_docs", "mobile_docs", "training_materials", "user_manuals"
        ]
        return formats

    def get_engine_analytics(self) -> dict:
        """Get real-time engine analytics from database"""
        db.get_system_analytics("doc_engine")

        # Get document statistics
        all_docs = db.get_all_content(1000)
        doc_engine_content = [d for d in all_docs if d["source_system"] == "doc_engine"]

        avg_coherence = 0.0
        if doc_engine_content:
            coherences = [d["voice_coherence"] for d in doc_engine_content if d["voice_coherence"]]
            avg_coherence = sum(coherences) / len(coherences) if coherences else 0.0

        return {
            "total_documents": len(doc_engine_content),
            "average_voice_coherence": round(avg_coherence, 1),
            "available_formats": len(self.get_available_formats()),
            "knowledge_base_items": len(db.get_all_content(1000)),
            "trinity_integration": True,
            "database_connected": True
        }

if __name__ == "__main__":
    engine = DocEngine()

    print("🚀 LUKHAS AI Document Engine Ready")
    print(f"📄 Available formats: {len(engine.get_available_formats())}")

    # Show real database integration
    analytics = engine.get_engine_analytics()
    print(f"📊 Total documents: {analytics['total_documents']}")
    print(f"📈 Average coherence: {analytics['average_voice_coherence']}%")
    print(f"🧠 Knowledge base: {analytics['knowledge_base_items']} items")
    print("⚛️🧠🛡️ Trinity Framework Integrated")
    print("🔗 Database Integration: ACTIVE")
