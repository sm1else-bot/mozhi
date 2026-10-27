import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from sync_playground import generate


class RuntimeRegressions(unittest.TestCase):
    def execute(self, runtime, source, inputs=()):
        result = subprocess.run(
            [sys.executable, '-B', str(ROOT / 'tests/runtime_driver.py')],
            input=json.dumps({'runtime': runtime, 'source': source, 'inputs': inputs}),
            text=True, encoding='utf-8', capture_output=True, timeout=4,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def success(self, source, expected, inputs=()):
        for runtime in ['cli', 'browser']:
            with self.subTest(runtime=runtime):
                result = self.execute(runtime, source, inputs)
                self.assertIsNone(result['error'], result)
                self.assertEqual(result['output'], expected)

    def failure(self, source, line, text, inputs=()):
        for runtime in ['cli', 'browser']:
            with self.subTest(runtime=runtime):
                result = self.execute(runtime, source, inputs)
                self.assertIsNotNone(result['error'], result)
                self.assertIn(f'Line {line}:', result['error'])
                self.assertIn(text, result['error'])

    def test_generated_browser_matches_core(self):
        self.assertEqual((ROOT / 'playground/runtime.py').read_text(encoding='utf-8'), generate())

    def test_loop_and_nested_block_updates(self):
        self.success('i = 0 vechukko\ni < 3 varaikum:\n'
                     '    true na:\n        i = i + 1 vechukko\n    mudivu\n'
                     'mudivu\ni sollu\n', '3\n')

    def test_parameters_shadow_enclosing_values(self):
        self.success('x = 10 vechukko\nseiy f(x):\n'
                     '    x = x + 1 vechukko\n    x thirumbu\n'
                     'mudivu\nf(4) sollu\nx sollu\n', '5\n10\n')

    def test_function_updates_enclosing_variable(self):
        self.success('count = 0 vechukko\nseiy bump():\n'
                     '    count = count + 1 vechukko\nmudivu\n'
                     'bump()\ncount sollu\n', '1\n')

    def test_class_properties_methods_and_parameter_shadowing(self):
        self.success('value = 90 vechukko\nvagai Box:\n'
                     '    seiy start(naan, value):\n'
                     '        naan.value = value vechukko\n    mudivu\n'
                     '    seiy get(naan):\n        naan.value thirumbu\n'
                     '    mudivu\nmudivu\nb = Box porul vechukko\n'
                     'b.start(7)\nb.get() sollu\nb.value sollu\nvalue sollu\n',
                     '7\n7\n90\n')

    def test_historical_noninteractive_examples(self):
        expected = {'demo': '1\n2\n3\n', 'library': 'by Thiruvalluvar\n',
                    'gossip': '[Mozhi] Podhum, I am out.\n'}
        for name, suffix in expected.items():
            for runtime in ['cli', 'browser']:
                with self.subTest(example=name, runtime=runtime):
                    result = self.execute(runtime, (ROOT / f'examples/{name}.mozhi').read_text())
                    self.assertIsNone(result['error'], result)
                    self.assertTrue(result['output'].endswith(suffix), result)

    def test_calculator_and_input_aliases(self):
        for runtime in ['cli', 'browser']:
            with self.subTest(runtime=runtime):
                result = self.execute(runtime, (ROOT / 'examples/calculator.mozhi').read_text(),
                                      ['1', '10', '5', '6'])
                self.assertIsNone(result['error'], result)
                self.assertIn('Ippo total: 10', result['output'])
        self.success('a = kelu("A?") vechukko\nb = ketukko("B?") vechukko\n'
                     'a kooda b sollu\n', 'A?B?xy\n', ['x', 'y'])

    def test_exit_stops_nested_function_and_program(self):
        self.success('seiy quit():\n    true varaikum:\n        podhum\n'
                     '    mudivu\n    "bad" sollu\nmudivu\nquit()\n'
                     '"also bad" sollu\n', '[Mozhi] Podhum, I am out.\n')

    def test_exit_does_not_poison_next_execution(self):
        self.success('podhum\n', '[Mozhi] Podhum, I am out.\n')
        self.success('"fresh" sollu\n', 'fresh\n')

    def test_python_power_precedence(self):
        self.success('2 ** 3 ** 2 sollu\n-2 ** 2 sollu\n'
                     '(-2) ** 2 sollu\n2 ** -2 sollu\n2 * 3 ** 2 sollu\n',
                     '512\n-4\n4\n0.25\n18\n')

    def test_short_circuit_skips_errors_and_side_effects(self):
        self.success('n = 0 vechukko\nseiy effect():\n'
                     '    n = n + 1 vechukko\n    true thirumbu\nmudivu\n'
                     'false mattrum (1 / 0) sollu\n'
                     'true illaiyal missing sollu\n'
                     'false mattrum effect() sollu\n'
                     'true illaiyal effect() sollu\nn sollu\n',
                     'false\ntrue\nfalse\ntrue\n0\n')

    def test_boolean_operators_still_return_booleans(self):
        self.success('1 mattrum 2 sollu\n0 illaiyal 3 sollu\n', 'true\ntrue\n')

    def test_break_and_continue(self):
        self.success('i = 0 vechukko\ni < 5 varaikum:\n'
                     '    i = i + 1 vechukko\n    i == 2 na:\n'
                     '        thodaru\n    mudivu\n    i == 4 na:\n'
                     '        nillu\n    mudivu\n    i sollu\nmudivu\n', '1\n3\n')

    def test_invalid_dedent(self):
        self.failure('true na:\n    1 sollu\n  2 sollu\nmudivu\n', 3, 'Indentation')

    def test_unexpected_indent(self):
        self.failure('a = 1 vechukko\n    a sollu\n', 2, 'Unexpected indentation')

    def test_mixed_indent(self):
        self.failure('true na:\n \t1 sollu\nmudivu\n', 2, 'mix tabs and spaces')

    def test_missing_indent(self):
        self.failure('true na:\n1 sollu\nmudivu\n', 2, 'Expected INDENT')

    def test_missing_block_end(self):
        self.failure('true na:\n    1 sollu\n', 2, 'Expected KEYWORD')

    def test_unterminated_string(self):
        self.failure('"not closed sollu\n', 1, 'Missing closing quote')

    def test_escaped_backslash_and_quote(self):
        self.success(r'"path\\" sollu' + '\n' + r'"a\"b" sollu' + '\n', 'path\\\na"b\n')

    def test_builtin_arity(self):
        self.failure('neelam() sollu\n', 1, 'expects 1 argument')

    def test_function_arity(self):
        self.failure('seiy f(x):\n    x thirumbu\nmudivu\nf()\n', 4, 'expects 1 argument')

    def test_duplicate_parameters(self):
        self.failure('seiy f(x, x):\n    x thirumbu\nmudivu\n', 1, 'Duplicate parameter')

    def test_method_arity(self):
        self.failure('vagai B:\n    seiy f(naan, x):\n        x thirumbu\n'
                     '    mudivu\nmudivu\nb = B porul vechukko\nb.f()\n',
                     7, 'expects 1 argument')

    def test_method_needs_instance_parameter(self):
        self.failure('vagai B:\n    seiy f():\n        1 thirumbu\n'
                     '    mudivu\nmudivu\nb = B porul vechukko\nb.f()\n',
                     7, 'instance parameter')

    def test_missing_property(self):
        self.failure('vagai B:\n    seiy f(naan):\n        1 thirumbu\n'
                     '    mudivu\nmudivu\nb = B porul vechukko\nb.absent sollu\n',
                     7, 'no property')

    def test_property_on_non_object(self):
        self.failure('x = 1 vechukko\nx.value sollu\n', 2, 'porul')

    def test_bad_conversion(self):
        self.failure('value = ketukko("?") vechukko\nenn(value) sollu\n',
                     2, 'invalid literal', ['oops'])

    def test_missing_input(self):
        self.failure('kelu("?") sollu\n', 1, 'No input was supplied')

    def test_index_validation(self):
        self.failure('a = [1] vechukko\na[2] sollu\n', 2, 'out of range')
        self.failure('a = [1] vechukko\na[true] sollu\n', 2, 'integer')

    def test_division_by_zero(self):
        self.failure('1 / 0 sollu\n', 1, 'division by zero')

    def test_top_level_control_flow_errors(self):
        for source, name in [('nillu\n', 'nillu'), ('thodaru\n', 'thodaru'),
                             ('1 thirumbu\n', 'thirumbu')]:
            self.failure(source, 1, name)

    def test_break_cannot_escape_a_function_into_callers_loop(self):
        self.failure('seiy f():\n    nillu\nmudivu\ntrue varaikum:\n'
                     '    f()\nmudivu\n', 2, 'current function')

    def test_cli_builtin_demo_terminates(self):
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'src/mozhi.py')],
                                capture_output=True, text=True, timeout=4)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Woof woof!', result.stdout)
        self.assertNotIn('This will not print', result.stdout)

    def test_cli_reports_user_error_without_python_traceback(self):
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            p = pathlib.Path(folder) / 'bad.mozhi'
            p.write_text('1 / 0 sollu\n')
            result = subprocess.run([sys.executable, '-B', str(ROOT / 'src/mozhi.py'), str(p)],
                                    capture_output=True, text=True, timeout=4)
        self.assertEqual(result.returncode, 1)
        self.assertIn('Line 1:', result.stderr)
        self.assertNotIn('Traceback', result.stderr)

    def test_cli_reads_and_writes_utf8_in_legacy_locale(self):
        import os
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            p = pathlib.Path(folder) / 'unicode.mozhi'
            p.write_text('name = kelu("?") vechukko\nname sollu\n', encoding='utf-8')
            env = dict(os.environ, PYTHONIOENCODING='cp1252')
            result = subprocess.run([sys.executable, '-B', str(ROOT / 'src/mozhi.py'), str(p)],
                                    input='வணக்கம்\n'.encode('utf-8'), capture_output=True,
                                    timeout=4, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.decode('utf-8').replace('\r\n', '\n'), '?வணக்கம்\n')
