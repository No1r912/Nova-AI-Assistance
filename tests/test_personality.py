import unittest

from core.personality import get_system_prompt


class PersonalityTests(unittest.TestCase):
    def test_prompt_contains_language_and_safety_guidance(self):
        prompt = get_system_prompt().lower()
        self.assertIn("match the user's language", prompt)
        self.assertIn("do not bluff", prompt)


if __name__ == "__main__":
    unittest.main()
