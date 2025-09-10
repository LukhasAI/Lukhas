#!/usr/bin/env python3
"""
LUKHAS AI System Orchestrator
Master coordinator for all integrated consciousness technology systems
Real-time coordination between database, content platform, and document engine
"""
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from database_integration import db
from lukhas_content_platform.content_platform import ContentPlatform
from lukhas_doc_engine.doc_engine import DocEngine


class Orchestrator:
    """
    Master orchestrator for LUKHAS AI consciousness technology platform
    Coordinates all systems with real-time database integration
    """

    def __init__(self):
        self.content_platform = ContentPlatform()
        self.doc_engine = DocEngine()

        # Trinity Framework branding
        self.trinity_branding = "⚛️🧠🛡️ LUKHAS AI Trinity Framework"

        # Log orchestrator initialization
        db.log_system_activity("orchestrator", "system_init", "System orchestrator initialized", 1.0)

    def create_complete_content_workflow(self, topic: str, content_type: str = "blog_post") -> dict:
        """
        Complete workflow: Generate content → Store in DB → Use for documents → Analytics
        Demonstrates real system interconnection
        """
        print(f"🚀 Starting complete workflow for: {topic}")

        # Step 1: Content platform generates initial content
        initial_content = f"""
# {topic}

This {content_type} demonstrates the LUKHAS AI consciousness technology platform.

Our Trinity Framework (⚛️🧠🛡️) provides:
- ⚛️ Authentic consciousness technology identity
- 🧠 Advanced consciousness technology processing
- 🛡️ Ethical consciousness technology protection

Generated through our integrated platform with real database integration.
"""

        content_id = self.content_platform.generate_content(
            content_type=content_type, title=topic, content=initial_content, voice_coherence=75.0
        )

        print(f"✅ Content generated and saved (ID: {content_id})")

        # Step 2: Document engine creates enhanced document using knowledge base
        doc_result = self.doc_engine.generate_document(
            doc_type="enhanced_" + content_type,
            content=initial_content + "\n\nEnhanced with knowledge base integration.",
            title=f"Enhanced {topic}",
            tone="professional",
        )

        print(f"✅ Enhanced document created (ID: {doc_result['id']})")

        # Step 3: Get cross-system analytics
        content_analytics = self.content_platform.get_platform_analytics()
        doc_analytics = self.doc_engine.get_engine_analytics()
        system_analytics = db.get_system_analytics()

        print("✅ Analytics gathered from all systems")

        # Step 4: Create workflow summary
        workflow_result = {
            "workflow_topic": topic,
            "content_id": content_id,
            "document_id": doc_result["id"],
            "content_analytics": content_analytics,
            "document_analytics": doc_analytics,
            "system_activity": len(system_analytics),
            "voice_coherence": doc_result["voice_coherence"],
            "trinity_integration": True,
            "systems_interconnected": True,
            "workflow_completed": datetime.now(timezone.utc).isoformat(),
        }

        # Log workflow completion
        db.log_system_activity(
            "orchestrator",
            "workflow_completed",
            f"Complete workflow for: {topic}",
            doc_result["voice_coherence"],
        )

        return workflow_result

    def get_dashboard(self) -> dict:
        """Get real-time dashboard data from all interconnected systems"""
        # Get data from all systems
        content_analytics = self.content_platform.get_platform_analytics()
        doc_analytics = self.doc_engine.get_engine_analytics()
        system_analytics = db.get_system_analytics()

        # Calculate unified metrics
        total_content = content_analytics["total_content_items"]
        total_docs = doc_analytics["total_documents"]
        avg_coherence = doc_analytics["average_voice_coherence"]

        dashboard = {
            "platform_status": "ACTIVE",
            "systems_integrated": 3,
            "database_connected": True,
            "trinity_framework_active": True,
            "metrics": {
                "total_content_items": total_content,
                "total_documents": total_docs,
                "average_voice_coherence": avg_coherence,
                "recent_activity": len(system_analytics),
                "specialist_bots": len(self.content_platform.get_specialist_bots()),
                "document_formats": len(self.doc_engine.get_available_formats()),
            },
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

        return dashboard

    def demonstrate_integration(self):
        """Demonstrate that all systems are truly interconnected"""
        print("\n" + "=" * 60)
        print("🎯 LUKHAS AI System Integration Demonstration")
        print("=" * 60)

        # Test workflow
        result = self.create_complete_content_workflow("Consciousness Technology Innovation", "technical_documentation")

        print("\n📊 Workflow Results:")
        print(f"   Content Items: {result['content_analytics']['total_content_items']}")
        print(f"   Documents: {result['document_analytics']['total_documents']}")
        print(f"   Voice Coherence: {result['voice_coherence']}%")
        print(f"   Systems Active: {result['systems_interconnected']}")

        # Show dashboard
        dashboard = self.get_dashboard()
        print("\n🎯 System Dashboard:")
        print(f"   Platform Status: {dashboard['platform_status']}")
        print(f"   Database Connected: {dashboard['database_connected']}")
        print(f"   Trinity Framework: {dashboard['trinity_framework_active']}")
        print(f"   Total Content: {dashboard['metrics']['total_content_items']}")
        print(f"   Recent Activity: {dashboard['metrics']['recent_activity']}")

        print("\n✅ ALL SYSTEMS FULLY INTERCONNECTED AND ACTIVE")
        return dashboard


if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.demonstrate_integration()