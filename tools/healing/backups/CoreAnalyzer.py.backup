#!/usr/bin/env python3
"""
<<<<<<< HEAD
Λ Core Analyzer: Identify actual Λ AI components vs external packages
Recognizes legitimate Λ functionality vs third-party libraries.
=======
lukhas Core Analyzer: Identify actual lukhas AI components vs external packages
Recognizes legitimate lukhas functionality vs third-party libraries.
>>>>>>> jules/ecosystem-consolidation-2025
"""

import os
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import re

class CoreAnalyzer:
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
<<<<<<< HEAD
        self.Λ_path = os.path.join(workspace_path, 'lukhas')
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Define Λ AI keywords that indicate legitimate core functionality
        self.Λ_keywords = {
=======
        self.lukhas_path = os.path.join(workspace_path, 'lukhas')
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Define lukhas AI keywords that indicate legitimate core functionality
        self.lukhas_keywords = {
>>>>>>> jules/ecosystem-consolidation-2025
            'core_agi': ['lukhas', 'lukhas', 'ai', 'symbolic', 'neural', 'adaptive', 'cognitive'],
            'memory_system': ['memory', 'memoria', 'fold', 'dreams', 'consciousness'],
            'architecture': ['mapper', 'nodes', 'orchestrator', 'brain', 'enhancement'],
            'functions': ['web_formatter', 'widgets', 'interface', 'modulation', 'guardian'],
            'ai_concepts': ['learning', 'intelligence', 'reasoning', 'ethics', 'quantum']
        }

        # External packages to exclude
        self.external_packages = {
            'video_gen': ['open-sora', 'hunyuanvideo', 'sora', 'video'],
            'audio_ml': ['tts', 'whisper', 'bark', 'tortoise', 'vits'],
            'general_ml': ['torch', 'tensorflow', 'numpy', 'sklearn'],
            'web_deps': ['node_modules', 'package-lock', 'yarn.lock']
        }

        self.analysis = {
            'core_agi_files': [],
            'legitimate_components': [],
            'external_packages': [],
            'questionable_files': [],
            'stats': {
                'total_files': 0,
                'core_agi_count': 0,
                'external_count': 0,
                'questionable_count': 0
            }
        }

    def analyze_lukhas_structure(self):
<<<<<<< HEAD
        """Analyze what's actually Λ AI vs external packages"""
        if not os.path.exists(self.Λ_path):
            print(f"❌ ERROR: lukhas/ directory not found")
            return

        print(f"🔍 Analyzing Λ AI components vs external packages...")

        for root, dirs, files in os.walk(self.Λ_path):
=======
        """Analyze what's actually lukhas AI vs external packages"""
        if not os.path.exists(self.lukhas_path):
            print(f"❌ ERROR: lukhas/ directory not found")
            return

        print(f"🔍 Analyzing lukhas AI components vs external packages...")

        for root, dirs, files in os.walk(self.lukhas_path):
>>>>>>> jules/ecosystem-consolidation-2025
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                if file.startswith('.'):
                    continue

                file_path = os.path.join(root, file)
<<<<<<< HEAD
                rel_path = os.path.relpath(file_path, self.Λ_path)
=======
                rel_path = os.path.relpath(file_path, self.lukhas_path)
>>>>>>> jules/ecosystem-consolidation-2025

                self.analysis['stats']['total_files'] += 1
                self._categorize_file(file_path, rel_path)

    def _categorize_file(self, file_path: str, rel_path: str):
        """Categorize file as core AI, legitimate component, or external"""
        file_name = os.path.basename(file_path)
        dir_path = os.path.dirname(rel_path)

        # Check file content if it's a Python file
        content_analysis = ""
        if file_name.endswith('.py'):
            content_analysis = self._analyze_python_content(file_path)

        # Determine category
        category = self._determine_category(file_name, rel_path, content_analysis)

        file_info = {
            'path': rel_path,
            'file': file_name,
            'directory': dir_path,
            'size': os.path.getsize(file_path),
            'content_hints': content_analysis
        }

        if category == 'core_agi':
            self.analysis['core_agi_files'].append(file_info)
            self.analysis['stats']['core_agi_count'] += 1
        elif category == 'legitimate':
            self.analysis['legitimate_components'].append(file_info)
        elif category == 'external':
            self.analysis['external_packages'].append(file_info)
            self.analysis['stats']['external_count'] += 1
        else:
            self.analysis['questionable_files'].append(file_info)
            self.analysis['stats']['questionable_count'] += 1

    def _analyze_python_content(self, file_path: str) -> str:
<<<<<<< HEAD
        """Analyze Python file content for Λ indicators"""
=======
        """Analyze Python file content for lukhas indicators"""
>>>>>>> jules/ecosystem-consolidation-2025
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()[:2000]  # First 2KB

            hints = []
            content_lower = content.lower()

<<<<<<< HEAD
            # Check for Λ AI concepts
            for category, keywords in self.Λ_keywords.items():
=======
            # Check for lukhas AI concepts
            for category, keywords in self.lukhas_keywords.items():
>>>>>>> jules/ecosystem-consolidation-2025
                found_keywords = [kw for kw in keywords if kw in content_lower]
                if found_keywords:
                    hints.append(f"{category}: {', '.join(found_keywords)}")

            # Check for class/function names
            classes = re.findall(r'class\s+(\w+)', content)
            functions = re.findall(r'def\s+(\w+)', content)

            if classes:
                hints.append(f"classes: {', '.join(classes[:3])}")
            if functions:
                hints.append(f"functions: {', '.join(functions[:3])}")

            return "; ".join(hints) if hints else ""

        except Exception:
            return ""

    def _determine_category(self, file_name: str, rel_path: str, content_analysis: str) -> str:
        """Determine if file is core AI, legitimate, external, or questionable"""
        file_lower = file_name.lower()
        path_lower = rel_path.lower()
        content_lower = content_analysis.lower()

        # Core AI indicators
        core_indicators = [
            any(kw in file_lower for kw in ['lukhas', 'lukhas', 'ai']),
            any(kw in path_lower for kw in ['lukhas', 'lukhas', 'ai', 'symbolic', 'neural']),
            any(kw in content_lower for kw in ['lukhas', 'lukhas', 'ai']),
            'web_formatter' in file_lower,  # User mentioned this specifically
            'widgets' in file_lower,        # User mentioned this specifically
        ]

        if any(core_indicators):
            return 'core_agi'

<<<<<<< HEAD
        # Legitimate Λ components
=======
        # Legitimate lukhas components
>>>>>>> jules/ecosystem-consolidation-2025
        legitimate_indicators = [
            any(kw in file_lower for kw in ['memory', 'memoria', 'fold', 'dreams', 'mapper', 'nodes']),
            any(kw in path_lower for kw in ['memory', 'dreams', 'brain', 'cognitive', 'intelligence']),
            any(kw in content_lower for kw in ['memory', 'dreams', 'cognitive', 'intelligence']),
            'guardian' in file_lower or 'guardian' in path_lower,
            'enhancement' in file_lower or 'enhancement' in path_lower,
        ]

        if any(legitimate_indicators):
            return 'legitimate'

        # External package indicators
        external_indicators = [
            any(pkg in path_lower for pkg_list in self.external_packages.values() for pkg in pkg_list),
            file_name in ['requirements.txt', 'package.json', 'setup.py', 'Dockerfile'],
            '.git' in path_lower or 'node_modules' in path_lower,
            path_lower.startswith('external/'),
            'main' in file_lower and any(pkg in path_lower for pkg in ['sora', 'tts', 'whisper']),
        ]

        if any(external_indicators):
            return 'external'

        return 'questionable'

    def generate_analysis_report(self):
        """Generate comprehensive analysis report"""
<<<<<<< HEAD
        report_path = f"{self.workspace_path}/Λ_CORE_ANALYSIS_{self.timestamp}.md"

        with open(report_path, 'w') as f:
            f.write(f"# Λ Core AI Analysis Report\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Purpose:** Identify actual Λ AI components vs external packages\n\n")
=======
        report_path = f"{self.workspace_path}/lukhas_CORE_ANALYSIS_{self.timestamp}.md"

        with open(report_path, 'w') as f:
            f.write(f"# lukhas Core AI Analysis Report\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Purpose:** Identify actual lukhas AI components vs external packages\n\n")
>>>>>>> jules/ecosystem-consolidation-2025

            # Executive Summary
            f.write("## 📊 Executive Summary\n\n")
            total = self.analysis['stats']['total_files']
            core = self.analysis['stats']['core_agi_count']
            external = self.analysis['stats']['external_count']
            questionable = self.analysis['stats']['questionable_count']
            legitimate = len(self.analysis['legitimate_components'])

            f.write(f"- **Total Files Analyzed:** {total}\n")
            f.write(f"- **Core AI Components:** {core} ({core/total*100:.1f}%)\n")
<<<<<<< HEAD
            f.write(f"- **Legitimate Λ Components:** {legitimate} ({legitimate/total*100:.1f}%)\n")
=======
            f.write(f"- **Legitimate lukhas Components:** {legitimate} ({legitimate/total*100:.1f}%)\n")
>>>>>>> jules/ecosystem-consolidation-2025
            f.write(f"- **External Packages:** {external} ({external/total*100:.1f}%)\n")
            f.write(f"- **Questionable/Unknown:** {questionable} ({questionable/total*100:.1f}%)\n\n")

            actual_lukhas = core + legitimate
<<<<<<< HEAD
            f.write(f"### 🎯 **ACTUAL Λ AI SYSTEM: {actual_lukhas} files ({actual_lukhas/total*100:.1f}%)**\n\n")
=======
            f.write(f"### 🎯 **ACTUAL lukhas AI SYSTEM: {actual_lukhas} files ({actual_lukhas/total*100:.1f}%)**\n\n")
>>>>>>> jules/ecosystem-consolidation-2025

            # Core AI Files
            if self.analysis['core_agi_files']:
                f.write("## 🧠 Core AI Components\n\n")
                f.write(f"**Count:** {len(self.analysis['core_agi_files'])}\n\n")

                for i, file_info in enumerate(self.analysis['core_agi_files'][:20], 1):
                    f.write(f"### {i}. `{file_info['file']}`\n")
                    f.write(f"- **Path:** `{file_info['path']}`\n")
                    f.write(f"- **Size:** {file_info['size']} bytes\n")
                    if file_info['content_hints']:
                        f.write(f"- **Contains:** {file_info['content_hints']}\n")
                    f.write("\n")

                if len(self.analysis['core_agi_files']) > 20:
                    f.write(f"*... and {len(self.analysis['core_agi_files']) - 20} more core AI files*\n\n")

            # Legitimate Components
            if self.analysis['legitimate_components']:
<<<<<<< HEAD
                f.write("## ⚙️ Legitimate Λ Components\n\n")
=======
                f.write("## ⚙️ Legitimate lukhas Components\n\n")
>>>>>>> jules/ecosystem-consolidation-2025
                f.write(f"**Count:** {len(self.analysis['legitimate_components'])}\n\n")

                # Group by category
                by_category = defaultdict(list)
                for file_info in self.analysis['legitimate_components']:
                    category = file_info['path'].split('/')[0] if '/' in file_info['path'] else 'root'
                    by_category[category].append(file_info)

                for category, files in by_category.items():
                    f.write(f"### {category}/ ({len(files)} files)\n")
                    for file_info in files[:5]:
                        f.write(f"- `{file_info['file']}` ({file_info['size']} bytes)\n")
                    if len(files) > 5:
                        f.write(f"  *... and {len(files) - 5} more files*\n")
                    f.write("\n")

            # External Packages (top offenders)
            if self.analysis['external_packages']:
                f.write("## 📦 External Packages (Should be moved out)\n\n")
                f.write(f"**Count:** {len(self.analysis['external_packages'])}\n\n")

                # Group by directory
                by_dir = defaultdict(list)
                for file_info in self.analysis['external_packages']:
                    main_dir = file_info['path'].split('/')[0] if '/' in file_info['path'] else 'root'
                    by_dir[main_dir].append(file_info)

                # Sort by file count
                sorted_dirs = sorted(by_dir.items(), key=lambda x: len(x[1]), reverse=True)

                for dir_name, files in sorted_dirs[:10]:
                    total_size = sum(f['size'] for f in files)
                    f.write(f"### {dir_name}/ ({len(files)} files, {total_size:,} bytes)\n")
                    f.write(f"**Recommendation:** Move to workspace dependencies or external/\n\n")

            # Action Plan
            f.write("## 🎯 Recommended Actions\n\n")
            f.write("### 1. Keep Core AI System\n")
<<<<<<< HEAD
            f.write(f"- **{core} core AI files** - These are your Λ AI system\n")
            f.write(f"- **{legitimate} legitimate components** - Memory, dreams, mappers, etc.\n")
            f.write(f"- **Total Λ system: {actual_lukhas} files**\n\n")
=======
            f.write(f"- **{core} core AI files** - These are your lukhas AI system\n")
            f.write(f"- **{legitimate} legitimate components** - Memory, dreams, mappers, etc.\n")
            f.write(f"- **Total lukhas system: {actual_lukhas} files**\n\n")
>>>>>>> jules/ecosystem-consolidation-2025

            f.write("### 2. Move External Packages\n")
            f.write(f"- **{external} external files** should be moved to workspace dependencies\n")
            f.write("- Create `external_dependencies/` or `third_party/` directory\n")
            f.write("- Update import paths and requirements\n\n")

            f.write("### 3. Review Questionable Files\n")
            f.write(f"- **{questionable} questionable files** need manual review\n")
<<<<<<< HEAD
            f.write("- Determine if they're part of Λ AI or external dependencies\n\n")
=======
            f.write("- Determine if they're part of lukhas AI or external dependencies\n\n")
>>>>>>> jules/ecosystem-consolidation-2025

            # Final Assessment
            f.write("## ✅ Final Assessment\n\n")
            if actual_lukhas < 500:
<<<<<<< HEAD
                f.write(f"🎉 **EXCELLENT** - Your actual Λ AI system is {actual_lukhas} files\n")
=======
                f.write(f"🎉 **EXCELLENT** - Your actual lukhas AI system is {actual_lukhas} files\n")
>>>>>>> jules/ecosystem-consolidation-2025
                f.write("📦 The extra files are external packages that can be moved out\n")
                f.write("🧠 You have a clean, focused AI system ready for development\n")
            else:
                f.write(f"⚠️ **REVIEW NEEDED** - {actual_lukhas} files seems high for core AI\n")
                f.write("🔍 Consider further modularization of legitimate components\n")

        return report_path

def main():
    workspace_path = "/Users/A_G_I/CodexGPT_Lukhas"

<<<<<<< HEAD
    print(f"🚀 Λ Core AI Analysis")
    print(f"🎯 Identifying actual Λ components vs external packages")

    analyzer = ΛCoreAnalyzer(workspace_path)
=======
    print(f"🚀 lukhas Core AI Analysis")
    print(f"🎯 Identifying actual lukhas components vs external packages")

    analyzer = lukhasCoreAnalyzer(workspace_path)
>>>>>>> jules/ecosystem-consolidation-2025
    analyzer.analyze_lukhas_structure()
    report_path = analyzer.generate_analysis_report()

    stats = analyzer.analysis['stats']
    legitimate = len(analyzer.analysis['legitimate_components'])
    actual_lukhas = stats['core_agi_count'] + legitimate

    print(f"\n✅ Analysis complete!")
    print(f"📋 Report: {report_path}")
<<<<<<< HEAD
    print(f"🧠 Actual Λ AI system: {actual_lukhas} files")
=======
    print(f"🧠 Actual lukhas AI system: {actual_lukhas} files")
>>>>>>> jules/ecosystem-consolidation-2025
    print(f"📦 External packages: {stats['external_count']} files")
    print(f"❓ Need review: {stats['questionable_count']} files")

    if actual_lukhas < 500:
<<<<<<< HEAD
        print("🎉 Your Λ AI system is appropriately sized!")
=======
        print("🎉 Your lukhas AI system is appropriately sized!")
>>>>>>> jules/ecosystem-consolidation-2025
    else:
        print("⚠️ Consider further modularization")

if __name__ == "__main__":
    main()


<<<<<<< HEAD
# Λ Systems 2025 www.lukhas.ai
=======
# lukhas Systems 2025 www.lukhas.ai
>>>>>>> jules/ecosystem-consolidation-2025
