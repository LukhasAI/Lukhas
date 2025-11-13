"""LUKHAS CLI commands."""
import argparse
import time


def regret_demo():
    """Run 2-minute regret signature demo."""
    print("=== LUKHAS Regret Demo ===\n")
    print("Running 2-minute demonstration of regret signatures...\n")

    # Simulate dream generation with regret tracking
    from oneiric.core.generator import DreamGenerator, SimpleEventBus

    bus = SimpleEventBus()
    generator = DreamGenerator(event_bus=bus)

    # Generate several dreams
    dreams = [
        {"seed_content": "Peaceful meadow", "themes": ["calm", "nature"], "intensity": 0.3},
        {"seed_content": "Stormy ocean", "themes": ["fear", "anxiety"], "intensity": 0.8},
        {"seed_content": "Mountain peak", "themes": ["achievement", "joy"], "intensity": 0.6},
    ]

    print("Generating dreams with regret signatures...\n")

    for i, context in enumerate(dreams, 1):
        dream = generator.synthesize_dream(context)
        sig = generator.get_last_signature()

        print(f"Dream {i}: {dream['content']}")
        print(f"  Themes: {', '.join(dream['themes'])}")
        print(f"  Regret Signature:")
        print(f"    Valence: {sig['valence']:.2f}")
        print(f"    Arousal: {sig['arousal']:.2f}")
        print(f"    Cause: {sig['cause_tag']}")
        print()

        time.sleep(0.5)

    # Show fold/regret stats
    print("=== Statistics ===")
    print(f"Total dreams generated: {len(bus.events)}")
    print(f"Events emitted: {len(bus.events)}")
    print(f"Average valence: {sum(e['data']['valence'] for e in bus.events) / len(bus.events):.2f}")
    print(f"Average arousal: {sum(e['data']['arousal'] for e in bus.events) / len(bus.events):.2f}")
    print("\nDemo complete!")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="LUKHAS AI CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Add regret demo command
    subparsers.add_parser("demo-regret", help="Run regret signature demo")

    args = parser.parse_args()

    if args.command == "demo-regret":
        regret_demo()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
