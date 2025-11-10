import math
import random
import unittest
from unittest.mock import MagicMock, patch

from candidate.quantum.annealing import QuantumAnnealer, AnnealingResult


class TestQuantumAnnealer(unittest.TestCase):
    def setUp(self):
        self.rng = random.Random(42)
        self.annealer = QuantumAnnealer(rng=self.rng)
        self.search_space = [{"x": i} for i in range(10)]
        self.objective = lambda state: state["x"]

    def test_anneal_finds_minimum(self):
        result = self.annealer.anneal(self.objective, search_space=self.search_space)
        self.assertIsInstance(result, AnnealingResult)
        self.assertEqual(result.solution["x"], 0)
        self.assertEqual(result.energy, 0)

    def test_anneal_with_constraints(self):
        constraints = {
            "initial_temperature": 100.0,
            "cooling_rate": 0.9,
            "min_temperature": 0.1,
            "max_iterations": 200,
            "tunneling_rate": 0.2,
        }
        result = self.annealer.anneal(
            self.objective, search_space=self.search_space, constraints=constraints
        )
        self.assertEqual(result.solution["x"], 0)
        self.assertEqual(result.energy, 0)
        self.assertLess(result.metadata["final_temperature"], 100.0)

    def test_anneal_with_energy_function_in_constraints(self):
        constraints = {"energy_function": self.objective}
        result = self.annealer.anneal(
            None, search_space=self.search_space, constraints=constraints
        )
        self.assertEqual(result.solution["x"], 0)
        self.assertEqual(result.energy, 0)

    def test_anneal_raises_error_if_no_objective(self):
        with self.assertRaises(ValueError):
            self.annealer.anneal(None, search_space=self.search_space)

    def test_anneal_raises_error_on_empty_search_space(self):
        with self.assertRaises(ValueError):
            self.annealer.anneal(self.objective, search_space=[])

    def test_quantum_tunneling_effect(self):
        # This test is probabilistic, but we can check if it explores more
        # A high tunneling rate should allow jumping out of local minima
        high_tunnel_annealer = QuantumAnnealer(rng=random.Random(42))
        constraints = {"tunneling_rate": 1.0, "max_iterations": 10} # high tunneling
        objective = lambda state: abs(state["x"] - 5) # minimum is at x=5
        search_space = [{"x": i} for i in range(10)]

        # Mock random to control acceptance probability
        with patch.object(self.rng, 'random', side_effect=[0.9, 0.9, 0.9, 0.1] + [0.9]*20):
             result = high_tunnel_annealer.anneal(
                objective, search_space=search_space, constraints=constraints
            )
             # Even if acceptance is low, tunneling should allow a jump
             self.assertNotEqual(result.solution['x'], search_space[0]['x'])


    def test_select_neighbour(self):
        current = {"x": 5}
        candidates = [{"x": i} for i in range(10)]
        neighbour = self.annealer._select_neighbour(current, candidates)
        self.assertIn(neighbour, candidates)

    def test_select_neighbour_avoids_current(self):
        current = {"x": 5}
        candidates = [{"x": 5}, {"x": 6}]
        # Rig the RNG to select the current state first
        with patch.object(self.rng, 'choice', side_effect=[{"x": 5}, {"x": 6}]):
            neighbour = self.annealer._select_neighbour(current, candidates)
            self.assertNotEqual(neighbour, current)


    def test_energy_landscape_traversal(self):
        objective = lambda state: (state["x"] - 5) ** 2
        result = self.annealer.anneal(objective, search_space=self.search_space)
        self.assertGreater(len(result.history), 1)
        self.assertTrue(all(e >= 0 for e in result.history))

    def test_temperature_scheduling(self):
        constraints = {
            "initial_temperature": 1.0,
            "cooling_rate": 0.5,
            "min_temperature": 0.1,
            "max_iterations": 3,
        }
        self.annealer.anneal(
            self.objective, search_space=self.search_space, constraints=constraints
        )
        # After 3 iterations, T should be 1.0 * 0.5 * 0.5 * 0.5 = 0.125
        # It should not go below min_temperature
        final_temp = 1.0 * (0.5**3)
        self.assertAlmostEqual(
            self.annealer.anneal(self.objective, search_space=self.search_space, constraints=constraints).metadata['final_temperature'],
            max(constraints['min_temperature'], final_temp)
        )

    def test_convergence_to_best_solution(self):
        # A landscape with a clear global minimum
        objective = lambda state: (state["x"] - 7) ** 2
        search_space = [{"x": i} for i in range(50)]
        result = self.annealer.anneal(objective, search_space=search_space, constraints={"max_iterations": 500})
        self.assertEqual(result.solution["x"], 7)

    def test_initial_state_is_respected(self):
        initial_state = {"x": 9}
        constraints = {"initial_state": initial_state, "max_iterations": 0}
        result = self.annealer.anneal(self.objective, search_space=self.search_space, constraints=constraints)
        # With 0 iterations, the solution should be the initial state
        self.assertEqual(result.solution, initial_state)

    def test_single_candidate_in_search_space(self):
        single_search_space = [{"x": 100}]
        result = self.annealer.anneal(self.objective, search_space=single_search_space)
        self.assertEqual(result.solution, single_search_space[0])
        self.assertEqual(result.energy, 100)
        self.assertEqual(result.explored, 128) # Explores the same state repeatedly

    def test_non_numeric_objective_values(self):
        objective = lambda state: "not a number"
        with self.assertRaises(ValueError):
            self.annealer.anneal(objective, search_space=self.search_space)


if __name__ == "__main__":
    unittest.main()