"""
Unit tests for the Symbolic Proteome system in labs/bio/symbolic_proteome.py
"""
import asyncio
import time
import unittest
from unittest.mock import MagicMock, patch, ANY

# The module is in 'labs', but bridged from 'bio'
from bio.symbolic_proteome import (
    MemoryCodon,
    MemoryProtein,
    ProteinComplex,
    MolecularChaperone,
    SymbolicProteome,
    ProteinType,
    FoldingState,
    PostTranslationalModification,
)


class TestSymbolicProteomeDataClasses(unittest.TestCase):
    """Tests for the data classes: MemoryCodon, MemoryProtein, ProteinComplex."""

    def test_memory_codon_from_fragment(self):
        fragment = "test_fragment"
        position = 10
        codon = MemoryCodon.from_memory_fragment(fragment, position)
        self.assertEqual(codon.sequence, "tes")
        self.assertEqual(codon.position, position)
        self.assertEqual(len(codon.amino_acid), 3)

    def test_memory_codon_short_fragment(self):
        fragment = "t"
        position = 0
        codon = MemoryCodon.from_memory_fragment(fragment, position)
        self.assertEqual(codon.sequence, "tXX")

    def test_memory_protein_initial_state(self):
        protein = MemoryProtein()
        self.assertEqual(protein.folding_state, FoldingState.UNFOLDED)
        self.assertEqual(protein.activity_level, 0.0)
        self.assertEqual(protein.misfold_count, 0)

    def test_memory_protein_calculate_stability_base(self):
        protein = MemoryProtein(folding_energy=20.0)
        self.assertAlmostEqual(protein.calculate_stability(), 1.0 - (20.0 / 100.0))

    def test_memory_protein_stability_with_sumoylation(self):
        protein = MemoryProtein(folding_energy=20.0)
        protein.modifications[PostTranslationalModification.SUMOYLATION] = []
        expected_stability = (1.0 - (20.0 / 100.0)) * 1.5
        self.assertAlmostEqual(protein.calculate_stability(), min(1.0, expected_stability))

    def test_memory_protein_stability_with_ubiquitination(self):
        protein = MemoryProtein(folding_energy=20.0)
        protein.modifications[PostTranslationalModification.UBIQUITINATION] = []
        expected_stability = (1.0 - (20.0 / 100.0)) * 0.5
        self.assertAlmostEqual(protein.calculate_stability(), expected_stability)

    def test_memory_protein_stability_with_misfolds(self):
        protein = MemoryProtein(folding_energy=20.0)
        protein.misfold_count = 2
        expected_stability = (1.0 - (20.0 / 100.0)) * (1.0 / 3.0)
        self.assertAlmostEqual(protein.calculate_stability(), expected_stability)

    def test_memory_protein_is_functional_true(self):
        protein = MemoryProtein(
            folding_state=FoldingState.NATIVE, activity_level=0.5, folding_energy=10.0
        )
        self.assertTrue(protein.is_functional())

    def test_memory_protein_is_functional_false_not_native(self):
        protein = MemoryProtein(
            folding_state=FoldingState.FOLDING, activity_level=0.5, folding_energy=10.0
        )
        self.assertFalse(protein.is_functional())

    def test_memory_protein_is_functional_false_low_activity(self):
        protein = MemoryProtein(
            folding_state=FoldingState.NATIVE, activity_level=0.1, folding_energy=10.0
        )
        self.assertFalse(protein.is_functional())

    def test_memory_protein_is_functional_false_low_stability(self):
        protein = MemoryProtein(
            folding_state=FoldingState.NATIVE, activity_level=0.5, folding_energy=90.0
        )
        self.assertFalse(protein.is_functional())

    def test_protein_complex_synergy_no_members(self):
        complex_ = ProteinComplex()
        self.assertEqual(complex_.calculate_synergy({}), 1.0)

    def test_protein_complex_synergy_one_member(self):
        p1 = MemoryProtein(protein_id="p1", folding_energy=10)
        complex_ = ProteinComplex(member_proteins={"p1"})
        self.assertEqual(complex_.calculate_synergy({"p1": p1}), 1.0)

    def test_protein_complex_synergy_multiple_members(self):
        p1 = MemoryProtein(protein_id="p1", folding_energy=10)
        p2 = MemoryProtein(protein_id="p2", folding_energy=30)
        proteins = {"p1": p1, "p2": p2}
        complex_ = ProteinComplex(
            member_proteins={"p1", "p2"}, activity_multiplier=1.5
        )
        avg_stability = (p1.calculate_stability() + p2.calculate_stability()) / 2
        import math
        expected_synergy = avg_stability * math.log(3) * 1.5
        self.assertAlmostEqual(
            complex_.calculate_synergy(proteins), expected_synergy
        )


class TestMolecularChaperone(unittest.IsolatedAsyncioTestCase):
    """Tests for the MolecularChaperone class."""

    def setUp(self):
        self.chaperone = MolecularChaperone()
        self.protein = MemoryProtein()

    async def test_assist_folding_of_folding_protein(self):
        self.protein.folding_state = FoldingState.FOLDING
        self.protein.folding_energy = 50.0
        result = await self.chaperone.assist_folding(self.protein)
        self.assertTrue(result)
        self.assertEqual(self.chaperone.assisted_folds, 1)
        self.assertEqual(self.protein.folding_energy, 40.0)

    @patch("random.random", return_value=0.5)
    async def test_assist_folding_rescue_misfolded_protein_success(self, mock_random):
        self.protein.folding_state = FoldingState.MISFOLDED
        self.protein.misfold_count = 2
        self.chaperone.rescue_rate = 0.8
        result = await self.chaperone.assist_folding(self.protein)
        self.assertTrue(result)
        self.assertEqual(self.chaperone.assisted_folds, 1)
        self.assertEqual(self.protein.folding_state, FoldingState.FOLDING)
        self.assertEqual(self.protein.misfold_count, 1)

    @patch("random.random", return_value=0.9)
    async def test_assist_folding_rescue_misfolded_protein_failure(self, mock_random):
        self.protein.folding_state = FoldingState.MISFOLDED
        self.chaperone.rescue_rate = 0.8
        result = await self.chaperone.assist_folding(self.protein)
        self.assertFalse(result)
        self.assertEqual(self.chaperone.assisted_folds, 0)
        self.assertEqual(self.protein.folding_state, FoldingState.MISFOLDED)

    async def test_assist_folding_no_effect_on_native_protein(self):
        self.protein.folding_state = FoldingState.NATIVE
        result = await self.chaperone.assist_folding(self.protein)
        self.assertFalse(result)
        self.assertEqual(self.chaperone.assisted_folds, 0)


class TestSymbolicProteome(unittest.IsolatedAsyncioTestCase):
    """Comprehensive tests for the SymbolicProteome class."""

    async def asyncSetUp(self):
        # We don't start the proteome to control the loops manually for testing
        self.proteome = SymbolicProteome(max_proteins=100, enable_chaperones=True)

    async def test_translate_memory_creates_unfolded_protein(self):
        protein_id = await self.proteome.translate_memory("mem1", {"data": "test"})
        self.assertIn(protein_id, self.proteome.proteins)
        protein = self.proteome.proteins[protein_id]
        self.assertEqual(protein.source_memory_id, "mem1")
        self.assertEqual(protein.folding_state, FoldingState.UNFOLDED)
        self.assertEqual(self.proteome.total_synthesized, 1)

    @patch("random.random", return_value=0.1)  # Guarantees successful fold
    async def test_fold_protein_successful(self, mock_random):
        protein = MemoryProtein()
        protein.folding_state = FoldingState.FOLDING
        await self.proteome._fold_protein(protein)
        self.assertEqual(protein.folding_state, FoldingState.NATIVE)
        self.assertGreater(protein.activity_level, 0.0)
        self.assertEqual(self.proteome.successful_folds, 1)

    @patch("random.random", return_value=0.99)  # Guarantees failed fold
    async def test_fold_protein_misfolded(self, mock_random):
        protein = MemoryProtein()
        protein.folding_state = FoldingState.FOLDING
        protein.fold_attempts = 4  # Ensure it misfolds on failure
        await self.proteome._fold_protein(protein)
        self.assertEqual(protein.folding_state, FoldingState.MISFOLDED)
        self.assertEqual(protein.misfold_count, 1)
        self.assertEqual(self.proteome.misfold_events, 1)

    async def test_modify_protein_ubiquitination_marks_for_degradation(self):
        protein_id = await self.proteome.translate_memory("mem1", "data")
        protein = self.proteome.proteins[protein_id]
        self.assertNotIn(protein_id, self.proteome.degradation_queue)

        await self.proteome.modify_protein(protein_id, PostTranslationalModification.UBIQUITINATION)
        await self.proteome.modify_protein(protein_id, PostTranslationalModification.UBIQUITINATION)
        self.assertEqual(protein.degradation_signals, 2)
        self.assertNotIn(protein_id, self.proteome.degradation_queue)

        await self.proteome.modify_protein(protein_id, PostTranslationalModification.UBIQUITINATION)
        self.assertEqual(protein.degradation_signals, 3)
        self.assertIn(protein_id, self.proteome.degradation_queue)

    async def test_form_complex_success(self):
        p1_id = await self.proteome.translate_memory("mem1", "data1")
        p2_id = await self.proteome.translate_memory("mem2", "data2")
        p1 = self.proteome.proteins[p1_id]
        p2 = self.proteome.proteins[p2_id]
        # Manually set to functional state for testing
        p1.folding_state = FoldingState.NATIVE
        p1.activity_level = 0.8
        p2.folding_state = FoldingState.NATIVE
        p2.activity_level = 0.8

        complex_id = await self.proteome.form_complex([p1_id, p2_id], "test_complex")
        self.assertIsNotNone(complex_id)
        self.assertIn(complex_id, self.proteome.protein_complexes)
        self.assertIn(complex_id, p1.complex_memberships)
        self.assertIn(complex_id, p2.complex_memberships)
        self.assertEqual(self.proteome.complex_formations, 1)

    async def test_form_complex_fails_with_non_functional_proteins(self):
        p1_id = await self.proteome.translate_memory("mem1", "data1")
        complex_id = await self.proteome.form_complex([p1_id], "test_complex")
        self.assertIsNone(complex_id)

    async def test_query_functional_proteins(self):
        # Create one functional and one non-functional protein
        p1_id = await self.proteome.translate_memory("mem1", "data")
        p1 = self.proteome.proteins[p1_id]
        p1.folding_state = FoldingState.NATIVE
        p1.activity_level = 0.8
        p1.protein_type = ProteinType.ENZYMATIC
        p1.modifications[PostTranslationalModification.PHOSPHORYLATION] = []

        await self.proteome.translate_memory("mem2", "data") # p2 remains non-functional

        results = await self.proteome.query_functional_proteins()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].protein_id, p1_id)

        # Test with filters
        enzymatic = await self.proteome.query_functional_proteins(protein_type=ProteinType.ENZYMATIC)
        self.assertEqual(len(enzymatic), 1)
        structural = await self.proteome.query_functional_proteins(protein_type=ProteinType.STRUCTURAL)
        self.assertEqual(len(structural), 0)
        modified = await self.proteome.query_functional_proteins(has_modification=PostTranslationalModification.PHOSPHORYLATION)
        self.assertEqual(len(modified), 1)

    async def test_express_memory_function_calculates_activity(self):
        p1_id = await self.proteome.translate_memory("mem1", "data1")
        p2_id = await self.proteome.translate_memory("mem1", "data2") # Same memory_id

        p1 = self.proteome.proteins[p1_id]
        p1.folding_state = FoldingState.NATIVE
        p1.activity_level = 0.6

        p2 = self.proteome.proteins[p2_id]
        p2.folding_state = FoldingState.NATIVE
        p2.activity_level = 0.3

        result = await self.proteome.express_memory_function("mem1")
        self.assertAlmostEqual(result["total_activity"], 0.9)
        self.assertEqual(result["active_proteins"], 2)

    @patch("labs.bio.symbolic_proteome.asyncio")
    @patch("labs.bio.symbolic_proteome.time")
    async def test_degradation_loop_removes_old_protein(self, mock_time, mock_asyncio):
        start_time = 1731312000.0
        mock_time.time.return_value = start_time

        protein_id = await self.proteome.translate_memory("mem1", "data")
        protein = self.proteome.proteins[protein_id]

        # Manually set the synthesis time for a predictable test
        protein.synthesis_time = start_time
        protein.half_life = 100  # seconds

        # Configure the sleep mock to break the loop after one iteration
        async def break_loop(*args):
            self.proteome._running = False
        mock_asyncio.sleep.side_effect = break_loop

        # Simulate time passing beyond half-life
        mock_time.time.return_value = start_time + 200
        self.proteome.degradation_queue.add(protein_id)

        # Run the loop, which will now exit after one pass
        self.proteome._running = True
        await self.proteome._degradation_loop()

        self.assertNotIn(protein_id, self.proteome.proteins)
        self.assertEqual(self.proteome.total_degraded, 1)
        self.assertNotIn(protein_id, self.proteome.degradation_queue)

    async def test_autophagy_triggered_when_max_proteins_exceeded(self):
        self.proteome.max_proteins = 5
        # Use a real method, but we can check its effects
        with patch.object(self.proteome, '_trigger_autophagy', wraps=self.proteome._trigger_autophagy) as wrapped_autophagy:
            for i in range(6):
                await self.proteome._synthesize_protein(f"mem{i}", "data", ProteinType.STRUCTURAL)

            # Autophagy should be called on the 6th protein
            wrapped_autophagy.assert_called_once()
            # It should mark at least one protein for degradation
            self.assertGreater(len(self.proteome.degradation_queue), 0)

    @patch("labs.bio.symbolic_proteome.asyncio")
    async def test_translation_loop_synthesizes_from_queue(self, mock_asyncio):
        self.proteome.ribosome_queue.append(("mem1", "data"))
        self.proteome.ribosome_queue.append(("mem2", "data"))
        self.assertEqual(len(self.proteome.proteins), 0)

        # Configure the sleep mock to break the loop after one iteration
        async def break_loop(*args):
            self.proteome._running = False
        mock_asyncio.sleep.side_effect = break_loop

        # Run the loop, which will now exit after one pass
        self.proteome._running = True
        await self.proteome._translation_loop()

        self.assertEqual(len(self.proteome.proteins), 2)
        self.assertEqual(self.proteome.total_synthesized, 2)
        self.assertEqual(len(self.proteome.ribosome_queue), 0)

    async def test_get_metrics_returns_correct_counts(self):
        await self.proteome.translate_memory("mem1", "data", ProteinType.ENZYMATIC)
        await self.proteome.translate_memory("mem2", "data", ProteinType.STRUCTURAL)

        p1 = list(self.proteome.proteins.values())[0]
        p1.folding_state = FoldingState.NATIVE
        p1.is_functional = MagicMock(return_value=True)

        metrics = self.proteome.get_metrics()
        self.assertEqual(metrics["total_proteins"], 2)
        self.assertEqual(metrics["functional_proteins"], 1)
        self.assertEqual(metrics["state_distribution"]["native"], 1)
        self.assertEqual(metrics["state_distribution"]["unfolded"], 1)
        self.assertEqual(metrics["type_distribution"]["enzymatic"], 1)


if __name__ == "__main__":
    unittest.main()
