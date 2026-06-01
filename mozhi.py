"""
Mozhi - A Tanglish Programming Language
"Mozhi" means "language" in Tamil.

Syntax examples:
    "hello world" sollu          -> print("hello world")
    a = 10 vechukko              -> a = 10
    a = a + 1 vechukko
    i = 0 vechukko
    i < 5 varaikum:              -> while i < 5:
        i sollu
        i = i + 1 vechukko
    mudivu
    a == 10 na:                  -> if a == 10:
        "yes" sollu
    illana:                      -> else:
        "no" sollu
    mudivu
"""

from lark import Lark, Transformer, v_args, Tree, Token
import sys
import operator

# ─────────────────────────────────────────────
# GRAMMAR
# ─────────────────────────────────────────────

MOZHI_GRAMMAR = r"""
    start: statement+

    statement: assign_stmt
             | print_stmt
             | while_stmt
             | if_stmt
             | func_def
             | func_call_stmt
             | return_stmt
             | break_stmt

    // Variable assignment: name = expr vechukko
    assign_stmt: NAME "=" expr "vechukko" NEWLINE+

    // Print: expr sollu
    print_stmt: expr "sollu" NEWLINE+

    // While: expr varaikum: block mudivu
    while_stmt: expr "varaikum" ":" NEWLINE+ INDENT statement+ DEDENT "mudivu" NEWLINE*

    // If: expr na: block [illana: block] mudivu
    if_stmt: expr "na" ":" NEWLINE+ INDENT statement+ DEDENT ("illana" ":" NEWLINE+ INDENT statement+ DEDENT)? "mudivu" NEWLINE*

    // Function def: seiy name(params): block mudivu
    func_def: "seiy" NAME "(" params? ")" ":" NEWLINE+ INDENT statement+ DEDENT "mudivu" NEWLINE*

    // Function call as statement
    func_call_stmt: func_call NEWLINE+

    // Return: expr thirumbu
    return_stmt: expr "thirumbu" NEWLINE+

    // Break: nillு
    break_stmt: "nillu" NEWLINE+

    params: NAME ("," NAME)*

    // Expressions
    expr: or_expr

    or_expr: and_expr ("illaiyal" and_expr)*

    and_expr: not_expr ("mattrum" not_expr)*

    not_expr: "illa" not_expr -> not_expr
            | compare_expr

    compare_expr: add_expr (CMP_OP add_expr)*

    add_expr: mul_expr (("+"|"-") mul_expr)*

    mul_expr: unary_expr (("*"|"/"|"%") unary_expr)*

    unary_expr: "-" unary_expr -> neg_expr
              | primary

    primary: NUMBER          -> number
           | STRING          -> string
           | "true"          -> true_val
           | "false"         -> false_val
           | func_call
           | NAME            -> var
           | "(" expr ")"    -> paren

    func_call: NAME "(" args? ")"

    args: expr ("," expr)*

    CMP_OP: "==" | "!=" | "<=" | ">=" | "<" | ">"

    NAME: /[a-zA-Z_][a-zA-Z0-9_]*/
    NUMBER: /[0-9]+(\.[0-9]+)?/
    STRING: /\"[^\"]*\"|'[^']*'/

    NEWLINE: /\n/
    INDENT: "<INDENT>"
    DEDENT: "<DEDENT>"

    %ignore /[ \t]+/
    %ignore /#[^\n]*/
"""

# ─────────────────────────────────────────────
# INDENTATION PREPROCESSOR
# Lark doesn't do Python-style indentation natively,
# so we inject INDENT/DEDENT tokens manually.
# ─────────────────────────────────────────────

def preprocess_indentation(source: str) -> str:
    lines = source.split('\n')
    result = []
    indent_stack = [0]

    for line in lines:
        stripped = line.lstrip()

        # Skip blank lines and comments
        if not stripped or stripped.startswith('#'):
            result.append(line)
            continue

        indent = len(line) - len(stripped)
        current = indent_stack[-1]

        if indent > current:
            indent_stack.append(indent)
            result.append('<INDENT>')
            result.append(line)
        elif indent < current:
            while indent_stack[-1] > indent:
                indent_stack.pop()
                result.append('<DEDENT>')
            result.append(line)
        else:
            result.append(line)

    # Close any remaining indents
    while len(indent_stack) > 1:
        indent_stack.pop()
        result.append('<DEDENT>')

    return '\n'.join(result)

# ─────────────────────────────────────────────
# ENVIRONMENT (scope chain)
# ─────────────────────────────────────────────

class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"'da {name}' theriyala — define pannunga first")

    def set(self, name, value):
        self.vars[name] = value

    def set_existing(self, name, value):
        if name in self.vars:
            self.vars[name] = value
        elif self.parent:
            self.parent.set_existing(name, value)
        else:
            self.vars[name] = value

# ─────────────────────────────────────────────
# SIGNALS (control flow)
# ─────────────────────────────────────────────

class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value

class BreakSignal(Exception):
    pass

# ─────────────────────────────────────────────
# FUNCTION
# ─────────────────────────────────────────────

class MozhiFunction:
    def __init__(self, name, params, body, closure):
        self.name = name
        self.params = params
        self.body = body
        self.closure = closure

    def __repr__(self):
        return f"<mozhi function '{self.name}'>"

# ─────────────────────────────────────────────
# INTERPRETER
# ─────────────────────────────────────────────

CMP_OPS = {
    '==': operator.eq,
    '!=': operator.ne,
    '<':  operator.lt,
    '>':  operator.gt,
    '<=': operator.le,
    '>=': operator.ge,
}

class MozhiInterpreter:
    def __init__(self):
        self.global_env = Environment()

    def run(self, source: str):
        processed = preprocess_indentation(source)
        parser = Lark(MOZHI_GRAMMAR, parser='earley', ambiguity='resolve')
        try:
            tree = parser.parse(processed)
        except Exception as e:
            print(f"[Mozhi Syntax Error] {e}")
            sys.exit(1)
        self.exec_block(tree.children, self.global_env)

    def exec_block(self, stmts, env):
        for stmt in stmts:
            if isinstance(stmt, Tree):
                self.exec_stmt(stmt, env)

    def exec_stmt(self, node: Tree, env: Environment):
        t = node.data

        if t == 'assign_stmt':
            name = str(node.children[0])
            value = self.eval_expr(node.children[1], env)
            env.set(name, value)

        elif t == 'print_stmt':
            value = self.eval_expr(node.children[0], env)
            print(self.mozhi_repr(value))

        elif t == 'while_stmt':
            condition_node = node.children[0]
            body = node.children[1:]
            while self.is_truthy(self.eval_expr(condition_node, env)):
                try:
                    self.exec_block(body, Environment(env))
                except BreakSignal:
                    break

        elif t == 'if_stmt':
            condition_node = node.children[0]
            # Find INDENT/DEDENT boundaries — children after condition are if-body then optional else-body
            # We split manually: look for structure
            children = node.children[1:]
            # Split into if_body and else_body by counting — grammar ensures ordering
            if_body = []
            else_body = []
            in_else = False
            for child in children:
                if isinstance(child, Token) and str(child) == 'illana':
                    in_else = True
                    continue
                if in_else:
                    else_body.append(child)
                else:
                    if_body.append(child)

            if self.is_truthy(self.eval_expr(condition_node, env)):
                self.exec_block(if_body, Environment(env))
            elif else_body:
                self.exec_block(else_body, Environment(env))

        elif t == 'func_def':
            name = str(node.children[0])
            params_node = node.children[1] if isinstance(node.children[1], Tree) and node.children[1].data == 'params' else None
            params = [str(p) for p in params_node.children] if params_node else []
            body_start = 2 if params_node else 1
            body = node.children[body_start:]
            fn = MozhiFunction(name, params, body, env)
            env.set(name, fn)

        elif t == 'func_call_stmt':
            self.eval_expr(node.children[0], env)

        elif t == 'return_stmt':
            value = self.eval_expr(node.children[0], env)
            raise ReturnSignal(value)

        elif t == 'break_stmt':
            raise BreakSignal()

        elif t == 'statement':
            self.exec_stmt(node.children[0], env)

    def eval_expr(self, node, env: Environment):
        if isinstance(node, Token):
            return str(node)

        t = node.data

        if t == 'expr' or t == 'or_expr' or t == 'and_expr' or t == 'compare_expr' or t == 'add_expr' or t == 'mul_expr':
            return self.eval_binary(node, env)

        elif t == 'not_expr':
            return not self.is_truthy(self.eval_expr(node.children[0], env))

        elif t == 'neg_expr':
            return -self.eval_expr(node.children[0], env)

        elif t == 'paren':
            return self.eval_expr(node.children[0], env)

        elif t == 'number':
            val = str(node.children[0])
            return float(val) if '.' in val else int(val)

        elif t == 'string':
            raw = str(node.children[0])
            return raw[1:-1]  # strip quotes

        elif t == 'true_val':
            return True

        elif t == 'false_val':
            return False

        elif t == 'var':
            return env.get(str(node.children[0]))

        elif t == 'func_call':
            return self.eval_func_call(node, env)

        elif t == 'unary_expr' or t == 'primary':
            return self.eval_expr(node.children[0], env)

        else:
            # Fallthrough for wrapper nodes
            if len(node.children) == 1:
                return self.eval_expr(node.children[0], env)
            return self.eval_binary(node, env)

    def eval_binary(self, node, env):
        children = node.children
        if len(children) == 1:
            return self.eval_expr(children[0], env)

        t = node.data
        result = self.eval_expr(children[0], env)

        i = 1
        while i < len(children):
            op_token = str(children[i])
            right = self.eval_expr(children[i + 1], env)
            i += 2

            if op_token in CMP_OPS:
                result = CMP_OPS[op_token](result, right)
            elif op_token == '+':
                result = result + right
            elif op_token == '-':
                result = result - right
            elif op_token == '*':
                result = result * right
            elif op_token == '/':
                result = result / right
            elif op_token == '%':
                result = result % right
            elif op_token == 'mattrum':
                result = self.is_truthy(result) and self.is_truthy(right)
            elif op_token == 'illaiyal':
                result = self.is_truthy(result) or self.is_truthy(right)

        return result

    def eval_func_call(self, node, env):
        name = str(node.children[0])
        args_node = node.children[1] if len(node.children) > 1 and isinstance(node.children[1], Tree) else None
        args = [self.eval_expr(a, env) for a in args_node.children] if args_node else []

        # Built-ins
        if name == 'kelu':       # input
            prompt = args[0] if args else ''
            return input(str(prompt))
        elif name == 'neelavai': # len
            return len(args[0])
        elif name == 'enn':      # int cast
            return int(args[0])
        elif name == 'padam':    # float cast
            return float(args[0])
        elif name == 'vaari':    # str cast
            return str(args[0])

        fn = env.get(name)
        if not isinstance(fn, MozhiFunction):
            raise TypeError(f"'{name}' oru function illa da")

        if len(args) != len(fn.params):
            raise TypeError(f"'{name}' ku {len(fn.params)} arguments venum, {len(args)} kuduthunga")

        call_env = Environment(fn.closure)
        for param, arg in zip(fn.params, args):
            call_env.set(param, arg)

        try:
            self.exec_block(fn.body, call_env)
            return None
        except ReturnSignal as r:
            return r.value

    def is_truthy(self, val):
        if val is None or val is False or val == 0 or val == '':
            return False
        return True

    def mozhi_repr(self, val):
        if val is True: return 'true'
        if val is False: return 'false'
        if val is None: return 'onnum illa'
        if isinstance(val, float) and val.is_integer():
            return str(int(val))
        return str(val)

# ─────────────────────────────────────────────
# ENTRY
# ─────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python mozhi.py <file.mozhi>")
        print("       python mozhi.py --example")
        sys.exit(0)

    if sys.argv[1] == '--example':
        example = """
# Mozhi example program

"Vanakkam world!" sollu

a = 10 vechukko
b = 20 vechukko
c = a + b vechukko
c sollu

i = 1 vechukko
i <= 5 varaikum:
    i sollu
    i = i + 1 vechukko
mudivu

a == 10 na:
    "a paththu dhaan" sollu
illana:
    "a paththu illa" sollu
mudivu

seiy koodunga(x, y):
    x + y thirumbu
mudivu

result = koodunga(7, 8) vechukko
result sollu
"""
        interp = MozhiInterpreter()
        interp.run(example)
        return

    with open(sys.argv[1], 'r') as f:
        source = f.read()

    interp = MozhiInterpreter()
    interp.run(source)

if __name__ == '__main__':
    main()
