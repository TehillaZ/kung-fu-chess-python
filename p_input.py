import sys

from kungfu_chess.texttests.script_runner import ScriptRunner


def parse_input(raw_input):
    return ScriptRunner().run(raw_input)


if __name__ == "__main__":
    parse_input(sys.stdin.read())
