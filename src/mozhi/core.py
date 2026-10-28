import sys
import re
import operator
import math
import pathlib
import random
import time

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
TT_LBRACKET = 'LBRACKET'
TT_RBRACKET = 'RBRACKET'
TT_COMMA    = 'COMMA'
TT_COLON    = 'COLON'
TT_NEWLINE  = 'NEWLINE'
TT_INDENT   = 'INDENT'
TT_DEDENT   = 'DEDENT'
TT_EOF      = 'EOF'
TT_DOT      = 'DOT'

KEYWORDS = {
    'sollu', 'vechukko', 'varaikum', 'na', 'illana',
    'mudivu', 'seiy', 'thirumbu', 'nillu', 'thodaru',
    'mattrum', 'illaiyal', 'illa', 'true', 'false',
    'kooda', 'ullapodu', 'veliyapodu', 'vagai', 'porul', 'podhum'
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
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue

        prefix = line[:len(line) - len(line.lstrip())]
        if ' ' in prefix and '\t' in prefix:
            raise SyntaxError(f"[Mozhi] Line {lineno}: Do not mix tabs and spaces in indentation.")
        indent = len(prefix.expandtabs(4))
        current_indent = indent_stack[-1]

        if indent > current_indent:
            if not tokens or tokens[-2].type != TT_COLON:
                raise SyntaxError(f"[Mozhi] Line {lineno}: Unexpected indentation; a block must follow ':'.")
            indent_stack.append(indent)
            tokens.append(Token(TT_INDENT, indent, lineno))
        elif indent < current_indent:
            if indent not in indent_stack:
                raise SyntaxError(f"[Mozhi] Line {lineno}: Indentation does not match an outer block.")
            while indent_stack[-1] > indent:
                indent_stack.pop()
                tokens.append(Token(TT_DEDENT, indent, lineno))

        content = stripped
        col = 0
        while col < len(content):
            if content[col].isspace():
                col += 1
                continue

            if content[col] == '#':
                break

            # String
            if content[col] in ('"', "'"):
                q = content[col]
                end = col + 1
                chars = []
                escapes = {'n': '\n', 't': '\t', '\\': '\\', '"': '"', "'": "'"}
                while end < len(content) and content[end] != q:
                    if content[end] == '\\' and end + 1 < len(content):
                        escaped = content[end + 1]
                        chars.append(escapes.get(escaped, '\\' + escaped))
                        end += 2
                    else:
                        chars.append(content[end])
                        end += 1
                if end >= len(content):
                    raise SyntaxError(f"[Mozhi] Line {lineno}: Missing closing quote.")
                val = ''.join(chars)
                tokens.append(Token(TT_STRING, val, lineno))
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
            for op in ('==', '!=', '<=', '>=', '**', '<', '>', '+', '-', '*', '/', '%', '='):
                if content[col:].startswith(op):
                    tokens.append(Token(TT_OP, op, lineno))
                    col += len(op)
                    break
            else:
                c = content[col]
                if c == '(':
                    tokens.append(Token(TT_LPAREN, '(', lineno))
                elif c == ')':
                    tokens.append(Token(TT_RPAREN, ')', lineno))
                elif c == '[':
                    tokens.append(Token(TT_LBRACKET, '[', lineno))
                elif c == ']':
                    tokens.append(Token(TT_RBRACKET, ']', lineno))
                elif c == ',':
                    tokens.append(Token(TT_COMMA, ',', lineno))
                elif c == ':':
                    tokens.append(Token(TT_COLON, ':', lineno))
                elif c == '.':
                    tokens.append(Token(TT_DOT, '.', lineno))
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

    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append(Token(TT_DEDENT, 0, 0))

    tokens.append(Token(TT_EOF, None, len(lines) or 1))
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

class ClassDef:
    def __init__(self, name, methods): self.name = name; self.methods = methods

class Return:
    def __init__(self, expr): self.expr = expr

class Break:
    pass

class Continue:
    pass

class Exit:
    pass

class ArrayPush:
    def __init__(self, array_expr, value_expr): self.array_expr = array_expr; self.value_expr = value_expr

class ArrayPop:
    def __init__(self, array_expr): self.array_expr = array_expr

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

class ArrayLiteral:
    def __init__(self, elements): self.elements = elements

class ArrayIndex:
    def __init__(self, array_expr, index_expr): self.array_expr = array_expr; self.index_expr = index_expr

class ObjectInstantiation:
    def __init__(self, class_name): self.class_name = class_name

class MethodCall:
    def __init__(self, obj_expr, method_name, args): self.obj_expr = obj_expr; self.method_name = method_name; self.args = args

class FuncCall:
    def __init__(self, name, args): self.name = name; self.args = args

class PropertyAccess:
    def __init__(self, obj_expr, name): self.obj_expr = obj_expr; self.name = name

class PropertyAssign:
    def __init__(self, obj_name, prop_name, expr):
        self.obj_name = obj_name; self.prop_name = prop_name; self.expr = expr

# ─────────────────────────────────────────────
# PARSER
# ─────────────────────────────────────────────

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[min(self.pos, len(self.tokens) - 1)]

    def peek2(self):
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return Token(TT_EOF, None)

    def consume(self, type_=None, value=None):
        tok = self.peek()
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
        line = self.peek().line
        node = self._parse_stmt()
        node.line = line
        return node

    def _parse_stmt(self):
        tok = self.peek()

        if tok.type == TT_KEYWORD and tok.value == 'seiy':
            return self.parse_func_def()

        if tok.type == TT_KEYWORD and tok.value == 'vagai':
            return self.parse_class_def()

        if tok.type == TT_KEYWORD and tok.value == 'nillu':
            self.consume()
            self.consume(TT_NEWLINE)
            return Break()

        if tok.type == TT_KEYWORD and tok.value == 'thodaru':
            self.consume()
            self.consume(TT_NEWLINE)
            return Continue()
            
        if tok.type == TT_KEYWORD and tok.value == 'podhum':
            self.consume()
            self.consume(TT_NEWLINE)
            return Exit()

        if (tok.type == TT_NAME and self.peek2().type == TT_DOT
                and self.pos + 3 < len(self.tokens)
                and self.tokens[self.pos + 2].type == TT_NAME
                and self.tokens[self.pos + 3].value == '='):
            obj_name = self.consume(TT_NAME).value
            self.consume(TT_DOT)
            prop_name = self.consume(TT_NAME).value
            self.consume(TT_OP, '=')
            expr = self.parse_expr()
            self.consume(TT_KEYWORD, 'vechukko')
            self.consume(TT_NEWLINE)
            return PropertyAssign(obj_name, prop_name, expr)

        if tok.type == TT_NAME and self.peek2().type == TT_OP and self.peek2().value == '=':
            return self.parse_assign()

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

        elif nxt.type == TT_KEYWORD and nxt.value == 'ullapodu':
            self.consume()
            target_array = self.parse_expr() 
            self.consume(TT_NEWLINE)
            return ArrayPush(target_array, expr)

        elif nxt.type == TT_KEYWORD and nxt.value == 'veliyapodu':
             self.consume()
             self.consume(TT_NEWLINE)
             return ArrayPop(expr)

        elif nxt.type == TT_NEWLINE:
            self.consume(TT_NEWLINE)
            return expr

        raise SyntaxError(f"[Mozhi] Line {nxt.line}: Enna pannara? '{nxt.value}' theriyala")

    def parse_assign(self):
        name = self.consume(TT_NAME).value
        self.consume(TT_OP, '=')
        
        # Check for object instantiation: name = ClassName porul vechukko
        if self.peek().type == TT_NAME and self.peek2().type == TT_KEYWORD and self.peek2().value == 'porul':
            class_name = self.consume(TT_NAME).value
            self.consume(TT_KEYWORD, 'porul')
            expr = ObjectInstantiation(class_name)
        else:
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
        if len(set(params)) != len(params):
            raise SyntaxError(f"[Mozhi] Line {self.peek().line}: Duplicate parameter in '{name}'.")
        self.consume(TT_COLON)
        self.consume(TT_NEWLINE)
        body = self.parse_block()
        self.consume(TT_KEYWORD, 'mudivu')
        self.consume(TT_NEWLINE)
        return FuncDef(name, params, body)

    def parse_class_def(self):
        self.consume(TT_KEYWORD, 'vagai')
        name = self.consume(TT_NAME).value
        self.consume(TT_COLON)
        self.consume(TT_NEWLINE)
        self.consume(TT_INDENT)
        self.skip_newlines()
        methods = []
        while self.peek().type != TT_DEDENT and self.peek().type != TT_EOF:
             if self.peek().type == TT_KEYWORD and self.peek().value == 'seiy':
                 methods.append(self.parse_func_def())
                 self.skip_newlines()
             else:
                 raise SyntaxError(f"[Mozhi] Line {self.peek().line}: Vagai (class) kulla function matum than irukanum.")
        self.consume(TT_DEDENT)
        self.consume(TT_KEYWORD, 'mudivu')
        self.consume(TT_NEWLINE)
        return ClassDef(name, methods)

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
        while (self.peek().type == TT_OP and self.peek().value in ('+', '-')) or (self.peek().type == TT_KEYWORD and self.peek().value == 'kooda'):
            op = self.consume().value
            right = self.parse_mul()
            left = BinOp(left, op, right)
        return left

    def parse_mul(self):
        left = self.parse_unary()
        while self.peek().type == TT_OP and self.peek().value in ('*', '/', '%'):
            op = self.consume().value
            left = BinOp(left, op, self.parse_unary())
        return left

    def parse_pow(self):
        left = self.parse_primary()
        if self.peek().type == TT_OP and self.peek().value == '**':
            self.consume()
            return BinOp(left, '**', self.parse_unary())
        return left

    def parse_unary(self):
        if self.peek().type == TT_OP and self.peek().value in ('-', '+'):
            op = self.consume().value
            return UnaryOp(op, self.parse_unary())
        return self.parse_pow()

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
            
        if tok.type == TT_LBRACKET:
            self.consume(TT_LBRACKET)
            elements = []
            if self.peek().type != TT_RBRACKET:
                elements.append(self.parse_expr())
                while self.peek().type == TT_COMMA:
                    self.consume(TT_COMMA)
                    elements.append(self.parse_expr())
            self.consume(TT_RBRACKET)
            return ArrayLiteral(elements)

        if tok.type == TT_LPAREN:
            self.consume(TT_LPAREN)
            expr = self.parse_expr()
            self.consume(TT_RPAREN)
            return expr

        # Name, function call, array access, or method call
        if tok.type == TT_NAME:
            name = self.consume(TT_NAME).value
            
            # Function Call
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
            
            node = Var(name)
            
            # Array Indexing and Method Calls can be chained
            while True:
                if self.peek().type == TT_LBRACKET:
                    self.consume(TT_LBRACKET)
                    index_expr = self.parse_expr()
                    self.consume(TT_RBRACKET)
                    node = ArrayIndex(node, index_expr)
                elif self.peek().type == TT_DOT:
                    self.consume(TT_DOT)
                    method_name = self.consume(TT_NAME).value
                    if self.peek().type == TT_LPAREN:
                        self.consume(TT_LPAREN)
                        args = []
                        if self.peek().type != TT_RPAREN:
                            args.append(self.parse_expr())
                            while self.peek().type == TT_COMMA:
                                self.consume(TT_COMMA)
                                args.append(self.parse_expr())
                        self.consume(TT_RPAREN)
                        node = MethodCall(node, method_name, args)
                    else:
                        node = PropertyAccess(node, method_name)
                else:
                    break
            
            return node

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
        raise NameError(f"[Mozhi] Variable '{name}' illa da! Add it first using 'vechukko'")

    def set(self, name, value):
        scope = self
        while scope is not None:
            if name in scope.vars:
                scope.vars[name] = value
                return
            scope = scope.parent
        self.vars[name] = value

class MozhiFunction:
    def __init__(self, name, params, body, closure):
        self.name = name; self.params = params
        self.body = body; self.closure = closure
    def __repr__(self):
        return f"<mozhi seiy '{self.name}'>"

class MozhiClass:
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods
    def __repr__(self):
        return f"<mozhi vagai '{self.name}'>"

class MozhiObject:
    def __init__(self, mozhi_class):
        self.mozhi_class = mozhi_class
        self.properties = {}
    def __repr__(self):
        return f"<{self.mozhi_class.name} porul>"

class ReturnSignal(Exception):
    def __init__(self, value): self.value = value

class BreakSignal(Exception):
    pass

class ContinueSignal(Exception):
    pass

class ExitSignal(Exception): pass

class MozhiError(Exception):
    """A user-facing runtime failure with the source statement's line."""
    def __init__(self, message, line):
        self.line = line
        self.detail = str(message).removeprefix('[Mozhi] ')
        super().__init__(f"[Mozhi] Line {line}: {self.detail}")

CMP = {'==': operator.eq, '!=': operator.ne, '<': operator.lt,
       '>': operator.gt, '<=': operator.le, '>=': operator.ge}

def read_input(args):
    return input(str(args[0]) if args else '')

def file_read(args):
    if not isinstance(args[0], str):
        raise TypeError("padi requires a path string.")
    return pathlib.Path(args[0]).read_text(encoding='utf-8')

def file_write(args, append=False):
    if not all(isinstance(value, str) for value in args):
        raise TypeError("File writing requires path and text strings.")
    with open(args[0], 'a' if append else 'w', encoding='utf-8', newline='') as output:
        output.write(args[1])

def random_value(args):
    if not args:
        return random.random()
    if len(args) != 2 or any(type(value) is not int for value in args):
        raise TypeError("seeratra expects no arguments or two integer bounds.")
    return random.randint(args[0], args[1])

def string_split(args):
    if not all(isinstance(value, str) for value in args):
        raise TypeError("pirithu requires string arguments.")
    return args[0].split(args[1])

def string_join(args):
    if not isinstance(args[0], list) or not isinstance(args[1], str):
        raise TypeError("inaithu requires a varisai and separator string.")
    return args[1].join(args[0])

def string_replace(args):
    if not all(isinstance(value, str) for value in args):
        raise TypeError("maatru requires three strings.")
    return args[0].replace(args[1], args[2])

BUILTINS = {
    'kelu': read_input,
    'ketukko': read_input,
    'neelam': lambda args: len(args[0]),
    'enn': lambda args: int(args[0]),
    'padam': lambda args: float(args[0]),
    'vaari': lambda args: str(args[0]),
    'neram': lambda args: time.perf_counter(),
    'seeratra': random_value,
    'padi': file_read,
    'ezhuthu': file_write,
    'serthu_ezhuthu': lambda args: file_write(args, append=True),
    'pirithu': string_split,
    'inaithu': string_join,
    'maatru': string_replace,
    'ver': lambda args: math.sqrt(args[0]),
}
BUILTIN_ARITY = {'kelu': (0, 1), 'ketukko': (0, 1),
                 'neelam': (1, 1), 'enn': (1, 1), 'padam': (1, 1), 'vaari': (1, 1)}
BUILTIN_ARITY.update({'neram': (0, 0), 'seeratra': (0, 2), 'padi': (1, 1),
                     'ezhuthu': (2, 2), 'serthu_ezhuthu': (2, 2), 'pirithu': (2, 2),
                     'inaithu': (2, 2), 'maatru': (3, 3), 'ver': (1, 1)})

class Interpreter:
    def __init__(self):
        self.loop_depth = 0
        self.function_depth = 0

    def exec_block(self, stmts, env):
        for stmt in stmts:
            self.exec(stmt, env)

    def exec(self, node, env):
        try:
            return self._exec(node, env)
        except (ExitSignal, ReturnSignal, BreakSignal, ContinueSignal, MozhiError):
            raise
        except (NameError, TypeError, ValueError, IndexError, AttributeError,
                ZeroDivisionError, OverflowError, RecursionError, EOFError, OSError) as error:
            raise MozhiError(error, getattr(node, 'line', 1)) from None

    def _exec(self, node, env):
        if isinstance(node, Assign):
            env.set(node.name, self.eval(node.expr, env))
        elif isinstance(node, PropertyAssign):
            obj = env.get(node.obj_name)
            if not isinstance(obj, MozhiObject):
                raise TypeError(f"'{node.obj_name}' is not a porul (object).")
            obj.properties[node.prop_name] = self.eval(node.expr, env)
        elif isinstance(node, Print):
            print(self.mozhi_repr(self.eval(node.expr, env)))
        elif isinstance(node, While):
            self.loop_depth += 1
            try:
                while self.truthy(self.eval(node.cond, env)):
                    try:
                        self.exec_block(node.body, Environment(env))
                    except BreakSignal:
                        break
                    except ContinueSignal:
                        continue
            finally:
                self.loop_depth -= 1
        elif isinstance(node, If):
            body = node.then_body if self.truthy(self.eval(node.cond, env)) else node.else_body
            self.exec_block(body, Environment(env))
        elif isinstance(node, FuncDef):
            env.set(node.name, MozhiFunction(node.name, node.params, node.body, env))
        elif isinstance(node, ClassDef):
            methods = {m.name: MozhiFunction(m.name, m.params, m.body, env) for m in node.methods}
            env.set(node.name, MozhiClass(node.name, methods))
        elif isinstance(node, Return):
            if not self.function_depth:
                raise TypeError("thirumbu requires a function or method.")
            raise ReturnSignal(self.eval(node.expr, env))
        elif isinstance(node, Break):
            if not self.loop_depth:
                raise TypeError("nillu requires a loop in the current function.")
            raise BreakSignal()
        elif isinstance(node, Continue):
            if not self.loop_depth:
                raise TypeError("thodaru requires a loop in the current function.")
            raise ContinueSignal()
        elif isinstance(node, Exit):
            print("[Mozhi] Podhum, I am out.")
            raise ExitSignal()
        elif isinstance(node, ArrayPush):
            target = self.eval(node.array_expr, env)
            if not isinstance(target, list):
                raise TypeError("ullapodu requires a varisai (list).")
            target.append(self.eval(node.value_expr, env))
        elif isinstance(node, ArrayPop):
            target = self.eval(node.array_expr, env)
            if not isinstance(target, list):
                raise TypeError("veliyapodu requires a varisai (list).")
            if not target:
                raise IndexError("Cannot pop an empty varisai (list).")
            target.pop()
        else:
            return self.eval(node, env)

    def eval_builtin(self, name, args):
        return BUILTINS[name](args)

    def call(self, fn, args, instance=None):
        if not isinstance(fn, MozhiFunction):
            raise TypeError("The requested value is not a function.")
        if instance is not None and not fn.params:
            raise TypeError(f"Method '{fn.name}' needs an instance parameter (naan).")
        values = ([instance] if instance is not None else []) + args
        expected = len(fn.params) - (1 if instance is not None else 0)
        if len(values) != len(fn.params):
            raise TypeError(f"'{fn.name}' expects {expected} argument(s), got {len(args)}.")
        call_env = Environment(fn.closure)
        call_env.vars.update(zip(fn.params, values))
        old_loop_depth = self.loop_depth
        self.loop_depth = 0
        self.function_depth += 1
        try:
            self.exec_block(fn.body, call_env)
        except ReturnSignal as result:
            return result.value
        finally:
            self.loop_depth = old_loop_depth
            self.function_depth -= 1
        return None

    def eval(self, node, env):
        if isinstance(node, (Num, Str, Bool)):
            return node.value
        if isinstance(node, Var):
            return env.get(node.name)
        if isinstance(node, ArrayLiteral):
            return [self.eval(e, env) for e in node.elements]
        if isinstance(node, ObjectInstantiation):
            cls = env.get(node.class_name)
            if not isinstance(cls, MozhiClass):
                raise TypeError(f"'{node.class_name}' is not a vagai (class).")
            return MozhiObject(cls)
        if isinstance(node, ArrayIndex):
            arr = self.eval(node.array_expr, env)
            idx = self.eval(node.index_expr, env)
            if not isinstance(arr, list):
                raise TypeError("Indexing requires a varisai (list).")
            if type(idx) is not int:
                raise TypeError("A varisai index must be an integer.")
            if not -len(arr) <= idx < len(arr):
                raise IndexError(f"Index {idx} is out of range for length {len(arr)}.")
            return arr[idx]
        if isinstance(node, PropertyAccess):
            obj = self.eval(node.obj_expr, env)
            if not isinstance(obj, MozhiObject):
                raise TypeError("Property access requires a porul (object).")
            if node.name not in obj.properties:
                raise AttributeError(f"'{obj.mozhi_class.name}' has no property '{node.name}'.")
            return obj.properties[node.name]
        if isinstance(node, BinOp):
            left = self.eval(node.left, env)
            if node.op == 'mattrum':
                return self.truthy(left) and self.truthy(self.eval(node.right, env))
            if node.op == 'illaiyal':
                return self.truthy(left) or self.truthy(self.eval(node.right, env))
            right = self.eval(node.right, env)
            if node.op in ('+', 'kooda'):
                return str(left) + str(right) if isinstance(left, str) or isinstance(right, str) else left + right
            if node.op in CMP: return CMP[node.op](left, right)
            if node.op == '-': return left - right
            if node.op == '*': return left * right
            if node.op == '/': return left / right
            if node.op == '%': return left % right
            if node.op == '**': return left ** right
        if isinstance(node, UnaryOp):
            value = self.eval(node.operand, env)
            if node.op == '-': return -value
            if node.op == '+': return +value
            if node.op == 'illa': return not self.truthy(value)
        if isinstance(node, FuncCall):
            args = [self.eval(arg, env) for arg in node.args]
            if node.name in BUILTINS:
                minimum, maximum = BUILTIN_ARITY[node.name]
                if not minimum <= len(args) <= maximum:
                    count = str(minimum) if minimum == maximum else f"{minimum} to {maximum}"
                    raise TypeError(f"'{node.name}' expects {count} argument(s), got {len(args)}.")
                return self.eval_builtin(node.name, args)
            return self.call(env.get(node.name), args)
        if isinstance(node, MethodCall):
            obj = self.eval(node.obj_expr, env)
            if not isinstance(obj, MozhiObject):
                raise TypeError(f"'{node.method_name}' requires a porul (object).")
            if node.method_name not in obj.mozhi_class.methods:
                raise AttributeError(f"'{obj.mozhi_class.name}' has no method '{node.method_name}'.")
            args = [self.eval(arg, env) for arg in node.args]
            return self.call(obj.mozhi_class.methods[node.method_name], args, obj)
        raise TypeError(f"Unsupported expression: {type(node).__name__}.")

    def truthy(self, value):
        return bool(value)

    def mozhi_repr(self, value):
        if value is True: return 'true'
        if value is False: return 'false'
        if value is None: return 'onnum illa'
        if isinstance(value, list): return '[' + ', '.join(self.mozhi_repr(x) for x in value) + ']'
        if isinstance(value, float) and value.is_integer(): return str(int(value))
        return str(value)

# ─────────────────────────────────────────────
# ENTRY
# ─────────────────────────────────────────────

EXAMPLE = """\
# Mozhi full test!

# 1. Strings & Concatenation
name = "Nanba" vechukko
greeting = "Vanakkam, " kooda name vechukko
greeting sollu

# 2. Arrays (varisai) and Push/Pop
numbers = [10, 20, 30] vechukko
99 ullapodu numbers
numbers sollu
numbers veliyapodu
"After pop: " kooda numbers sollu
"First element: " kooda numbers[0] sollu

# 3. Loops with continue (thodaru) and break (nillu)
"Looping:" sollu
i = 0 vechukko
i < 5 varaikum:
    i = i + 1 vechukko
    i == 3 na:
        thodaru
    mudivu
    i == 5 na:
        nillu
    mudivu
    i sollu
mudivu

# 4. Classes (Vagai) & Objects (Porul)
vagai Dog:
    seiy bark(naan, sound):
        sound sollu
    mudivu
mudivu

myDog = Dog porul vechukko
myDog.bark("Woof woof!")

# Exit program
podhum
"This will not print" sollu
"""

def run(source: str):
    tokens = tokenize(source)
    parser = Parser(tokens)
    ast = parser.parse()
    interp = Interpreter()
    try:
        interp.exec_block(ast, Environment())
    except ExitSignal:
        pass
