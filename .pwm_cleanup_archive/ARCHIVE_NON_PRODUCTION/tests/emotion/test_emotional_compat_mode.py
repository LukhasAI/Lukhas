import unittest

from memory.core_memory import emotional_memory
from memory.core_memory.emotional_memory import EmotionalMemory


class TestEmotionalCompatMode(unittest.TestCase):
    def setUp(self):
        self.em_original = emotional_memory.compat_mode

    def tearDown(self):
        emotional_memory.compat_mode = self.em_original

    def test_compat_mode_toggle(self):
        emotional_memory.compat_mode = False
        em = EmotionalMemory()
        with self.assertRaises(NotImplementedError):
            em.affect_vector_velocity(depth=1)
        emotional_memory.compat_mode = True
        self.assertIsNone(em.affect_vector_velocity(depth=1))
