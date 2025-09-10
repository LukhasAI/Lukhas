from dataclasses import dataclass
from enum import Enum


class AdaptationStrategy(Enum):
    BALANCED = "balanced"


@dataclass
class ConvergenceSignal:
    pass


class DynamicLearningRateModulator:
    pass
