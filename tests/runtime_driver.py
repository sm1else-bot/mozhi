"""Bounded subprocess harness for testing both current execution adapters."""
import asyncio
import contextlib
import io
import json
import pathlib
import runpy
import sys
import types
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]


class BoundedOutput(io.StringIO):
    def write(self, text):
        if self.tell() + len(text) > 200000:
            raise RuntimeError('Test program exceeded its output budget.')
        return super().write(text)


def execute(request):
    target = ROOT / ('src/mozhi.py' if request['runtime'] == 'cli' else 'playground/runtime.py')
    namespace = runpy.run_path(str(target))
    # run_path returns a copy; function globals retain the execution namespace.
    globals_ = namespace['Interpreter'].exec.__globals__
    output = BoundedOutput()
    answers = iter(request.get('inputs', []))

    def read_answer(prompt=''):
        try:
            return next(answers)
        except StopIteration:
            raise EOFError('No input was supplied.') from None

    def cli_input(prompt=''):
        print(prompt, end='')
        return read_answer()

    async def browser_input(prompt):
        return read_answer()

    with contextlib.redirect_stdout(output), patch('builtins.input', cli_input):
        if request['runtime'] == 'browser':
            globals_['js'] = types.SimpleNamespace(
                appendMozhiOutput=output.write, getMozhiInput=browser_input,
            )
            result = asyncio.run(namespace['execute_mozhi'](request['source']))
            return {'output': output.getvalue(), 'error': result['error']}
        try:
            namespace['run'](request['source'])
            error = None
        except (namespace['MozhiError'], SyntaxError) as failure:
            error = str(failure)
    return {'output': output.getvalue(), 'error': error}


if __name__ == '__main__':
    print(json.dumps(execute(json.load(sys.stdin))))
