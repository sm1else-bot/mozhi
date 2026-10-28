"""Terminal adapter for the canonical Mozhi interpreter."""
import argparse
from pathlib import Path
import sys

from ._version import __version__
from . import core


def parse(source):
    return core.Parser(core.tokenize(source)).parse()


def execute(statements, interpreter, environment, echo=False):
    try:
        for statement in statements:
            value = interpreter.exec(statement, environment)
            if echo and value is not None:
                print(interpreter.mozhi_repr(value))
    except core.ExitSignal:
        pass


def report(error, filename):
    print(f"{filename}: {error}", file=sys.stderr)


def repl():
    print(f"Mozhi {__version__}. quit / exit; EOF veliya pogum.")
    interpreter, environment = core.Interpreter(), core.Environment()
    pending = []
    while True:
        try:
            line = input("... " if pending else "mozhi> ")
            if not pending and line.strip() in {"quit", "exit", ":quit", ":exit"}:
                return 0
            pending.append(line)
            parser = None
            try:
                parser = core.Parser(core.tokenize("\n".join(pending) + "\n"))
                statements = parser.parse()
            except SyntaxError as error:
                if parser is not None and all(
                    token.type == core.TT_EOF or (token.type == core.TT_DEDENT and token.line == 0)
                    for token in parser.tokens[parser.pos:]
                ):
                    continue
                report(error, "<repl>")
                pending.clear()
                continue
            pending.clear()
            execute(statements, interpreter, environment, echo=True)
        except EOFError:
            if pending:
                report("Incomplete input at EOF; mudivu venum.", "<repl>")
                return 1
            print()
            return 0
        except KeyboardInterrupt:
            print("\n[Mozhi] Input cancelled.", file=sys.stderr)
            pending.clear()
        except (core.MozhiError, SyntaxError) as error:
            report(error, "<repl>")
            pending.clear()


def main(argv=None):
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except (OSError, ValueError):
                pass
    parser = argparse.ArgumentParser(prog="mozhi", description="Mozhi interpreted language")
    parser.add_argument("--version", action="version", version=f"Mozhi {__version__}")
    parser.add_argument("--example", action="store_true", help="run the built-in example")
    commands = parser.add_subparsers(dest="command")
    for command, help_text in [("run", "execute a UTF-8 program"), ("check", "parse without executing")]:
        command_parser = commands.add_parser(command, help=help_text)
        command_parser.add_argument("file", help="relative or absolute source path")
    commands.add_parser("repl", help="persistent interactive session")
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments and arguments[0] not in {"run", "check", "repl"} and not arguments[0].startswith("-"):
        arguments.insert(0, "run")
    options = parser.parse_args(arguments)
    filename = getattr(options, "file", "<example>")
    try:
        if options.example:
            print("--- Mozhi Example ---")
            core.run(core.EXAMPLE)
        elif options.command == "repl":
            return repl()
        elif options.command in {"run", "check"}:
            source = Path(options.file).read_text(encoding="utf-8-sig")
            statements = parse(source)
            if options.command == "run":
                execute(statements, core.Interpreter(), core.Environment())
            else:
                print(f"{filename}: syntax OK")
        else:
            parser.print_help()
        return 0
    except KeyboardInterrupt:
        print("[Mozhi] Stopped by user.", file=sys.stderr)
        return 130
    except (core.MozhiError, SyntaxError, OSError, UnicodeError) as error:
        report(error, filename)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
