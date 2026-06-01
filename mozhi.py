"""
Mozhi - A Tanglish Programming Language
"Mozhi" means "language" in Tamil.

Syntax:
    "hello world" sollu              -> print
    a = 10 vechukko                  -> variable assignment
    i <= 5 varaikum:                 -> while loop
        ...
    mudivu
    a == 10 na:                      -> if
        ...
    illana:                          -> else
        ...
    mudivu
    seiy add(x, y):                  -> function def
        x + y thirumbu
    mudivu
    result = add(3, 4) vechukko

Built-ins:
    kelu("prompt")   -> input()
    neelavai(x)      -> len(x)
    enn(x)           -> int(x)
    padam(x)         -> float(x)
    vaari(x)         -> str(x)

Operators:
    mattrum          -> and
    illaiyal         -> or
    illa <expr>      -> not
"""

import sys
import re
import operator

# ─────────────────────────────────────────────
# TOKENIZER
# ─────────────────────────────────────────────

TT_NUMBER   = 'NUMBER'
TT_STRING   = 'STRING'
TT_NAME     = 'NAME'
TT_KEYWORD  = 'KEYWORD'
TT_OP       = 'OP'
TT_LPAREN   = 'LPAREN'
TT_RPAREN   = 'RPAREN'
TT_COMMA    = 'COMMA'
TT_COLON    = 'COLON'
TT_NEWLINE  = 'NEWLINE'
TT_INDENT   = 'INDENT'
TT_DEDENT   = 'DEDENT'
TT_EOF      = 'EOF'

KEYWORDS = {
    'sollu', 'vechukko', 'varaikum', 'na', 'illana',
    'mudivu', 'seiy', 'thirumbu', 'nillu',
    'mattrum', 'illaiyal', 'illa', 'true', 'false'
}

class Token:
    def __init__(self, type_, value, line=0):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        return f'Token({self.type}, {self.value!r})'

def tokenize(source: str):
    tokens = []
    lines = source.splitlines(keepends=True)
    indent_stack = [0]

    for lineno, line in enumerate(lines, 1):
        # Skip blank lines and comments
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue

        # Measure indent
        indent = len(line) - len(line.lstrip())
        current_indent = indent_stack[-1]

        if indent > current_indent:
            indent_stack.append(indent)
            tokens.append(Token(TT_INDENT, indent, lineno))
        elif indent < current_indent:
            while indent_stack[-1] > indent:
                indent_stack.pop()
                tokens.append(Token(TT_DEDENT, indent, lineno))

        # Lex the actual content
        content = stripped
        col = 0
        while col < len(content):
            # Skip spaces
            if content[col] == ' ':
                col += 1
                continue

            # Comment
            if content[col] == '#':
                break

            # String
            if content[col] in ('"', "'"):
                q = content[col]
                end = content.index(q, col + 1)
                tokens.append(Token(TT_STRING, content[col+1:end], lineno))
                col = end + 1
                continue

            # Number
            m = re.match(r'\d+(\.\d+)?', content[col:])
            if m:
                val = m.group()
                tokens.append(Token(TT_NUMBER, float(val) if '.' in val else int(val), lineno))
                col += len(val)
                continue

            # Operators
            for op in ('==', '!=', '<=', '>=', '<', '>', '+', '-', '*', '/', '%', '='):
                if content[col:].startswith(op):
                    tokens.append(Token(TT_OP, op, lineno))
                    col += len(op)
                    break
            else:
                # Single chars
                c = content[col]
                if c == '(':
                    tokens.append(Token(TT_LPAREN, '(', lineno))
                elif c == ')':
                    tokens.append(Token(TT_RPAREN, ')', lineno))
                elif c == ',':
                    tokens.append(Token(TT_COMMA, ',', lineno))
                elif c == ':':
                    tokens.append(Token(TT_COLON, ':', lineno))
                elif re.match(r'[a-zA-Z_]', c):
                    m2 = re.match(r'[a-zA-Z_][a-zA-Z0-9_]*', content[col:])
                    word = m2.group()
                    tt = TT_KEYWORD if word in KEYWORDS else TT_NAME
                    tokens.append(Token(tt, word, lineno))
                    col += len(word)
                    continue
                else:
                    raise SyntaxError(f"[Mozhi] Line {lineno}: Theriyatha character '{c}'")
                col += 1

        tokens.append(Token(TT_NEWLINE, '\n', lineno))

    # Close remaining indents
    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append(Token(TT_DEDENT, 0, 0))

    tokens.append(Token(TT_EOF, None, 0))
    return tokens

# ─────────────────────────────────────────────
# AST NODES
# ─────────────────────────────────────────────

class Assign:
    def __init__(self, name, expr): self.name = name; self.expr = expr

class Print:
    def __init__(self, expr): self.expr = expr

class While:
    def __init__(self, cond, body): self.cond = cond; self.body = body

class If:
    def __init__(self, cond, then_body, else_body): self.cond = cond; self.then_body = then_body; self.else_body = else_body

class FuncDef:
    def __init__(self, name, params, body): self.name = name; self.params = params; self.body = body

class Return:
    def __init__(self, expr): self.expr = expr

class Break:
    pass

class BinOp:
    def __init__(self, left, op, right): self.left = left; self.op = op; self.right = right

class UnaryOp:
    def __init__(self, op, operand): self.op = op; self.operand = operand

class Num:
    def __init__(self, value): self.value = value

class Str:
    def __init__(self, value): self.value = value

class Bool:
    def __init__(self, value): self.value = value

class Var:
    def __init__(self, name): self.name = name

class FuncCall:
    def __init__(self, name, args): self.name = name; self.args = args

# ─────────────────────────────────────────────
# PARSER
# ─────────────────────────────────────────────

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def peek2(self):
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return Token(TT_EOF, None)

    def consume(self, type_=None, value=None):
        tok = self.tokens[self.pos]
        if type_ and tok.type != type_:
            raise SyntaxError(f"[Mozhi] Line {tok.line}: Expected {type_}, got {tok.type} ({tok.value!r})")
        if value and tok.value != value:
            raise SyntaxError(f"[Mozhi] Line {tok.line}: Expected '{value}', got '{tok.value}'")
        self.pos += 1
        return tok

    def skip_newlines(self):
        while self.peek().type == TT_NEWLINE:
            self.pos += 1

    def parse(self):
        stmts = []
        self.skip_newlines()
        while self.peek().type != TT_EOF:
            stmts.append(self.parse_stmt())
            self.skip_newlines()
        return stmts

    def parse_block(self):
        self.consume(TT_INDENT)
        self.skip_newlines()
        stmts = []
        while self.peek().type not in (TT_DEDENT, TT_EOF):
            stmts.append(self.parse_stmt())
            self.skip_newlines()
        self.consume(TT_DEDENT)
        return stmts

    def parse_stmt(self):
        tok = self.peek()

        # Function definition: seiy name(...):
        if tok.type == TT_KEYWORD and tok.value == 'seiy':
            return self.parse_func_def()

        # Break
        if tok.type == TT_KEYWORD and tok.value == 'nillu':
            self.consume()
            self.consume(TT_NEWLINE)
            return Break()

        # Assignment check: NAME = expr vechukko
        # We need lookahead: NAME followed by '='
        if tok.type == TT_NAME and self.peek2().type == TT_OP and self.peek2().value == '=':
            return self.parse_assign()

        # Otherwise parse expr and check trailing keyword
        expr = self.parse_expr()
        nxt = self.peek()

        if nxt.type == TT_KEYWORD and nxt.value == 'sollu':
            self.consume()
            self.consume(TT_NEWLINE)
            return Print(expr)

        elif nxt.type == TT_KEYWORD and nxt.value == 'thirumbu':
            self.consume()
            self.consume(TT_NEWLINE)
            return Return(expr)

        elif nxt.type == TT_KEYWORD and nxt.value == 'varaikum':
            self.consume()
            self.consume(TT_COLON)
            self.consume(TT_NEWLINE)
            body = self.parse_block()
            self.consume(TT_KEYWORD, 'mudivu')
            self.consume(TT_NEWLINE)
            return While(expr, body)

        elif nxt.type == TT_KEYWORD and nxt.value == 'na':
            self.consume()
            self.consume(TT_COLON)
            self.consume(TT_NEWLINE)
            then_body = self.parse_block()
            else_body = []
            if self.peek().type == TT_KEYWORD and self.peek().value == 'illana':
                self.consume()
                self.consume(TT_COLON)
                self.consume(TT_NEWLINE)
                else_body = self.parse_block()
            self.consume(TT_KEYWORD, 'mudivu')
            self.consume(TT_NEWLINE)
            return If(expr, then_body, else_body)

        # Bare function call as statement
        elif nxt.type == TT_NEWLINE:
            self.consume(TT_NEWLINE)
            return expr  # will be FuncCall node

        raise SyntaxError(f"[Mozhi] Line {nxt.line}: Enna pannara? '{nxt.value}' theriyala")

    def parse_assign(self):
        name = self.consume(TT_NAME).value
        self.consume(TT_OP, '=')
        expr = self.parse_expr()
        self.consume(TT_KEYWORD, 'vechukko')
        self.consume(TT_NEWLINE)
        return Assign(name, expr)

    def parse_func_def(self):
        self.consume(TT_KEYWORD, 'seiy')
        name = self.consume(TT_NAME).value
        self.consume(TT_LPAREN)
        params = []
        if self.peek().type == TT_NAME:
            params.append(self.consume(TT_NAME).value)
            while self.peek().type == TT_COMMA:
                self.consume(TT_COMMA)
                params.append(self.consume(TT_NAME).value)
        self.consume(TT_RPAREN)
        self.consume(TT_COLON)
        self.consume(TT_NEWLINE)
        body = self.parse_block()
        self.consume(TT_KEYWORD, 'mudivu')
        self.consume(TT_NEWLINE)
        return FuncDef(name, params, body)

    # Expression parsing (precedence climbing)
    def parse_expr(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.peek().type == TT_KEYWORD and self.peek().value == 'illaiyal':
            self.consume()
            right = self.parse_and()
            left = BinOp(left, 'illaiyal', right)
        return left

    def parse_and(self):
        left = self.parse_not()
        while self.peek().type == TT_KEYWORD and self.peek().value == 'mattrum':
            self.consume()
            right = self.parse_not()
            left = BinOp(left, 'mattrum', right)
        return left

    def parse_not(self):
        if self.peek().type == TT_KEYWORD and self.peek().value == 'illa':
            self.consume()
            return UnaryOp('illa', self.parse_not())
        return self.parse_compare()

    def parse_compare(self):
        left = self.parse_add()
        while self.peek().type == TT_OP and self.peek().value in ('==', '!=', '<', '>', '<=', '>='):
            op = self.consume().value
            right = self.parse_add()
            left = BinOp(left, op, right)
        return left

    def parse_add(self):
        left = self.parse_mul()
        while self.peek().type == TT_OP and self.peek().value in ('+', '-'):
            op = self.consume().value
            right = self.parse_mul()
            left = BinOp(left, op, right)
        return left

    def parse_mul(self):
        left = self.parse_unary()
        while self.peek().type == TT_OP and self.peek().value in ('*', '/', '%'):
            op = self.consume().value
            right = self.parse_unary()
            left = BinOp(left, op, right)
        return left

    def parse_unary(self):
        if self.peek().type == TT_OP and self.peek().value == '-':
            self.consume()
            return UnaryOp('-', self.parse_unary())
        return self.parse_primary()

    def parse_primary(self):
        tok = self.peek()

        if tok.type == TT_NUMBER:
            self.consume()
            return Num(tok.value)

        if tok.type == TT_STRING:
            self.consume()
            return Str(tok.value)

        if tok.type == TT_KEYWORD and tok.value == 'true':
            self.consume()
            return Bool(True)

        if tok.type == TT_KEYWORD and tok.value == 'false':
            self.consume()
            return Bool(False)

        if tok.type == TT_LPAREN:
            self.consume(TT_LPAREN)
            expr = self.parse_expr()
            self.consume(TT_RPAREN)
            return expr

        # Name or function call
        if tok.type == TT_NAME:
            name = self.consume(TT_NAME).value
            if self.peek().type == TT_LPAREN:
                self.consume(TT_LPAREN)
                args = []
                if self.peek().type != TT_RPAREN:
                    args.append(self.parse_expr())
                    while self.peek().type == TT_COMMA:
                        self.consume(TT_COMMA)
                        args.append(self.parse_expr())
                self.consume(TT_RPAREN)
                return FuncCall(name, args)
            return Var(name)

        raise SyntaxError(f"[Mozhi] Line {tok.line}: Unexpected '{tok.value}' — enna ithu?")

# ─────────────────────────────────────────────
# RUNTIME
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
        raise NameError(f"[Mozhi] '{name}' theriyala da — vechukko pannunga first")

    def set(self, name, value):
        self.vars[name] = value

class MozhiFunction:
    def __init__(self, name, params, body, closure):
        self.name = name; self.params = params
        self.body = body; self.closure = closure
    def __repr__(self):
        return f"<mozhi seiy '{self.name}'>"

class ReturnSignal(Exception):
    def __init__(self, value): self.value = value

class BreakSignal(Exception):
    pass

CMP = {'==': operator.eq, '!=': operator.ne, '<': operator.lt,
       '>': operator.gt, '<=': operator.le, '>=': operator.ge}

BUILTINS = {
    'kelu':     lambda args: input(str(args[0]) if args else ''),
    'neelavai': lambda args: len(args[0]),
    'enn':      lambda args: int(args[0]),
    'padam':    lambda args: float(args[0]),
    'vaari':    lambda args: str(args[0]),
}

class Interpreter:
    def exec_block(self, stmts, env):
        for stmt in stmts:
            self.exec(stmt, env)

    def exec(self, node, env):
        if isinstance(node, Assign):
            env.set(node.name, self.eval(node.expr, env))

        elif isinstance(node, Print):
            print(self.mozhi_repr(self.eval(node.expr, env)))

        elif isinstance(node, While):
            while self.truthy(self.eval(node.cond, env)):
                try:
                    self.exec_block(node.body, Environment(env))
                except BreakSignal:
                    break

        elif isinstance(node, If):
            if self.truthy(self.eval(node.cond, env)):
                self.exec_block(node.then_body, Environment(env))
            elif node.else_body:
                self.exec_block(node.else_body, Environment(env))

        elif isinstance(node, FuncDef):
            env.set(node.name, MozhiFunction(node.name, node.params, node.body, env))

        elif isinstance(node, Return):
            raise ReturnSignal(self.eval(node.expr, env))

        elif isinstance(node, Break):
            raise BreakSignal()

        elif isinstance(node, FuncCall):
            self.eval(node, env)

        else:
            raise RuntimeError(f"[Mozhi] Exec theriyala: {type(node).__name__}")

    def eval(self, node, env):
        if isinstance(node, Num):   return node.value
        if isinstance(node, Str):   return node.value
        if isinstance(node, Bool):  return node.value
        if isinstance(node, Var):   return env.get(node.name)

        if isinstance(node, BinOp):
            l = self.eval(node.left, env)
            r = self.eval(node.right, env)
            op = node.op
            if op in CMP:           return CMP[op](l, r)
            if op == '+':           return l + r
            if op == '-':           return l - r
            if op == '*':           return l * r
            if op == '/':           return l / r
            if op == '%':           return l % r
            if op == 'mattrum':     return self.truthy(l) and self.truthy(r)
            if op == 'illaiyal':    return self.truthy(l) or self.truthy(r)

        if isinstance(node, UnaryOp):
            v = self.eval(node.operand, env)
            if node.op == '-':   return -v
            if node.op == 'illa': return not self.truthy(v)

        if isinstance(node, FuncCall):
            if node.name in BUILTINS:
                args = [self.eval(a, env) for a in node.args]
                return BUILTINS[node.name](args)
            fn = env.get(node.name)
            if not isinstance(fn, MozhiFunction):
                raise TypeError(f"[Mozhi] '{node.name}' function illa")
            if len(node.args) != len(fn.params):
                raise TypeError(f"[Mozhi] '{node.name}' ku {len(fn.params)} args venum, {len(node.args)} kuduthunga")
            call_env = Environment(fn.closure)
            for p, a in zip(fn.params, node.args):
                call_env.set(p, self.eval(a, env))
            try:
                self.exec_block(fn.body, call_env)
                return None
            except ReturnSignal as r:
                return r.value

        raise RuntimeError(f"[Mozhi] Eval theriyala: {type(node).__name__}")

    def truthy(self, v):
        return v not in (None, False, 0, 0.0, '')

    def mozhi_repr(self, v):
        if v is True:  return 'true'
        if v is False: return 'false'
        if v is None:  return 'onnum illa'
        if isinstance(v, float) and v.is_integer(): return str(int(v))
        return str(v)

# ─────────────────────────────────────────────
# ENTRY
# ─────────────────────────────────────────────

EXAMPLE = """\
# Mozhi example — Vanakkam!

"Vanakkam world!" sollu

a = 10 vechukko
b = 32 vechukko
c = a + b vechukko
c sollu

# While loop
i = 1 vechukko
i <= 5 varaikum:
    i sollu
    i = i + 1 vechukko
mudivu

# If / else
a == 10 na:
    "a paththu dhaan!" sollu
illana:
    "a vera edhaavo" sollu
mudivu

# Function
seiy koodunga(x, y):
    x + y thirumbu
mudivu

result = koodunga(7, 8) vechukko
result sollu

# Nested condition
seiy check(n):
    n > 100 na:
        "periya number" sollu
    illana:
        "chinna number" sollu
    mudivu
mudivu

check(42)
check(200)
"""

def run(source: str):
    tokens = tokenize(source)
    parser = Parser(tokens)
    ast = parser.parse()
    interp = Interpreter()
    interp.exec_block(ast, Environment())

def main():
    if len(sys.argv) < 2 or sys.argv[1] == '--example':
        print("─── Mozhi Example ───")
        run(EXAMPLE)
        return
    with open(sys.argv[1], 'r') as f:
        run(f.read())

if __name__ == '__main__':
    main()
