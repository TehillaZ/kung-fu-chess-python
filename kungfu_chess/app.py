import os
import sys

# Allow running as: py kungfu_chess/app.py
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kungfu_chess.texttests.script_runner import ScriptRunner


def main():
    ScriptRunner().run(sys.stdin.read())


if __name__ == "__main__":
    main()
