"""Compatibility entry point; the packaged interpreter is canonical."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from mozhi.core import *


def main():
    from mozhi.cli import main as cli_main
    return cli_main(sys.argv[1:] or ['--example'])


if __name__ == '__main__':
    raise SystemExit(main())
