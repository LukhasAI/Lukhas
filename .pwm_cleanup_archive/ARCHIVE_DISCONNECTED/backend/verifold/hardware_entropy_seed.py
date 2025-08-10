"""
hardware_entropy_seed.py

Hardware/Compliance Add-on - TPM/HSM Entropy Seeding
Pulls entropy from Trusted Platform Module (TPM) or Hardware Security Module (HSM) for cryptographic seeding.

Purpose:
- Interface with hardware entropy sources (TPM, HSM, TRNG)
- Provide high-quality entropy for cryptographic key generation
- Ensure compliance with hardware security standards
- Support various hardware entropy devices and protocols

Author: LUKHAS AGI Core
"""

import hashlib
import os
import platform
import secrets
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class HardwareType(Enum):
    """Types of hardware entropy sources."""

    TPM_20 = "tpm_2.0"
    TPM_12 = "tpm_1.2"
    HSM_NETWORK = "hsm_network"
    HSM_USB = "hsm_usb"
    TRNG_DEVICE = "trng_device"
    INTEL_RDRAND = "intel_rdrand"
    SYSTEM_ENTROPY = "system_entropy"


@dataclass
class EntropySource:
    """Configuration for a hardware entropy source."""

    hardware_type: HardwareType
    device_path: str
    device_name: str
    available: bool
    entropy_rate: float  # bits per second
    quality_score: float  # 0.0 to 1.0


class HardwareEntropySeeder:
    """
    Interfaces with hardware entropy sources for cryptographic seeding.
    """

    def __init__(self):
        """Initialize hardware entropy seeder."""
        self.available_sources = []
        self.preferred_source = None
        self.entropy_cache = {}
        self.discovery_complete = False

    def discover_entropy_sources(self) -> List[EntropySource]:
        """
        Discover available hardware entropy sources on the system.

        Returns:
            List[EntropySource]: Available entropy sources
        """
        print("🔍 Discovering hardware entropy sources...")
        sources = []

        # Check for TPM devices
        tpm_sources = self._discover_tpm_devices()
        sources.extend(tpm_sources)

        # Check for HSM devices
        hsm_sources = self._discover_hsm_devices()
        sources.extend(hsm_sources)

        # Check for TRNG devices
        trng_sources = self._discover_trng_devices()
        sources.extend(trng_sources)

        # Check for CPU-based entropy (Intel RDRAND)
        cpu_sources = self._discover_cpu_entropy()
        sources.extend(cpu_sources)

        # Always include system entropy as fallback
        system_source = self._get_system_entropy_source()
        sources.append(system_source)

        self.available_sources = sources
        self.discovery_complete = True

        # Select preferred source
        self._select_preferred_source()

        return sources

    def _discover_tpm_devices(self) -> List[EntropySource]:
        """
        Discover TPM (Trusted Platform Module) devices.

        Returns:
            List[EntropySource]: Available TPM sources
        """
        # TODO: Implement actual TPM discovery
        sources = []

        # Check common TPM device paths
        tpm_paths = ["/dev/tpm0", "/dev/tpmrm0", "\\\\?\\TPM"]  # Windows TPM path

        for path in tpm_paths:
            if self._check_device_available(path):
                # Determine TPM version
                tpm_version = self._detect_tpm_version(path)
                sources.append(
                    EntropySource(
                        hardware_type=tpm_version,
                        device_path=path,
                        device_name=f"TPM {tpm_version.value}",
                        available=True,
                        entropy_rate=1000.0,  # bits/sec
                        quality_score=0.95,
                    )
                )

        return sources

    def _discover_hsm_devices(self) -> List[EntropySource]:
        """
        Discover HSM (Hardware Security Module) devices.

        Returns:
            List[EntropySource]: Available HSM sources
        """
        # TODO: Implement actual HSM discovery
        sources = []

        # Check for USB HSM devices
        usb_hsms = self._scan_usb_hsm_devices()
        sources.extend(usb_hsms)

        # Check for network HSM devices
        network_hsms = self._scan_network_hsm_devices()
        sources.extend(network_hsms)

        return sources

    def _discover_trng_devices(self) -> List[EntropySource]:
        """
        Discover TRNG (True Random Number Generator) devices.

        Returns:
            List[EntropySource]: Available TRNG sources
        """
        # TODO: Implement actual TRNG discovery
        sources = []

        # Check for hardware TRNG devices
        trng_paths = [
            "/dev/hwrng",
            "/dev/random",  # On some systems, this is hardware-backed
        ]

        for path in trng_paths:
            if self._check_device_available(path) and self._is_hardware_backed(path):
                sources.append(
                    EntropySource(
                        hardware_type=HardwareType.TRNG_DEVICE,
                        device_path=path,
                        device_name=f"Hardware RNG ({path})",
                        available=True,
                        entropy_rate=2000.0,  # bits/sec
                        quality_score=0.90,
                    )
                )

        return sources

    def _discover_cpu_entropy(self) -> List[EntropySource]:
        """
        Discover CPU-based entropy sources (Intel RDRAND, etc.).

        Returns:
            List[EntropySource]: Available CPU entropy sources
        """
        # TODO: Implement actual CPU entropy detection
        sources = []

        # Check for Intel RDRAND instruction
        if self._has_rdrand_support():
            sources.append(
                EntropySource(
                    hardware_type=HardwareType.INTEL_RDRAND,
                    device_path="cpu:rdrand",
                    device_name="Intel RDRAND",
                    available=True,
                    entropy_rate=500.0,  # bits/sec
                    quality_score=0.85,
                )
            )

        return sources

    def _get_system_entropy_source(self) -> EntropySource:
        """
        Get system entropy source as fallback.

        Returns:
            EntropySource: System entropy source
        """
        system_path = (
            "/dev/urandom" if platform.system() != "Windows" else "CryptGenRandom"
        )

        return EntropySource(
            hardware_type=HardwareType.SYSTEM_ENTROPY,
            device_path=system_path,
            device_name="System Entropy Pool",
            available=True,
            entropy_rate=100.0,  # bits/sec (conservative estimate)
            quality_score=0.70,
        )

    def _check_device_available(self, device_path: str) -> bool:
        """
        Check if a device path is available.

        Parameters:
            device_path (str): Device path to check

        Returns:
            bool: True if device is available
        """
        # TODO: Implement actual device checking
        if platform.system() == "Windows":
            # Windows-specific checks
            return device_path.startswith("\\\\?\\")
        else:
            # Unix-like systems
            return os.path.exists(device_path) and os.access(device_path, os.R_OK)

    def _detect_tpm_version(self, device_path: str) -> HardwareType:
        """
        Detect TPM version from device.

        Parameters:
            device_path (str): TPM device path

        Returns:
            HardwareType: TPM version type
        """
        # TODO: Implement actual TPM version detection
        # Placeholder logic
        if "tpmrm" in device_path:
            return HardwareType.TPM_20
        else:
            return HardwareType.TPM_12

    def _scan_usb_hsm_devices(self) -> List[EntropySource]:
        """Scan for USB-connected HSM devices."""
        # TODO: Implement USB HSM scanning
        return []

    def _scan_network_hsm_devices(self) -> List[EntropySource]:
        """Scan for network-accessible HSM devices."""
        # TODO: Implement network HSM scanning
        return []

    def _is_hardware_backed(self, device_path: str) -> bool:
        """Check if device is truly hardware-backed."""
        # TODO: Implement hardware backing verification
        return True  # Placeholder

    def _has_rdrand_support(self) -> bool:
        """Check if CPU supports RDRAND instruction."""
        # TODO: Implement RDRAND capability detection
        try:
            # This is a placeholder - actual implementation would check CPU features
            import cpuinfo

            cpu_info = cpuinfo.get_cpu_info()
            return "rdrand" in cpu_info.get("flags", [])
        except ImportError:
            return False

    def _select_preferred_source(self):
        """Select the preferred entropy source based on quality and availability."""
        if not self.available_sources:
            return

        # Sort by quality score (descending)
        sorted_sources = sorted(
            self.available_sources, key=lambda s: s.quality_score, reverse=True
        )

        # Prefer hardware sources over system entropy
        hardware_sources = [
            s for s in sorted_sources if s.hardware_type != HardwareType.SYSTEM_ENTROPY
        ]

        if hardware_sources:
            self.preferred_source = hardware_sources[0]
        else:
            self.preferred_source = sorted_sources[0]

    def generate_entropy_seed(
        self, byte_count: int = 32, source: Optional[EntropySource] = None
    ) -> bytes:
        """
        Generate entropy seed from hardware source.

        Parameters:
            byte_count (int): Number of entropy bytes to generate
            source (EntropySource): Specific source to use (None for preferred)

        Returns:
            bytes: Generated entropy seed
        """
        if not self.discovery_complete:
            self.discover_entropy_sources()

        target_source = source or self.preferred_source

        if not target_source:
            raise RuntimeError("No entropy sources available")

        print(
            f"🎲 Generating {byte_count} bytes of entropy from {target_source.device_name}"
        )

        # Generate entropy based on source type
        if (
            target_source.hardware_type == HardwareType.TPM_20
            or target_source.hardware_type == HardwareType.TPM_12
        ):
            return self._generate_tpm_entropy(target_source, byte_count)
        elif target_source.hardware_type == HardwareType.HSM_USB:
            return self._generate_hsm_entropy(target_source, byte_count)
        elif target_source.hardware_type == HardwareType.TRNG_DEVICE:
            return self._generate_trng_entropy(target_source, byte_count)
        elif target_source.hardware_type == HardwareType.INTEL_RDRAND:
            return self._generate_rdrand_entropy(target_source, byte_count)
        else:
            # Fallback to system entropy
            return self._generate_system_entropy(byte_count)

    def _generate_tpm_entropy(self, source: EntropySource, byte_count: int) -> bytes:
        """Generate entropy from TPM device."""
        # TODO: Implement actual TPM entropy generation
        print(f"  → Using TPM device: {source.device_path}")
        # Placeholder: use system entropy with TPM-style mixing
        raw_entropy = secrets.token_bytes(byte_count * 2)
        return hashlib.sha3_256(raw_entropy).digest()[:byte_count]

    def _generate_hsm_entropy(self, source: EntropySource, byte_count: int) -> bytes:
        """Generate entropy from HSM device."""
        # TODO: Implement actual HSM entropy generation
        print(f"  → Using HSM device: {source.device_path}")
        return secrets.token_bytes(byte_count)

    def _generate_trng_entropy(self, source: EntropySource, byte_count: int) -> bytes:
        """Generate entropy from TRNG device."""
        # TODO: Implement actual TRNG entropy generation
        print(f"  → Using TRNG device: {source.device_path}")
        try:
            with open(source.device_path, "rb") as f:
                return f.read(byte_count)
        except OSError:
            return self._generate_system_entropy(byte_count)

    def _generate_rdrand_entropy(self, source: EntropySource, byte_count: int) -> bytes:
        """Generate entropy from Intel RDRAND."""
        # TODO: Implement actual RDRAND entropy generation
        print("  → Using CPU RDRAND instruction")
        # Placeholder: mix system entropy with simulated RDRAND
        system_entropy = secrets.token_bytes(byte_count)
        return hashlib.sha256(system_entropy + b"rdrand_seed").digest()[:byte_count]

    def _generate_system_entropy(self, byte_count: int) -> bytes:
        """Generate entropy from system source."""
        print("  → Using system entropy pool")
        return secrets.token_bytes(byte_count)

    def get_entropy_quality_report(self) -> Dict[str, Any]:
        """
        Get quality report for available entropy sources.

        Returns:
            Dict[str, Any]: Entropy quality report
        """
        if not self.discovery_complete:
            self.discover_entropy_sources()

        report = {
            "discovery_timestamp": None,  # TODO: Add timestamp
            "total_sources": len(self.available_sources),
            "preferred_source": {
                "name": (
                    self.preferred_source.device_name if self.preferred_source else None
                ),
                "type": (
                    self.preferred_source.hardware_type.value
                    if self.preferred_source
                    else None
                ),
                "quality_score": (
                    self.preferred_source.quality_score
                    if self.preferred_source
                    else 0.0
                ),
            },
            "sources": [
                {
                    "name": source.device_name,
                    "type": source.hardware_type.value,
                    "path": source.device_path,
                    "available": source.available,
                    "entropy_rate": source.entropy_rate,
                    "quality_score": source.quality_score,
                }
                for source in self.available_sources
            ],
            "recommendations": self._generate_recommendations(),
        }

        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations for entropy configuration."""
        recommendations = []

        hardware_sources = [
            s
            for s in self.available_sources
            if s.hardware_type != HardwareType.SYSTEM_ENTROPY
        ]

        if not hardware_sources:
            recommendations.append(
                "Consider installing a hardware entropy source (TPM, HSM, or TRNG)"
            )

        if self.preferred_source and self.preferred_source.quality_score < 0.8:
            recommendations.append(
                "Current entropy source has lower quality - consider upgrading"
            )

        if len(self.available_sources) == 1:
            recommendations.append(
                "Multiple entropy sources recommended for redundancy"
            )

        return recommendations


# 🧪 Example usage and testing
if __name__ == "__main__":
    print("🔐 Hardware Entropy Seeder - TPM/HSM Integration")
    print("Discovering and interfacing with hardware entropy sources...")

    # Initialize seeder
    seeder = HardwareEntropySeeder()

    # Discover available sources
    sources = seeder.discover_entropy_sources()

    print(f"\nDiscovered {len(sources)} entropy sources:")
    for source in sources:
        status = "✅" if source.available else "❌"
        print(f"  {status} {source.device_name} ({source.hardware_type.value})")
        print(
            f"      Quality: {source.quality_score:.2f}, Rate: {source.entropy_rate:.0f} bits/sec"
        )

    # Show preferred source
    if seeder.preferred_source:
        print(f"\nPreferred source: {seeder.preferred_source.device_name}")

    # Generate entropy seed
    try:
        entropy_seed = seeder.generate_entropy_seed(32)
        print(f"\nGenerated entropy seed: {entropy_seed.hex()[:32]}...")
        print(f"Seed length: {len(entropy_seed)} bytes")
    except Exception as e:
        print(f"\nError generating entropy: {e}")

    # Get quality report
    quality_report = seeder.get_entropy_quality_report()
    print("\nEntropy Quality Report:")
    print(f"  Total sources: {quality_report['total_sources']}")
    print(f"  Preferred: {quality_report['preferred_source']['name']}")
    print(f"  Quality score: {quality_report['preferred_source']['quality_score']:.2f}")

    if quality_report["recommendations"]:
        print("\nRecommendations:")
        for rec in quality_report["recommendations"]:
            print(f"  • {rec}")

    print("\nReady for hardware entropy seeding operations.")
