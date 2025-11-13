from typing import Protocol, TypeVar

T_in = TypeVar("T_in", contravariant=True)
T_out = TypeVar("T_out", covariant=True)


class StageInput(Protocol[T_in]):
    """Represents the input to a pipeline stage."""

    @property
    def data(self) -> T_in:
        ...


class StageOutput(Protocol[T_out]):
    """Represents the output of a pipeline stage."""

    @property
    def data(self) -> T_out:
        ...


class PipelineStage(Protocol[T_in, T_out]):
    """Represents a single stage in a pipeline."""

    def process(self, input_data: StageInput[T_in]) -> StageOutput[T_out]:
        ...
