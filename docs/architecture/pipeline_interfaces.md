# Pipeline Stage Interface Contracts

This document outlines the interface contracts for pipeline stages in the Lukhas orchestration system. These contracts are defined as `Protocol`s in the `lukhas.orchestrator.interfaces` module.

## `PipelineStage`

A `PipelineStage` represents a single stage in a processing pipeline. It is a generic protocol that takes two type variables:

-   `T_in`: The type of the input data.
-   `T_out`: The type of the output data.

A `PipelineStage` must implement a `process` method that takes a `StageInput` and returns a `StageOutput`.

## `StageInput`

A `StageInput` represents the input to a pipeline stage. It is a generic protocol that takes one type variable:

-   `T_in`: The type of the input data.

A `StageInput` must have a `data` property that returns the input data.

## `StageOutput`

A `StageOutput` represents the output of a pipeline stage. It is a generic protocol that takes one type variable:

-   `T_out`: The type of the output data.

A `StageOutput` must have a `data` property that returns the output data.
