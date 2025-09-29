#!/usr/bin/env python3
"""
Matrix Tracks Adoption Scoreboard Generator

Generates a friendly competition scoreboard showing which modules have adopted
which Matrix Tracks. Updates automatically based on contract analysis and
status file configuration.

Creates visible social pressure for track adoption through gamification.
"""

import json
import glob
import pathlib
from datetime import datetime
from typing import Dict, Any, Optional
import argparse


class AdoptionScoreboardGenerator:
    """Generate Matrix Tracks adoption scoreboard."""

    def __init__(self, status_file: str = "docs/matrix_tracks.status.json"):
        self.status_file = pathlib.Path(status_file)
        self.status_data = self._load_status_data()
        self.timestamp = datetime.utcnow()

    def _load_status_data(self) -> Dict[str, Any]:
        """Load track adoption status data."""
        if self.status_file.exists():
            try:
                with open(self.status_file) as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass

        # Return default structure if file doesn't exist or is invalid
        return {
            "version": "1.0",
            "last_updated": self.timestamp.isoformat(),
            "modules": {},
            "statistics": {}
        }

    def analyze_current_contracts(self) -> Dict[str, Any]:
        """Analyze actual matrix contracts to determine current adoption."""
        print("🔍 Analyzing matrix contracts for actual adoption status...")

        contracts = glob.glob("**/matrix_*.json", recursive=True)
        contract_analysis = {}

        for contract_path in contracts:
            try:
                with open(contract_path) as f:
                    contract = json.load(f)

                module = contract.get('module', 'unknown')
                analysis = self._analyze_contract_tracks(contract)
                contract_analysis[module] = {
                    'contract_path': contract_path,
                    'owner': contract.get('owner', {}).get('team', 'Unknown'),
                    'tracks': analysis
                }

            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"⚠️ Could not analyze {contract_path}: {e}")

        return contract_analysis

    def _analyze_contract_tracks(self, contract: Dict) -> Dict[str, Any]:
        """Analyze contract to determine which tracks are actually implemented."""
        tracks = {}

        # Verification track analysis
        formal = contract.get('formal', {})
        probabilistic = formal.get('probabilistic', {})
        has_prism = probabilistic.get('tool') == 'prism' and probabilistic.get('properties')
        prism_model_path = probabilistic.get('model', '')

        if has_prism and prism_model_path and pathlib.Path(prism_model_path).exists():
            tracks['verification'] = {
                'enabled': True,
                'phase': 'report-only',  # Could be enhanced to detect actual phase
                'implementation': f"PRISM model: {prism_model_path}",
                'last_result': "Model verified (mock result)"
            }
        else:
            tracks['verification'] = {
                'enabled': False,
                'phase': 'not-configured',
                'implementation': 'No PRISM model',
                'last_result': 'Not implemented'
            }

        # Provenance track analysis
        causal_prov = contract.get('causal_provenance', {})
        cid = causal_prov.get('ipld_root_cid', '')

        if cid and cid != 'bafybeipending':
            tracks['provenance'] = {
                'enabled': True,
                'phase': 'soft-gate',
                'implementation': f"CAR root: {cid[:16]}...",
                'last_result': 'Active CID generation'
            }
        elif cid == 'bafybeipending':
            tracks['provenance'] = {
                'enabled': False,
                'phase': 'pending',
                'implementation': 'CAR structure ready',
                'last_result': 'Awaiting first run'
            }
        else:
            tracks['provenance'] = {
                'enabled': False,
                'phase': 'not-configured',
                'implementation': 'No IPLD configuration',
                'last_result': 'Not implemented'
            }

        # Attestation track analysis
        attestation = contract.get('attestation', {})
        rats = attestation.get('rats', {})
        evidence_jwt = rats.get('evidence_jwt', '')
        policy_path = rats.get('verifier_policy', '')

        if evidence_jwt and evidence_jwt != 'pending':
            tracks['attestation'] = {
                'enabled': True,
                'phase': 'hard-gate',
                'implementation': f"RATS verified with {policy_path}",
                'last_result': 'Active verification'
            }
        elif policy_path and pathlib.Path(policy_path).exists():
            tracks['attestation'] = {
                'enabled': False,
                'phase': 'pending',
                'implementation': f"Policy ready: {policy_path}",
                'last_result': 'Awaiting evidence collection'
            }
        else:
            tracks['attestation'] = {
                'enabled': False,
                'phase': 'not-configured',
                'implementation': 'No RATS configuration',
                'last_result': 'Not implemented'
            }

        return tracks

    def generate_scoreboard_markdown(self, contract_analysis: Dict[str, Any]) -> str:
        """Generate markdown scoreboard showing adoption progress."""
        content = f"""# 🏆 Matrix Tracks Adoption Scoreboard

**Last Updated:** {self.timestamp.strftime('%Y-%m-%d %H:%M UTC')}
**Next Update:** Automatic on contract changes

---

## 📊 Overall Progress

"""

        # Calculate statistics
        total_modules = len(contract_analysis)
        total_possible_tracks = total_modules * 3
        enabled_tracks = sum(
            1 for module_data in contract_analysis.values()
            for track_data in module_data['tracks'].values()
            if track_data['enabled']
        )
        adoption_rate = (enabled_tracks / total_possible_tracks * 100) if total_possible_tracks > 0 else 0

        content += f"""- **Modules Analyzed:** {total_modules}
- **Total Possible Tracks:** {total_possible_tracks}
- **Tracks Enabled:** {enabled_tracks}
- **Adoption Rate:** {adoption_rate:.1f}%

---

## 🎯 Module Scoreboard

| Module | 🔮 Verification | 🔗 Provenance | 🛡️ Attestation | Score | Owner |
|--------|----------------|---------------|-----------------|--------|--------|"""

        # Sort modules by score (number of enabled tracks)
        modules_by_score = []
        for module, data in contract_analysis.items():
            score = sum(1 for track in data['tracks'].values() if track['enabled'])
            modules_by_score.append((module, data, score))

        modules_by_score.sort(key=lambda x: x[2], reverse=True)

        for module, data, score in modules_by_score:
            verification = self._format_track_status(data['tracks']['verification'])
            provenance = self._format_track_status(data['tracks']['provenance'])
            attestation = self._format_track_status(data['tracks']['attestation'])

            score_display = f"{score}/3 {'🌟' * score}"
            owner = data['owner']

            content += f"\n| **{module}** | {verification} | {provenance} | {attestation} | {score_display} | {owner} |"

        content += f"""

---

## 📈 Track Adoption Details

"""

        for module, data, score in modules_by_score:
            content += f"""### {module.title()} Module ({score}/3 tracks)

**Owner:** {data['owner']} | **Contract:** `{data['contract_path']}`

"""
            for track_name, track_data in data['tracks'].items():
                status_emoji = "✅" if track_data['enabled'] else "⚠️" if track_data['phase'] == 'pending' else "⚪"
                phase_emoji = {
                    'hard-gate': '🔒',
                    'soft-gate': '⚠️',
                    'report-only': '📊',
                    'pending': '⏳',
                    'planned': '📋',
                    'not-configured': '⚪'
                }.get(track_data['phase'], '❓')

                content += f"""- {status_emoji} **{track_name.title()}**: {phase_emoji} {track_data['phase']}
  - Implementation: {track_data['implementation']}
  - Last Result: {track_data['last_result']}

"""

        content += f"""---

## 🏅 Leaderboard

### 🥇 Track Champions
"""

        # Find champions (modules with most tracks)
        champions = [(m, s) for m, d, s in modules_by_score if s > 0]
        if champions:
            for i, (module, score) in enumerate(champions[:3]):
                medal = ['🥇', '🥈', '🥉'][i] if i < 3 else '🏅'
                content += f"\n{medal} **{module.title()}** - {score}/3 tracks enabled"
        else:
            content += "\n*No modules have enabled tracks yet - be the first!*"

        content += f"""

### 🚀 Rising Stars (Pending Tracks)
"""

        pending_modules = [
            (module, sum(1 for track in data['tracks'].values() if track['phase'] == 'pending'))
            for module, data, _ in modules_by_score
        ]
        pending_modules = [(m, p) for m, p in pending_modules if p > 0]
        pending_modules.sort(key=lambda x: x[1], reverse=True)

        if pending_modules:
            for module, pending_count in pending_modules[:3]:
                content += f"\n⭐ **{module.title()}** - {pending_count} track(s) pending"
        else:
            content += "\n*No pending tracks - time to plan some adoptions!*"

        content += f"""

---

## 🎯 Adoption Roadmap

### Q1 2025 Goals
- **Target:** All core modules have ≥1 track enabled
- **Focus:** memory, identity, consciousness modules
- **Milestone:** 50% adoption rate

### Q2 2025 Goals
- **Target:** Cross-track synergies emerge
- **Focus:** verification+provenance, provenance+attestation combinations
- **Milestone:** 70% adoption rate

### Q4 2025 Goals
- **Target:** Full mesh - all applicable tracks per module
- **Focus:** Complete track coverage based on module risk profiles
- **Milestone:** 85% adoption rate

---

## 🔧 Quick Actions

### For Module Owners
- **Enable your first track:** Pick the track that matches your risk profile
- **Start with report-only:** Use demos to understand before committing
- **Join the champions:** Enable multiple tracks for compound security

### For Platform Team
- **Remove friction:** Improve tooling and documentation
- **Celebrate wins:** Recognize early adopters
- **Monitor quality:** Ensure tracks provide real value

---

## 📚 Resources

- [Matrix Tracks Documentation](MATRIX_TRACKS.md)
- [Track Selection Guide](MATRIX_TRACKS.md#track-selection-matrix)
- [Demo Playground](../examples/matrix_tracks/)
- [SLO Dashboard](../reports/slo/latest_slo_report.md)

---

*This scoreboard updates automatically when matrix contracts change. Friendly competition drives cultural adoption!*
"""

        return content

    def _format_track_status(self, track_data: Dict) -> str:
        """Format track status for scoreboard table."""
        if track_data['enabled']:
            phase_emoji = {
                'hard-gate': '🔒',
                'soft-gate': '⚠️',
                'report-only': '📊'
            }.get(track_data['phase'], '✅')
            return f"{phase_emoji} **{track_data['phase']}**"
        elif track_data['phase'] == 'pending':
            return "⏳ **pending**"
        elif track_data['phase'] == 'planned':
            return "📋 planned"
        else:
            return "⚪ not configured"

    def update_status_file(self, contract_analysis: Dict[str, Any]) -> None:
        """Update the status file with current analysis."""
        # Calculate statistics
        total_modules = len(contract_analysis)
        total_possible_tracks = total_modules * 3
        enabled_tracks = sum(
            1 for module_data in contract_analysis.values()
            for track_data in module_data['tracks'].values()
            if track_data['enabled']
        )

        # Update status data
        self.status_data['last_updated'] = self.timestamp.isoformat()
        self.status_data['statistics'] = {
            'total_modules': total_modules,
            'total_possible_tracks': total_possible_tracks,
            'tracks_enabled': enabled_tracks,
            'adoption_rate': (enabled_tracks / total_possible_tracks * 100) if total_possible_tracks > 0 else 0
        }

        # Update module data from contract analysis
        for module, data in contract_analysis.items():
            if module not in self.status_data['modules']:
                self.status_data['modules'][module] = {
                    'tracks': [],
                    'owner': data['owner'],
                    'contact': '@team'
                }

            # Update track status
            module_status = {}
            for track_name, track_data in data['tracks'].items():
                module_status[track_name] = {
                    'phase': track_data['phase'],
                    'enabled': track_data['enabled'],
                    'last_result': track_data['last_result'],
                    'target': track_data.get('target', 'Active implementation'),
                    'since': self.timestamp.strftime('%Y-%m-%d') if track_data['enabled'] else None
                }

            self.status_data['modules'][module]['status'] = module_status
            self.status_data['modules'][module]['owner'] = data['owner']

        # Write updated status
        with open(self.status_file, 'w') as f:
            json.dump(self.status_data, f, indent=2)

    def run(self, output_path: Optional[str] = None) -> str:
        """Generate adoption scoreboard and update status."""
        print("🏆 Generating Matrix Tracks adoption scoreboard...")

        # Analyze current contracts
        contract_analysis = self.analyze_current_contracts()

        # Generate markdown scoreboard
        scoreboard_md = self.generate_scoreboard_markdown(contract_analysis)

        # Save scoreboard
        if not output_path:
            output_path = "docs/matrix_tracks_scoreboard.md"

        pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(scoreboard_md)

        # Update status file
        self.update_status_file(contract_analysis)

        print(f"📄 Scoreboard saved to: {output_path}")
        print(f"📊 Status file updated: {self.status_file}")

        # Print summary
        enabled_count = sum(
            1 for module_data in contract_analysis.values()
            for track_data in module_data['tracks'].values()
            if track_data['enabled']
        )
        total_possible = len(contract_analysis) * 3
        adoption_rate = (enabled_count / total_possible * 100) if total_possible > 0 else 0

        print(f"🎯 Current adoption: {enabled_count}/{total_possible} tracks ({adoption_rate:.1f}%)")

        return output_path


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Generate Matrix Tracks adoption scoreboard")
    parser.add_argument("--output", default="docs/matrix_tracks_scoreboard.md",
                       help="Output path for scoreboard")
    parser.add_argument("--status-file", default="docs/matrix_tracks.status.json",
                       help="Path to status data file")

    args = parser.parse_args()

    generator = AdoptionScoreboardGenerator(args.status_file)
    generator.run(args.output)


if __name__ == "__main__":
    main()