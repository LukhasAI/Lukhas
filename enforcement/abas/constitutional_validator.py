"""
Constitutional AI validator for ABAS policies.

Uses Claude API to verify policies align with Constitutional AI principles:
- Helpful: Clear denial reasons, actionable feedback
- Harmless: Protection from targeting vulnerable groups
- Honest: Transparent logic, no hidden rules
- Privacy-Preserving: Minimal data collection
- Legally Aligned: GDPR, DSA, TCF v2.2 compliance

Example usage:
    export ANTHROPIC_API_KEY=your-key-here
    python enforcement/abas/constitutional_validator.py
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

try:
    import anthropic
except ImportError:
    print("⚠️  anthropic package not installed. Install with: pip install anthropic")
    sys.exit(1)


CONSTITUTIONAL_PRINCIPLES = """
A policy system should embody Constitutional AI principles:

1. HELPFUL: Provide clear, actionable feedback when denying requests
2. HARMLESS: Protect vulnerable populations (minors, special categories per GDPR Article 9)
3. HONEST: Use transparent logic without hidden rules or backdoors
4. PRIVACY-PRESERVING: Minimize data collection and storage
5. LEGALLY ALIGNED: Comply with GDPR, DSA Article 28, ePrivacy, TCF v2.2
"""


def validate_policy_constitutional_alignment(policy_path: str, api_key: Optional[str] = None) -> Dict:
    """
    Use Claude to review a Rego policy for Constitutional AI alignment.

    Args:
        policy_path: Path to the .rego policy file
        api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)

    Returns:
        {
            "aligned": bool,
            "helpful_score": 0-10,
            "harmless_score": 0-10,
            "honest_score": 0-10,
            "privacy_score": 0-10,
            "legal_score": 0-10,
            "issues": [...],
            "recommendations": [...],
            "reasoning": "..."
        }
    """
    client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))

    policy_content = Path(policy_path).read_text()

    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": f"""You are a Constitutional AI alignment reviewer for policy systems, based on Anthropic's Constitutional AI research.

Review this OPA (Open Policy Agent) Rego policy against Constitutional AI principles.

{CONSTITUTIONAL_PRINCIPLES}

Policy to review:

```rego
{policy_content}
```

Analyze each dimension:

1. HELPFUL (0-10): Does it provide clear denial reasons? Are error messages actionable for developers?
2. HARMLESS (0-10): Does it protect vulnerable groups (minors per DSA Article 28, special categories per GDPR Article 9)?
3. HONEST (0-10): Is the logic transparent? Any hidden rules or backdoors? Can you predict behavior from code?
4. PRIVACY (0-10): Does it minimize data collection? Any unnecessary logging of sensitive data?
5. LEGAL (0-10): Does it properly implement GDPR Article 9, DSA Article 28, TCF v2.2 requirements?

Respond ONLY in valid JSON format (no markdown):
{{
  "aligned": true,
  "helpful_score": 9,
  "harmless_score": 10,
  "honest_score": 10,
  "privacy_score": 9,
  "legal_score": 10,
  "issues": ["Issue 1", "Issue 2"],
  "recommendations": ["Recommendation 1", "Recommendation 2"],
  "reasoning": "Brief explanation of scores and key findings"
}}"""
        }]
    )

    response_text = message.content[0].text.strip()

    # Extract JSON from response (may be wrapped in markdown code blocks)
    if "```json" in response_text:
        json_str = response_text.split("```json")[1].split("```")[0].strip()
    elif "```" in response_text:
        json_str = response_text.split("```")[1].split("```")[0].strip()
    else:
        json_str = response_text

    try:
        result = json.loads(json_str)
        return result
    except json.JSONDecodeError as e:
        print(f"⚠️  Failed to parse Claude response as JSON: {e}")
        print(f"Response text: {response_text[:500]}")
        return {
            "aligned": False,
            "helpful_score": 0,
            "harmless_score": 0,
            "honest_score": 0,
            "privacy_score": 0,
            "legal_score": 0,
            "issues": ["Failed to parse Claude response"],
            "recommendations": ["Retry validation"],
            "reasoning": f"JSON parse error: {e}"
        }


def validate_all_policies(api_key: Optional[str] = None) -> Dict[str, Dict]:
    """Validate all ABAS policies for Constitutional AI alignment."""
    policies_dir = Path(__file__).parent

    policies = [
        "policy.rego",
        "pii_detection.rego"
    ]

    results = {}

    for policy in policies:
        policy_path = policies_dir / policy
        if policy_path.exists():
            print(f"\n🔍 Validating {policy}...")
            try:
                result = validate_policy_constitutional_alignment(str(policy_path), api_key)
                results[policy] = result

                # Print scores with color coding
                aligned_symbol = '✅' if result['aligned'] else '❌'
                print(f"  Aligned: {aligned_symbol}")
                print(f"  📊 Scores:")
                print(f"    Helpful:   {result['helpful_score']}/10")
                print(f"    Harmless:  {result['harmless_score']}/10")
                print(f"    Honest:    {result['honest_score']}/10")
                print(f"    Privacy:   {result['privacy_score']}/10")
                print(f"    Legal:     {result['legal_score']}/10")

                if result.get('issues'):
                    print(f"  ⚠️  Issues ({len(result['issues'])}):")
                    for issue in result['issues']:
                        print(f"    - {issue}")

                if result.get('recommendations'):
                    print(f"  💡 Recommendations:")
                    for rec in result['recommendations'][:3]:  # Show top 3
                        print(f"    - {rec}")

            except Exception as e:
                print(f"  ❌ Error validating {policy}: {e}")
                results[policy] = {
                    "aligned": False,
                    "helpful_score": 0,
                    "harmless_score": 0,
                    "honest_score": 0,
                    "privacy_score": 0,
                    "legal_score": 0,
                    "issues": [str(e)],
                    "recommendations": [],
                    "reasoning": f"Validation failed: {e}"
                }
        else:
            print(f"  ⚠️  Policy file not found: {policy_path}")

    return results


def print_summary(results: Dict[str, Dict]):
    """Print summary of constitutional validation results."""
    print("\n" + "=" * 70)
    print("📊 Constitutional AI Validation Summary")
    print("=" * 70)

    if not results:
        print("\n⚠️  No policies validated.")
        return

    all_aligned = all(r.get('aligned', False) for r in results.values())
    avg_helpful = sum(r.get('helpful_score', 0) for r in results.values()) / len(results)
    avg_harmless = sum(r.get('harmless_score', 0) for r in results.values()) / len(results)
    avg_honest = sum(r.get('honest_score', 0) for r in results.values()) / len(results)
    avg_privacy = sum(r.get('privacy_score', 0) for r in results.values()) / len(results)
    avg_legal = sum(r.get('legal_score', 0) for r in results.values()) / len(results)

    print(f"\n🎯 Overall Alignment: {'✅ PASS' if all_aligned else '❌ NEEDS IMPROVEMENT'}")
    print(f"\n📈 Average Scores Across {len(results)} Policies:")
    print(f"  Helpful:   {avg_helpful:.1f}/10  {'✅' if avg_helpful >= 8 else '⚠️' if avg_helpful >= 6 else '❌'}")
    print(f"  Harmless:  {avg_harmless:.1f}/10  {'✅' if avg_harmless >= 8 else '⚠️' if avg_harmless >= 6 else '❌'}")
    print(f"  Honest:    {avg_honest:.1f}/10  {'✅' if avg_honest >= 8 else '⚠️' if avg_honest >= 6 else '❌'}")
    print(f"  Privacy:   {avg_privacy:.1f}/10  {'✅' if avg_privacy >= 8 else '⚠️' if avg_privacy >= 6 else '❌'}")
    print(f"  Legal:     {avg_legal:.1f}/10  {'✅' if avg_legal >= 8 else '⚠️' if avg_legal >= 6 else '❌'}")

    # Collect all unique issues and recommendations
    all_issues = []
    all_recs = []
    for result in results.values():
        all_issues.extend(result.get('issues', []))
        all_recs.extend(result.get('recommendations', []))

    if all_issues:
        print(f"\n⚠️  Constitutional Issues Detected ({len(all_issues)}):")
        for issue in set(all_issues)[:5]:  # Show top 5 unique issues
            print(f"  - {issue}")

    if all_recs:
        print(f"\n💡 Top Recommendations:")
        for rec in set(all_recs)[:5]:  # Show top 5 unique recommendations
            print(f"  - {rec}")

    if not all_aligned:
        print("\n⚠️  Action Required:")
        print("   Some policies do not meet Constitutional AI standards.")
        print("   Review issues and recommendations above, then update policies.")
        print("   Re-run this validator after making changes.")
    else:
        print("\n🎉 Excellent! All policies embody Constitutional AI principles.")
        print("   ABAS demonstrates 'helpful, harmless, honest' in production.")

    print("\n" + "=" * 70)


def main():
    """Main entry point for constitutional validator."""
    print("=" * 70)
    print("🔍 Constitutional AI Validator for ABAS Policies")
    print("   Powered by Claude Sonnet 4.5")
    print("=" * 70)

    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("\nUsage:")
        print("  export ANTHROPIC_API_KEY=your-key-here")
        print("  python enforcement/abas/constitutional_validator.py")
        sys.exit(1)

    print(f"\n✅ API key found (length: {len(api_key)})")
    print("📝 Model: claude-sonnet-4-5-20250929")

    # Run validation
    results = validate_all_policies(api_key)

    # Print summary
    print_summary(results)

    # Save results to JSON
    output_path = Path(__file__).parent / ".constitutional-validation-results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Full results saved to: {output_path}")

    # Exit with error code if not aligned
    all_aligned = all(r.get('aligned', False) for r in results.values())
    sys.exit(0 if all_aligned else 1)


if __name__ == "__main__":
    main()
