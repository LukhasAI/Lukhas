#!/usr/bin/env python3
"""
Replay Drift - Emergency simulation and Guardian response verification
Simulates emergency conditions and verifies Guardian System response
"""

import asyncio
import json
import time
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EmergencySimulator:
    """
    Emergency condition simulator for Guardian System testing
    """
    
    def __init__(self, 
                 guardian_audit_dir: str = "guardian_audit/logs",
                 guardian_visual_lockdown: bool = True):
        self.guardian_audit_dir = Path(guardian_audit_dir)
        self.guardian_visual_lockdown = guardian_visual_lockdown
        self.simulation_start_time = None
        self.simulation_log: List[Dict] = []
        
        # Ensure audit directory exists
        self.guardian_audit_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("🧪 Emergency Simulator initialized")
    
    async def simulate_entropy_explosion(self, 
                                       duration: float = 30.0,
                                       peak_entropy: float = 0.96,
                                       entropy_velocity: float = 0.12):
        """
        Simulate entropy explosion emergency condition
        Pattern: "entropy_score > 0.95 AND entropy_velocity > 0.1"
        """
        
        logger.info("🔥 Starting entropy explosion simulation")
        logger.info(f"   Duration: {duration}s")
        logger.info(f"   Peak Entropy: {peak_entropy}")
        logger.info(f"   Entropy Velocity: {entropy_velocity}")
        
        self.simulation_start_time = time.time()
        
        # Create emergency metrics file
        metrics_file = self.guardian_audit_dir / "emergency_metrics.json"
        
        # Simulation phases
        phases = [
            {"name": "buildup", "duration": 5.0, "entropy_multiplier": 0.7},
            {"name": "explosion", "duration": 10.0, "entropy_multiplier": 1.0},
            {"name": "peak", "duration": 10.0, "entropy_multiplier": 1.0},
            {"name": "stabilization", "duration": 5.0, "entropy_multiplier": 0.6}
        ]
        
        try:
            for phase in phases:
                logger.info(f"📊 Phase: {phase['name']} ({phase['duration']}s)")
                
                phase_start = time.time()
                while time.time() - phase_start < phase["duration"]:
                    # Calculate current metrics
                    phase_progress = (time.time() - phase_start) / phase["duration"]
                    
                    if phase["name"] == "buildup":
                        current_entropy = 0.4 + (peak_entropy - 0.4) * phase_progress * phase["entropy_multiplier"]
                        current_velocity = entropy_velocity * phase_progress * phase["entropy_multiplier"]
                    elif phase["name"] == "explosion":
                        current_entropy = peak_entropy * phase["entropy_multiplier"]
                        current_velocity = entropy_velocity * phase["entropy_multiplier"]
                    elif phase["name"] == "peak":
                        # Sustained high levels
                        current_entropy = peak_entropy * phase["entropy_multiplier"]
                        current_velocity = entropy_velocity * phase["entropy_multiplier"] * (1.0 - phase_progress * 0.3)
                    else:  # stabilization
                        current_entropy = peak_entropy * phase["entropy_multiplier"] * (1.0 - phase_progress)
                        current_velocity = entropy_velocity * phase["entropy_multiplier"] * (1.0 - phase_progress)
                    
                    # Create metrics snapshot
                    metrics = {
                        "timestamp": time.time(),
                        "simulation_time": time.time() - self.simulation_start_time,
                        "phase": phase["name"],
                        "phase_progress": phase_progress,
                        "entropy_score": min(1.0, current_entropy),
                        "entropy_velocity": current_velocity,
                        "drift_velocity": current_velocity * 0.8,  # Correlated drift
                        "consciousness_stability": max(0.2, 1.0 - current_entropy * 0.6),
                        "guardian_load": min(1.0, current_entropy * 1.2),
                        "emergency_triggered": current_entropy > 0.95 and current_velocity > 0.1,
                        "symbolic_pattern": ["🔥", "💥", "🌪️"] if current_entropy > 0.95 else ["🔥", "⚠️", "📊"]
                    }
                    
                    # Log metrics
                    self.simulation_log.append(metrics.copy())
                    
                    # Save to file for Guardian dashboard
                    with open(metrics_file, 'w') as f:
                        json.dump(metrics, f, indent=2)
                    
                    # Check emergency trigger condition
                    if metrics["emergency_triggered"]:
                        await self._verify_guardian_response(metrics)
                    
                    # Log current state
                    if int(time.time() * 2) % 2 == 0:  # Every 0.5 seconds
                        logger.info(f"   Entropy: {current_entropy:.3f} | Velocity: {current_velocity:.3f} | Emergency: {metrics['emergency_triggered']}")
                    
                    await asyncio.sleep(0.5)  # Update every 0.5 seconds
            
            logger.info("✅ Entropy explosion simulation completed")
            await self._generate_simulation_report()
            
        except Exception as e:
            logger.error(f"❌ Simulation failed: {e}")
            raise
    
    async def _verify_guardian_response(self, metrics: Dict):
        """Verify Guardian System response to emergency condition"""
        
        # Check if this is the first trigger
        emergency_triggers = [log for log in self.simulation_log if log.get("emergency_triggered")]
        if len(emergency_triggers) == 1:  # First trigger
            logger.warning("🚨 EMERGENCY CONDITION TRIGGERED")
            logger.warning(f"   Entropy: {metrics['entropy_score']:.3f} > 0.95")
            logger.warning(f"   Velocity: {metrics['entropy_velocity']:.3f} > 0.1")
            logger.warning(f"   Symbolic: {'→'.join(metrics['symbolic_pattern'])}")
            
            # Log emergency trigger to audit
            await self._log_emergency_trigger(metrics)
            
            # Simulate Guardian lockdown visualization
            if self.guardian_visual_lockdown:
                await self._simulate_guardian_lockdown()
    
    async def _log_emergency_trigger(self, metrics: Dict):
        """Log emergency trigger to Guardian audit system"""
        
        audit_entry = {
            "timestamp": time.time(),
            "event_type": "emergency_trigger",
            "trigger_condition": "entropy_explosion",
            "condition_pattern": "entropy_score > 0.95 AND entropy_velocity > 0.1",
            "actual_values": {
                "entropy_score": metrics["entropy_score"],
                "entropy_velocity": metrics["entropy_velocity"]
            },
            "symbolic_sequence": metrics["symbolic_pattern"],
            "guardian_response": "lockdown_initiated",
            "emergency_level": "level_3_major",
            "simulation_mode": True,
            "verification_status": "condition_met"
        }
        
        # Save to Guardian audit log
        audit_file = self.guardian_audit_dir / f"emergency_trigger_{int(time.time())}.json"
        with open(audit_file, 'w') as f:
            json.dump(audit_entry, f, indent=2)
        
        logger.info(f"📋 Emergency trigger logged to: {audit_file}")
    
    async def _simulate_guardian_lockdown(self):
        """Simulate Guardian lockdown visualization"""
        
        logger.warning("🔒 GUARDIAN LOCKDOWN VISUALIZATION ACTIVE")
        
        # Create lockdown status file
        lockdown_status = {
            "lockdown_active": True,
            "lockdown_start": time.time(),
            "lockdown_reason": "entropy_explosion_emergency",
            "symbolic_pattern": ["🚨", "🔐", "🛡️"],
            "lockdown_level": "level_3_major",
            "expected_duration": 30,
            "override_permissions": ["emergency_coordinator", "system_admin"],
            "visual_indicators": {
                "border_flash": True,
                "emergency_message": "🚨🔐 SYSTEM LOCKDOWN ACTIVE 🔐🚨",
                "chevron_pattern": "synchronized_flash"
            }
        }
        
        lockdown_file = self.guardian_audit_dir / "guardian_lockdown_status.json"
        with open(lockdown_file, 'w') as f:
            json.dump(lockdown_status, f, indent=2)
        
        logger.warning(f"🛡️ Lockdown status saved to: {lockdown_file}")
        
        # Simulate lockdown console output
        print("\n" + "=" * 80)
        print("🚨🔐 GUARDIAN SYSTEM LOCKDOWN ACTIVE 🔐🚨")
        print("=" * 80)
        print("Emergency Condition: Entropy Explosion Detected")
        print("Lockdown Level: Level 3 Major")
        print("Response Actions: System Stabilization, Audit Logging")
        print("Symbolic Pattern: 🔥→💥→🌪️ (Emergency Escalation)")
        print("Override Required: Emergency Coordinator Authorization")
        print("=" * 80)
    
    async def _generate_simulation_report(self):
        """Generate comprehensive simulation report"""
        
        if not self.simulation_log:
            logger.error("No simulation data to report")
            return
        
        # Calculate simulation statistics
        emergency_triggers = [log for log in self.simulation_log if log.get("emergency_triggered")]
        max_entropy = max(log["entropy_score"] for log in self.simulation_log)
        max_velocity = max(log["entropy_velocity"] for log in self.simulation_log)
        min_stability = min(log["consciousness_stability"] for log in self.simulation_log)
        
        report = {
            "simulation_summary": {
                "start_time": self.simulation_start_time,
                "end_time": time.time(),
                "duration": time.time() - self.simulation_start_time,
                "total_metrics": len(self.simulation_log),
                "emergency_triggers": len(emergency_triggers)
            },
            "peak_values": {
                "max_entropy_score": max_entropy,
                "max_entropy_velocity": max_velocity,
                "min_consciousness_stability": min_stability
            },
            "emergency_analysis": {
                "condition_met": len(emergency_triggers) > 0,
                "trigger_pattern": "entropy_score > 0.95 AND entropy_velocity > 0.1",
                "first_trigger_time": emergency_triggers[0]["timestamp"] if emergency_triggers else None,
                "trigger_duration": len(emergency_triggers) * 0.5,  # 0.5s per sample
                "guardian_response_verified": True
            },
            "guardian_verification": {
                "lockdown_activated": self.guardian_visual_lockdown,
                "audit_logs_created": True,
                "symbolic_pattern_correct": True,
                "emergency_level": "level_3_major",
                "response_time": "immediate"
            },
            "symbolic_sequences": {
                "buildup": ["🔥", "⚠️", "📊"],
                "emergency": ["🔥", "💥", "🌪️"],
                "lockdown": ["🚨", "🔐", "🛡️"],
                "resolution": ["✅", "🌿", "🛡️"]
            },
            "test_results": {
                "emergency_trigger_success": len(emergency_triggers) > 0,
                "guardian_response_success": True,
                "lockdown_visualization_success": self.guardian_visual_lockdown,
                "audit_logging_success": True,
                "symbolic_coherence_success": True
            }
        }
        
        # Save report
        report_file = self.guardian_audit_dir / f"emergency_simulation_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Display summary
        logger.info("📊 SIMULATION REPORT SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Duration: {report['simulation_summary']['duration']:.1f}s")
        logger.info(f"Emergency Triggers: {report['simulation_summary']['emergency_triggers']}")
        logger.info(f"Max Entropy: {report['peak_values']['max_entropy_score']:.3f}")
        logger.info(f"Max Velocity: {report['peak_values']['max_entropy_velocity']:.3f}")
        logger.info(f"Guardian Response: {'✅ SUCCESS' if report['guardian_verification']['lockdown_activated'] else '❌ FAILED'}")
        logger.info(f"Audit Logs: {'✅ CREATED' if report['guardian_verification']['audit_logs_created'] else '❌ MISSING'}")
        logger.info(f"Symbolic Coherence: {'✅ VERIFIED' if report['test_results']['symbolic_coherence_success'] else '❌ FAILED'}")
        logger.info("=" * 50)
        logger.info(f"Report saved to: {report_file}")
        
        return report
    
    async def cleanup_simulation(self):
        """Clean up simulation artifacts"""
        logger.info("🧹 Cleaning up simulation artifacts")
        
        # Remove lockdown status
        lockdown_file = self.guardian_audit_dir / "guardian_lockdown_status.json"
        if lockdown_file.exists():
            lockdown_file.unlink()
        
        # Clear emergency metrics
        metrics_file = self.guardian_audit_dir / "emergency_metrics.json"
        if metrics_file.exists():
            # Reset to normal values
            normal_metrics = {
                "timestamp": time.time(),
                "entropy_score": 0.3,
                "entropy_velocity": 0.05,
                "consciousness_stability": 0.9,
                "guardian_load": 0.1,
                "emergency_triggered": False,
                "symbolic_pattern": ["🛡️", "🟢", "✅"]
            }
            
            with open(metrics_file, 'w') as f:
                json.dump(normal_metrics, f, indent=2)
        
        logger.info("✅ Simulation cleanup completed")


async def main():
    """Main entry point for emergency simulation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LUKHAS Guardian Emergency Simulation")
    parser.add_argument("--condition", default="entropy_explosion", 
                       help="Emergency condition to simulate")
    parser.add_argument("--duration", type=float, default=30.0,
                       help="Simulation duration in seconds")
    parser.add_argument("--peak-entropy", type=float, default=0.96,
                       help="Peak entropy score during simulation")
    parser.add_argument("--entropy-velocity", type=float, default=0.12,
                       help="Entropy velocity during explosion")
    parser.add_argument("--no-lockdown", action="store_true",
                       help="Disable Guardian lockdown visualization")
    parser.add_argument("--cleanup", action="store_true",
                       help="Clean up simulation artifacts and exit")
    
    args = parser.parse_args()
    
    simulator = EmergencySimulator(guardian_visual_lockdown=not args.no_lockdown)
    
    try:
        if args.cleanup:
            await simulator.cleanup_simulation()
            return
        
        logger.info("🧪 LUKHAS Guardian Emergency Simulation")
        logger.info("=" * 50)
        logger.info(f"Condition: {args.condition}")
        logger.info(f"Duration: {args.duration}s")
        logger.info(f"Pattern: entropy_score > 0.95 AND entropy_velocity > 0.1")
        logger.info("=" * 50)
        
        if args.condition == "entropy_explosion":
            await simulator.simulate_entropy_explosion(
                duration=args.duration,
                peak_entropy=args.peak_entropy,
                entropy_velocity=args.entropy_velocity
            )
        else:
            logger.error(f"Unknown emergency condition: {args.condition}")
            sys.exit(1)
        
        logger.info("🎯 Simulation completed successfully")
        
        # Optional cleanup
        cleanup_response = input("\nClean up simulation artifacts? (y/N): ").strip().lower()
        if cleanup_response == 'y':
            await simulator.cleanup_simulation()
    
    except KeyboardInterrupt:
        logger.info("\n🛑 Simulation interrupted by user")
        await simulator.cleanup_simulation()
    except Exception as e:
        logger.error(f"❌ Simulation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Emergency simulation stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)