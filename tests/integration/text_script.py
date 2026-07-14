import io
from contextlib import redirect_stdout

from kungfu_chess.texttests.script_runner import ScriptRunner


def split_script_and_expected(raw_input):
    if "---" in raw_input:
        script_text, expected_text = raw_input.split("---", 1)
        return script_text.strip(), expected_text.strip()
    return raw_input.strip(), None


def run_text_script(raw_input):
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        ScriptRunner().run(raw_input)
    return buffer.getvalue().strip()
