import random
import unittest

from candidate.quantum.annealing import QuantumAnnealer


class TestQuantumAnnealer(unittest.TestCase):
    def setUp(self):
        self.rng = random.Random(42)
        self.annealer = QuantumAnnealer(rng=self.rng)

    def test_anneal_basic(self):
        # Objective: minimize x^2
        objective = lambda state: state["x"] ** 2
        search_space = [{"x": i} for i in range(-10, 11)]
        result = self.annealer.anneal(objective, search_space=search_space)
        self.assertEqual(result.solution, {"x": 0})
        self.assertEqual(result.energy, 0)

    def test_anneal_with_constraints(self):
        objective = lambda state: state["x"] ** 2
        search_space = [{"x": i} for i in range(-10, 11)]
        constraints = {
            "initial_temperature": 100.0,
            "cooling_rate": 0.9,
            "max_iterations": 200,
        }
        result = self.annealer.anneal(objective, search_space=search_space, constraints=constraints)
        self.assertEqual(result.solution, {"x": 0})
        self.assertEqual(result.energy, 0)
        self.assertLess(result.metadata["final_temperature"], 100.0)

    def test_quantum_tunneling(self):
        # A landscape with a local minimum at x=5 and global minimum at x=-10
        def objective_with_local_minimum(state):
            x = state["x"]
            if x > 0:
                return (x - 5) ** 2  # Local minimum at x=5, energy=0
            else:
                return (x + 10) ** 2 - 10  # Global minimum at x=-10, energy=-10

        search_space = [{"x": i} for i in range(-20, 21)]
        constraints = {
            "initial_state": {"x": 5},
            "tunneling_rate": 0.3,
            "max_iterations": 500,
        }
        result = self.annealer.anneal(
            objective_with_local_minimum,
            search_space=search_space,
            constraints=constraints,
        )
        self.assertEqual(result.solution, {"x": -10})
        self.assertEqual(result.energy, -10)

    def test_no_objective_or_energy_function(self):
        search_space = [{"x": 1}]
        with self.assertRaises(ValueError):
            self.annealer.anneal(None, search_space=search_space)

    def test_empty_search_space(self):
        objective = lambda state: state["x"] ** 2
        with self.assertRaises(ValueError):
            self.annealer.anneal(objective, search_space=[])

    def test_reproducibility(self):
        objective = lambda state: (state["x"] - 7) ** 2 + (state["y"] + 2) ** 2
        search_space = [{"x": i, "y": j} for i in range(10) for j in range(-5, 5)]

        # Run 1
        rng1 = random.Random(123)
        annealer1 = QuantumAnnealer(rng=rng1)
        result1 = annealer1.anneal(objective, search_space=search_space)

        # Run 2
        rng2 = random.Random(123)
        annealer2 = QuantumAnnealer(rng=rng2)
        result2 = annealer2.anneal(objective, search_space=search_space)

        self.assertEqual(result1.solution, result2.solution)
        self.assertEqual(result1.energy, result2.energy)

    def test_initial_state(self):
        objective = lambda state: state["x"]
        search_space = [{"x": i} for i in range(10)]
        constraints = {"initial_state": {"x": 9}}
        result = self.annealer.anneal(objective, search_space=search_space, constraints=constraints)
        # The first energy in history should correspond to the initial state
        self.assertEqual(result.history[0], 9)

    def test_single_candidate(self):
        objective = lambda state: state["x"] ** 2
        search_space = [{"x": 5}]
        result = self.annealer.anneal(objective, search_space=search_space)
        self.assertEqual(result.solution, {"x": 5})
        self.assertEqual(result.energy, 25)

if __name__ == "__main__":
    unittest.main()
