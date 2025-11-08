#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
DPA Generator Tool.

Generates customized Data Processing Agreement from template.

⚠️ LEGAL DISCLAIMER: Generated documents require legal review before use.
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


def generate_dpa(
    customer_name: str,
    customer_address: str,
    customer_email: str,
    output_file: Path | None = None,
) -> None:
    """Generate customized DPA from template."""

    # Load template
    template_file = Path(__file__).parent.parent / "legal/templates/DATA_PROCESSING_AGREEMENT.md"

    if not template_file.exists():
        print(f"❌ Template not found: {template_file}")
        return

    with open(template_file) as f:
        template = f.read()

    # Replace placeholders
    dpa = template.replace("[CUSTOMER_NAME]", customer_name)
    dpa = dpa.replace("[CUSTOMER_ADDRESS]", customer_address)
    dpa = dpa.replace("[CUSTOMER_EMAIL]", customer_email)
    dpa = dpa.replace("[DATE]", datetime.now().strftime("%Y-%m-%d"))
    dpa = dpa.replace("[LUKHAS_ADDRESS]", "LUKHAS AI GmbH, [Address], EU")  # Update with real address

    # Determine output file
    if output_file is None:
        safe_name = customer_name.lower().replace(" ", "_")
        output_file = Path(f"DPA_{safe_name}_{datetime.now().strftime('%Y%m%d')}.md")

    # Save
    with open(output_file, "w") as f:
        f.write(dpa)

    print(f"✅ DPA generated: {output_file}")
    print()
    print("⚠️  IMPORTANT:")
    print("   1. Review all placeholders (marked with [BRACKETS])")
    print("   2. Have legal counsel review before signing")
    print("   3. Execute Sub-Processor DPAs before using this DPA")
    print("   4. File signed copy securely")


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Generate customized DPA")

    parser.add_argument("customer_name", help="Customer/company name")
    parser.add_argument("customer_address", help="Customer address")
    parser.add_argument("customer_email", help="Customer contact email")
    parser.add_argument("--output", type=Path, help="Output file (default: DPA_<customer>_<date>.md)")

    args = parser.parse_args()

    generate_dpa(
        customer_name=args.customer_name,
        customer_address=args.customer_address,
        customer_email=args.customer_email,
        output_file=args.output,
    )


if __name__ == "__main__":
    main()
