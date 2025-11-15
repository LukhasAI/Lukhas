import json
import os
import random
from unittest.mock import MagicMock, patch

import pytest
from labs.consciousness.dream.expand.evolution import (
    EvolutionEngine,
    StrategyGenome,
    save_strategy,
    load_strategy,
)

@pytest.fixture(autouse=True)
def enable_evolution(monkeypatch):
    """Enable evolution for all tests in this module."""
    monkeypatch.setattr("labs.consciousness.dream.expand.evolution.ENABLED", True)

@pytest.fixture
def genome():
    """Fixture for a StrategyGenome instance."""
    return StrategyGenome()


@pytest.fixture
def engine():
    """Fixture for an EvolutionEngine instance."""
    return EvolutionEngine(population_size=10)


def test_strategy_genome_initialization(genome):
    """Test StrategyGenome initialization with default and custom configs."""
    assert 0.0 <= genome.genes["alignment_threshold"] <= 1.0
    assert genome.fitness is None
    assert genome.generation == 0

    custom_config = {
        "alignment_threshold": 0.9,
        "drift_threshold": -0.5,  # Should be clamped
        "generation": 5,
    }
    custom_genome = StrategyGenome(custom_config)
    assert custom_genome.genes["alignment_threshold"] == 0.9
    assert custom_genome.genes["drift_threshold"] == 0.0  # Clamped
    assert custom_genome.generation == 5


def test_strategy_genome_mutation(genome):
    """Test genome mutation."""
    mutated_genome = genome.mutate(mutation_rate=1.0, mutation_strength=0.1)

    assert mutated_genome.genome_id != genome.genome_id
    assert mutated_genome.generation == genome.generation + 1
    # Check if at least one gene has changed
    assert any(
        mutated_genome.genes[g] != genome.genes[g] for g in genome.genes
    )


def test_strategy_genome_crossover(genome):
    """Test genome crossover."""
    other_config = {
        "alignment_threshold": 0.1,
        "drift_threshold": 0.9,
        "confidence_threshold": 0.1,
        "hybrid_alpha": 0.9,
        "temporal_weight": 0.1,
    }
    other_genome = StrategyGenome(other_config)

    child1, child2 = genome.crossover(other_genome)

    assert child1.generation == 1
    assert child2.generation == 1
    # Check that children have a mix of parent genes
    assert (
        child1.genes["alignment_threshold"] == genome.genes["alignment_threshold"] or
        child1.genes["alignment_threshold"] == other_genome.genes["alignment_threshold"]
    )
    assert (
        child2.genes["temporal_weight"] == genome.genes["temporal_weight"] or
        child2.genes["temporal_weight"] == other_genome.genes["temporal_weight"]
    )


def test_evolution_engine_initialization(engine):
    """Test EvolutionEngine population initialization."""
    engine.initialize_population()
    assert len(engine.population) == 10
    assert all(isinstance(g, StrategyGenome) for g in engine.population)


def test_evolution_engine_fitness_evaluation(engine):
    """Test fitness evaluation of the population."""
    engine.initialize_population()

    def mock_benchmark(config):
        # Simple fitness function for testing
        return config["alignment_threshold"]

    engine.evaluate_fitness(mock_benchmark)

    assert all(g.fitness is not None for g in engine.population)
    assert engine.best_genome is not None
    assert engine.best_genome.fitness == max(g.fitness for g in engine.population)


def test_evolution_engine_selection(engine):
    """Test parent selection."""
    engine.initialize_population()
    for i, g in enumerate(engine.population):
        g.fitness = i / 10.0  # Assign fitness scores

    parents = engine.selection(selection_pressure=0.5)
    assert len(parents) == 5
    # Check that the selected parents are the fittest
    assert all(p.fitness >= 0.5 for p in parents)


def test_evolution_engine_reproduction(engine):
    """Test reproduction to create a new generation."""
    engine.initialize_population()
    for g in engine.population:
        g.fitness = random.random()

    engine.best_genome = max(engine.population, key=lambda g: g.fitness)

    parents = engine.selection()
    offspring = engine.reproduce(parents)

    assert len(offspring) == 10
    # Best genome should be preserved (elitism)
    best_parent = max(parents, key=lambda g: g.fitness)
    assert any(o.genome_id == best_parent.genome_id for o in offspring)


def test_evolution_engine_full_cycle(engine):
    """Test a full evolution cycle."""
    engine.initialize_population()

    def mock_benchmark(config):
        return random.random()

    stats = engine.evolve_generation(mock_benchmark)

    assert stats["generation"] == 1
    assert len(engine.population) == 10
    assert "best_fitness" in stats
    assert len(engine.evolution_history) == 1


@patch("builtins.open")
@patch("json.dump")
def test_save_strategy(mock_json_dump, mock_open):
    """Test saving a strategy configuration."""
    config = StrategyGenome().to_dream_config()
    save_strategy(config, "test_strategy.json")

    mock_open.assert_called_once_with("test_strategy.json", "w")
    mock_json_dump.assert_called_once()
    # Check that metadata is added
    args, _ = mock_json_dump.call_args
    assert "timestamp" in args[0]
    assert args[0]["config"] == config


@patch("builtins.open")
@patch("json.load")
def test_load_strategy(mock_json_load, mock_open):
    """Test loading a strategy configuration."""
    mock_config = {"alignment_threshold": 0.75}
    mock_json_load.return_value = {"config": mock_config}

    config = load_strategy("test_strategy.json")

    mock_open.assert_called_once_with("test_strategy.json", "r")
    assert config == mock_config
