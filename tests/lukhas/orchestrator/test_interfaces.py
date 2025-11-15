import pytest

from lukhas.orchestrator.interfaces import (
    PipelineStage,
    StageInput,
    StageOutput,
)


class MyStageInput:
    def __init__(self, data: int):
        self._data = data

    @property
    def data(self) -> int:
        return self._data


class MyStageOutput:
    def __init__(self, data: str):
        self._data = data

    @property
    def data(self) -> str:
        return self._data


class MyPipelineStage:
    def process(self, input_data: StageInput[int]) -> StageOutput[str]:
        return MyStageOutput(str(input_data.data))


def test_pipeline_stage():
    stage: PipelineStage[int, str] = MyPipelineStage()
    input_data = MyStageInput(123)
    output = stage.process(input_data)
    assert output.data == "123"


def test_stage_input():
    input_data: StageInput[int] = MyStageInput(123)
    assert input_data.data == 123


def test_stage_output():
    output_data: StageOutput[str] = MyStageOutput("123")
    assert output_data.data == "123"
