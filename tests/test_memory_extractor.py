import unittest

from core.memory_extractor import extract


class MemoryExtractorTests(unittest.TestCase):
    def test_preserves_name_capitalization(self):
        self.assertEqual(
            extract("My name is Hazwan"),
            {"remember": True, "type": "profile", "key": "name", "value": "Hazwan"},
        )

    def test_finds_natural_preference(self):
        self.assertEqual(
            extract("I really like Python and local AI."),
            {"remember": True, "type": "preference", "key": "likes", "value": "Python and local AI"},
        )

    def test_ignores_small_talk(self):
        self.assertEqual(extract("Hello, how are you?"), {"remember": False})

    def test_extracts_goal(self):
        self.assertEqual(
            extract("I'm planning to build a voice assistant"),
            {"remember": True, "type": "goal", "goal_type": "short_term", "value": "build a voice assistant"},
        )
