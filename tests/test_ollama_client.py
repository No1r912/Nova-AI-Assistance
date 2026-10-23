import builtins
import unittest
from unittest.mock import patch

from ai.ollama_client import generate


class OllamaClientTests(unittest.TestCase):
    def test_missing_dependency_has_a_clear_error(self):
        original_import = builtins.__import__

        def missing_ollama(name, *args, **kwargs):
            if name == "ollama":
                raise ModuleNotFoundError("No module named 'ollama'")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=missing_ollama):
            with self.assertRaisesRegex(RuntimeError, "Could not reach Ollama"):
                generate([])


if __name__ == "__main__":
    unittest.main()
