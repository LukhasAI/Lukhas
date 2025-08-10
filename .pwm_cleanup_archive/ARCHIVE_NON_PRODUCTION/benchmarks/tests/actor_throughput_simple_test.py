#!/usr/bin/env python3
"""
Simple Actor Benchmark Test - No external dependencies
Tests basic actor message throughput without complex imports
"""

import asyncio
import json
import queue
import threading
import time
from datetime import datetime


class SimpleActor:
    """Lightweight actor implementation for benchmarking."""

    def __init__(self, actor_id):
        self.actor_id = actor_id
        self.message_count = 0
        self.mailbox = queue.Queue()
        self.running = True
        self.thread = threading.Thread(target=self._process_messages)
        self.thread.daemon = True
        self.thread.start()

    def send_message(self, message):
        """Send a message to this actor."""
        if self.running:
            self.mailbox.put(message)

    def _process_messages(self):
        """Process messages in a loop."""
        while self.running:
            try:
                message = self.mailbox.get(timeout=0.1)
                self._handle_message(message)
            except queue.Empty:
                continue

    def _handle_message(self, message):
        """Handle a single message - just count it."""
        self.message_count += 1

    def stop(self):
        """Stop the actor."""
        self.running = False
        self.thread.join(timeout=1)

    def get_stats(self):
        """Get actor statistics."""
        return {
            "actor_id": self.actor_id,
            "messages_processed": self.message_count,
            "queue_size": self.mailbox.qsize(),
        }


class SimpleBenchmark:
    """Simple benchmark runner."""

    def __init__(self):
        self.actors = []
        self.results = {}

    def create_actors(self, num_actors):
        """Create a pool of actors."""
        print(f"Creating {num_actors} actors...")
        for i in range(num_actors):
            actor = SimpleActor(f"actor_{i}")
            self.actors.append(actor)
        print(f"✅ Created {len(self.actors)} actors")

    def send_messages(self, num_messages):
        """Send messages to actors in round-robin fashion."""
        print(f"Sending {num_messages} messages...")

        start_time = time.time()

        for i in range(num_messages):
            actor_index = i % len(self.actors)
            message = {"id": i, "data": f"test_message_{i}", "timestamp": time.time()}
            self.actors[actor_index].send_message(message)

        # Wait for processing
        print("Waiting for message processing...")
        time.sleep(1)  # Give actors time to process

        end_time = time.time()
        elapsed = end_time - start_time

        return elapsed

    def collect_stats(self):
        """Collect statistics from all actors."""
        total_processed = 0
        stats = []

        for actor in self.actors:
            actor_stats = actor.get_stats()
            stats.append(actor_stats)
            total_processed += actor_stats["messages_processed"]

        return total_processed, stats

    def cleanup(self):
        """Stop all actors."""
        print("Stopping actors...")
        for actor in self.actors:
            actor.stop()
        self.actors.clear()

    def run_test(self, num_actors=100, num_messages=10000):
        """Run the complete benchmark test."""
        print("🚀 SIMPLE ACTOR BENCHMARK TEST")
        print("=" * 50)
        print(f"Test started: {datetime.now()}")
        print(f"Actors: {num_actors}")
        print(f"Messages: {num_messages}")
        print("-" * 50)

        try:
            # Create actors
            self.create_actors(num_actors)

            # Send messages and measure time
            elapsed = self.send_messages(num_messages)

            # Collect final stats
            total_processed, actor_stats = self.collect_stats()

            # Calculate metrics
            messages_per_second = total_processed / elapsed if elapsed > 0 else 0

            # Results
            results = {
                "test_timestamp": datetime.now().isoformat(),
                "configuration": {
                    "num_actors": num_actors,
                    "num_messages": num_messages,
                },
                "performance": {
                    "total_messages_sent": num_messages,
                    "total_messages_processed": total_processed,
                    "elapsed_time_seconds": elapsed,
                    "messages_per_second": messages_per_second,
                    "throughput_description": f"{messages_per_second:,.0f} msg/sec",
                },
                "actor_stats": actor_stats[:5],  # First 5 actors for brevity
            }

            # Display results
            print("\n📊 BENCHMARK RESULTS")
            print("=" * 50)
            print(f"Messages Sent: {num_messages:,}")
            print(f"Messages Processed: {total_processed:,}")
            print(f"Processing Rate: {(total_processed/num_messages)*100:.1f}%")
            print(f"Elapsed Time: {elapsed:.3f} seconds")
            print(f"Throughput: {messages_per_second:,.0f} messages/sec")

            if messages_per_second >= 33000:
                print("✅ EXCEEDS 33K msg/sec target!")
            elif messages_per_second >= 25000:
                print("✅ GOOD performance (25K+ msg/sec)")
            elif messages_per_second >= 10000:
                print("⚠️  MODERATE performance (10K+ msg/sec)")
            else:
                print("❌ BELOW expected performance")

            # Save results
            with open("simple_actor_benchmark_results.json", "w") as f:
                json.dump(results, f, indent=2)
            print("\n💾 Results saved to: simple_actor_benchmark_results.json")

            return results

        except Exception as e:
            print(f"❌ Benchmark failed: {e}")
            import traceback

            traceback.print_exc()
            return None

        finally:
            self.cleanup()


async def run_async_test():
    """Run benchmark in async context."""
    benchmark = SimpleBenchmark()

    # Test different configurations
    configs = [
        (50, 5000),  # Small test
        (100, 10000),  # Medium test
        (200, 20000),  # Large test
    ]

    all_results = []

    for num_actors, num_messages in configs:
        print(f"\n🧪 Testing {num_actors} actors with {num_messages} messages")
        result = benchmark.run_test(num_actors, num_messages)
        if result:
            all_results.append(result)

        # Brief pause between tests
        await asyncio.sleep(0.5)

    # Summary
    if all_results:
        print("\n📈 SUMMARY OF ALL TESTS")
        print("=" * 50)
        for i, result in enumerate(all_results, 1):
            perf = result["performance"]
            config = result["configuration"]
            print(
                f"Test {i}: {config['num_actors']} actors, {config['num_messages']} msgs"
            )
            print(f"  Throughput: {perf['messages_per_second']:,.0f} msg/sec")

        best_throughput = max(
            r["performance"]["messages_per_second"] for r in all_results
        )
        print(f"\n🏆 Best Throughput: {best_throughput:,.0f} messages/sec")

        if best_throughput >= 33000:
            print("✅ VALIDATES 33K+ msg/sec claim!")
        else:
            print(f"❌ Does not reach 33K msg/sec (achieved: {best_throughput:,.0f})")


if __name__ == "__main__":
    print("Starting simple actor benchmark...")
    try:
        asyncio.run(run_async_test())
    except KeyboardInterrupt:
        print("\n⚠️  Benchmark interrupted by user")
    except Exception as e:
        print(f"\n❌ Benchmark error: {e}")
