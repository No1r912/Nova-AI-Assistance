import unittest
from unittest.mock import patch

from voice.speak import speak


class SpeakTests(unittest.TestCase):
    def test_uses_windows_speech_when_piper_is_unavailable(self):
        with patch("voice.speak._speak_with_piper", return_value=False), patch(
            "voice.speak._speak_with_windows_sapi", return_value=True
        ) as sapi:
            self.assertTrue(speak("Hello"))
            sapi.assert_called_once_with("Hello")

    def test_blank_text_does_not_start_a_speech_engine(self):
        with patch("voice.speak._speak_with_piper") as piper:
            self.assertTrue(speak("   "))
            piper.assert_not_called()
