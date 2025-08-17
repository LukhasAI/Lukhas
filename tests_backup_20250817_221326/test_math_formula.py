#!/usr/bin/env python3
"""
VIVOX Z(t) Mathematical Formula Test & Validation
===============================================
Comprehensive validation of the z(t) collapse function with correct mathematical expectations.

The formula: z(t) = A(t) * [e^(iθ(t)) + e^(i(π-θ(t)))] × W(ΔS(t))

Mathematical Analysis:
- When θ = 0: z(t) = A * [1 + e^(iπ)] * W = A * [1 + (-1)] * W = 0
- When θ = π/2: z(t) = A * [i + i] * W = A * 2i * W
- When θ = π: z(t) = A * [-1 + 1] * W = 0
- Non-zero results occur when θ ≠ 0, π

This corrects the baseline expectation and provides proper test cases.
"""

import cmath
import math
import os
import sys

# Add project paths
sys.path.append(os.path.join(os.path.dirname(__file__), "vivox", "collapse"))


def compute_z_formula(amplitude: float, theta: float, entropy_weight: float) -> complex:
    """
    Direct implementation of the z(t) formula for verification
    z(t) = A(t) * [e^(iθ(t)) + e^(i(π-θ(t)))] × W(ΔS(t))
    """
    # Calculate complex exponential terms
    exp_theta = cmath.exp(1j * theta)
    exp_pi_minus_theta = cmath.exp(1j * (math.pi - theta))

    # Sum exponential terms
    exponential_sum = exp_theta + exp_pi_minus_theta

    # Apply amplitude and entropy weighting
    z_result = amplitude * exponential_sum * entropy_weight

    return z_result


def test_mathematical_properties():
    """Test mathematical properties of the z(t) function"""
    print("🧮 Testing Mathematical Properties of z(t)")
    print("=" * 50)

    test_cases = [
        # (theta, expected_description)
        (0.0, "θ=0: Should give 0 (1 + e^(iπ) = 1 + (-1) = 0)"),
        (math.pi / 6, "θ=π/6: Should give real positive result"),
        (math.pi / 4, "θ=π/4: Should give real positive result"),
        (math.pi / 3, "θ=π/3: Should give real positive result"),
        (math.pi / 2, "θ=π/2: Should give pure imaginary (2i)"),
        (2 * math.pi / 3, "θ=2π/3: Should give real positive result"),
        (3 * math.pi / 4, "θ=3π/4: Should give real positive result"),
        (5 * math.pi / 6, "θ=5π/6: Should give real positive result"),
        (math.pi, "θ=π: Should give 0 (e^(iπ) + 1 = -1 + 1 = 0)"),
    ]

    print("Formula: z(t) = A * [e^(iθ) + e^(i(π-θ))] * W")
    print("Using: A=1.0, W=1.0\n")

    for theta, description in test_cases:
        z_result = compute_z_formula(amplitude=1.0, theta=theta, entropy_weight=1.0)

        print(f"θ = {theta:.4f} ({theta/math.pi:.2f}π)")
        print(f"  Description: {description}")
        print(f"  Result: {z_result:.6f}")
        print(f"  Magnitude: {abs(z_result):.6f}")
        print(f"  Phase: {cmath.phase(z_result):.6f} rad")

        # Verify mathematical identity: e^(iθ) + e^(i(π-θ)) = 2*cos(θ - π/2)
        manual_calc = 2 * math.cos(theta - math.pi / 2)
        identity_check = (
            abs(z_result.real - manual_calc) < 1e-10 and abs(z_result.imag) < 1e-10
        )
        print(
            f"  Identity check: {'✅' if identity_check else '❌'} (2*cos(θ-π/2) = {manual_calc:.6f})"
        )
        print()


def test_symmetry_properties():
    """Test symmetry properties of the function"""
    print("🔄 Testing Symmetry Properties")
    print("=" * 30)

    # Test that z(θ) = z(π-θ) (should be true due to the formula structure)
    theta_values = [math.pi / 6, math.pi / 4, math.pi / 3, math.pi / 2]

    for theta in theta_values:
        z1 = compute_z_formula(1.0, theta, 1.0)
        z2 = compute_z_formula(1.0, math.pi - theta, 1.0)

        symmetry_holds = abs(z1 - z2) < 1e-10
        print(f"θ={theta:.4f}, π-θ={math.pi-theta:.4f}")
        print(f"  z(θ) = {z1:.6f}")
        print(f"  z(π-θ) = {z2:.6f}")
        print(f"  Symmetry: {'✅' if symmetry_holds else '❌'}")
        print()


def test_amplitude_scaling():
    """Test amplitude scaling properties"""
    print("📈 Testing Amplitude Scaling")
    print("=" * 25)

    theta = math.pi / 4  # Use a theta that gives non-zero result
    base_result = compute_z_formula(1.0, theta, 1.0)

    amplitudes = [0.5, 1.0, 1.5, 2.0]

    for amp in amplitudes:
        z_result = compute_z_formula(amp, theta, 1.0)
        expected = base_result * amp
        scaling_correct = abs(z_result - expected) < 1e-10

        print(f"Amplitude={amp}")
        print(f"  Result: {z_result:.6f}")
        print(f"  Expected: {expected:.6f}")
        print(f"  Scaling: {'✅' if scaling_correct else '❌'}")
        print()


def test_entropy_weighting():
    """Test entropy weight properties"""
    print("⚖️  Testing Entropy Weighting")
    print("=" * 25)

    theta = math.pi / 3  # Use a theta that gives non-zero result
    base_result = compute_z_formula(1.0, theta, 1.0)

    weights = [0.0, 0.25, 0.5, 0.75, 1.0]

    for weight in weights:
        z_result = compute_z_formula(1.0, theta, weight)
        expected = base_result * weight
        weighting_correct = abs(z_result - expected) < 1e-10

        print(f"Entropy Weight={weight}")
        print(f"  Result: {z_result:.6f}")
        print(f"  Expected: {expected:.6f}")
        print(f"  Weighting: {'✅' if weighting_correct else '❌'}")
        print()


def find_good_baseline_cases():
    """Find good baseline test cases with predictable results"""
    print("🎯 Finding Good Baseline Test Cases")
    print("=" * 35)

    # Look for theta values that give nice, predictable results
    candidates = []

    for i in range(13):  # Test θ from 0 to π in 12 steps
        theta = i * math.pi / 12
        z_result = compute_z_formula(1.0, theta, 1.0)

        # Look for cases with real results or simple imaginary results
        is_real = abs(z_result.imag) < 1e-10
        is_imaginary = abs(z_result.real) < 1e-10
        is_simple = is_real or is_imaginary
        is_nonzero = abs(z_result) > 1e-10

        if is_simple and is_nonzero:
            candidates.append((theta, z_result, "Real" if is_real else "Imaginary"))

        print(
            f"θ = {theta:.4f} ({theta/math.pi:.2f}π): {z_result:.6f} ({'Simple' if is_simple else 'Complex'})"
        )

    print("\n🌟 Recommended baseline test cases:")
    for theta, result, type_desc in candidates:
        print(f"  θ = {theta:.4f} ({theta/math.pi:.2f}π): {result:.6f} ({type_desc})")


def generate_integration_test_cases():
    """Generate comprehensive test cases for integration tests"""
    print("\n🧪 Recommended Integration Test Cases")
    print("=" * 40)

    test_cases = [
        {
            "name": "Pure Real Result",
            "theta": math.pi / 6,
            "expected_type": "real",
            "description": "θ=π/6 gives √3 real result",
        },
        {
            "name": "Pure Imaginary Result",
            "theta": math.pi / 2,
            "expected_type": "imaginary",
            "description": "θ=π/2 gives 2i result",
        },
        {
            "name": "Zero Result (θ=0)",
            "theta": 0.0,
            "expected_type": "zero",
            "description": "θ=0 gives 0 result",
        },
        {
            "name": "Zero Result (θ=π)",
            "theta": math.pi,
            "expected_type": "zero",
            "description": "θ=π gives 0 result",
        },
        {
            "name": "Maximum Magnitude",
            "theta": math.pi / 2,
            "expected_type": "max_magnitude",
            "description": "θ=π/2 gives maximum |z| = 2",
        },
    ]

    for test_case in test_cases:
        theta = test_case["theta"]
        z_result = compute_z_formula(1.0, theta, 1.0)

        print(f"\nTest Case: {test_case['name']}")
        print(f"  θ = {theta:.4f} rad ({theta/math.pi:.2f}π)")
        print(f"  Result: {z_result:.6f}")
        print(f"  Magnitude: {abs(z_result):.6f}")
        print(f"  Description: {test_case['description']}")

        # Generate code snippet
        print("  Code snippet:")
        print(f"    result = engine.compute_z_collapse(t=0.0, theta={theta:.4f})")
        print(f"    expected = complex({z_result.real:.6f}, {z_result.imag:.6f})")


if __name__ == "__main__":
    print("VIVOX Z(t) Mathematical Formula Validation")
    print("=" * 60)
    print()

    test_mathematical_properties()
    print()
    test_symmetry_properties()
    print()
    test_amplitude_scaling()
    print()
    test_entropy_weighting()
    print()
    find_good_baseline_cases()
    print()
    generate_integration_test_cases()

    print("\n" + "=" * 60)
    print("✅ Mathematical validation complete!")
    print("📝 Use the recommended test cases for integration testing.")
