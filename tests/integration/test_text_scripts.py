import unittest
from pathlib import Path

from tests.integration.text_script import run_text_script, split_script_and_expected

SCRIPTS_DIR = Path(__file__).parent / "scripts"


class TestTextScripts(unittest.TestCase):
    def test_kfc_scripts_match_expected_output(self):
        script_paths = sorted(SCRIPTS_DIR.glob("*.kfc"))

        self.assertGreaterEqual(len(script_paths), 6)

        for script_path in script_paths:
            with self.subTest(script=script_path.name):
                content = script_path.read_text(encoding="utf-8")
                script_text, expected_output = split_script_and_expected(content)

                self.assertIsNotNone(expected_output)
                self.assertEqual(run_text_script(script_text), expected_output)


if __name__ == "__main__":
    unittest.main()
