"""Minimal prime oscillator stub"""


class PrimeHarmonicOscillator:

    def __init__(self, prime_frequency=2.0):
        self.prime_frequency = prime_frequency
        self.harmonics = []

    def generate_harmonic(self, order=1):
        return self.prime_frequency * order

    def get_harmonic_series(self, max_order=5):
        return [self.generate_harmonic(i) for i in range(1, max_order + 1)]
