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

        indent = len(line) - len(line.lstrip())
        current_indent = indent_stack[-1]

        if indent > current_indent:
            indent_stack.append(indent)
            tokens.append(Token(TT_INDENT, indent, lineno))
        elif indent < current_indent:
            while indent_stack[-1] > indent:
                indent_stack.pop()
                tokens.append(Token(TT_DEDENT, indent, lineno))

        content = stripped
        col = 0
        while col < len(content):
            if content[col] == ' ':
                col += 1
                continue

            if content[col] == '#':
                break

            # String
            if content[col] in ('"', "'"):
                q = content[col]
                end = col + 1
                while end < len(content):
                    if content[end] == q and content[end-1] != '\\':
                        break
                    end += 1
                
                if end >= len(content):
                     raise SyntaxError(f"[Mozhi] Line {lineno}: String a close panniya da? Missing closing quote.")
                
                val = content[col+1:end].replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace("\\'", "'")
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
            for op in ('==', '!=', '<=', '>=', '<', '>', '+', '-', '*', '/', '%', '=', '**'):
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
        left = self.parse_pow()
        while self.peek().type == TT_OP and self.peek().value in ('*', '/', '%'):
            op = self.consume().value
            right = self.parse_pow()
            left = BinOp(left, op, right)
        return left

    def parse_pow(self):
        left = self.parse_unary()
        while self.peek().type == TT_OP and self.peek().value == '**':
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

CMP = {'==': operator.eq, '!=': operator.ne, '<': operator.lt,
       '>': operator.gt, '<=': operator.le, '>=': operator.ge}

BUILTINS = {
    'kelu':     lambda args: input(str(args[0]) if args else ''),
    'neelam':   lambda args: len(args[0]),
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
                except ContinueSignal:
                    continue

        elif isinstance(node, If):
            if self.truthy(self.eval(node.cond, env)):
                self.exec_block(node.then_body, Environment(env))
            elif node.else_body:
                self.exec_block(node.else_body, Environment(env))

        elif isinstance(node, FuncDef):
            env.set(node.name, MozhiFunction(node.name, node.params, node.body, env))
            
        elif isinstance(node, ClassDef):
            methods = {}
            for m in node.methods:
                 methods[m.name] = m
            env.set(node.name, MozhiClass(node.name, methods))

        elif isinstance(node, Return):
            raise ReturnSignal(self.eval(node.expr, env))

        elif isinstance(node, Break):
            raise BreakSignal()
            
        elif isinstance(node, Continue):
            raise ContinueSignal()
            
        elif isinstance(node, Exit):
            print("Podhum, I am out.")
            sys.exit(0)

        elif isinstance(node, ArrayPush):
            target = self.eval(node.array_expr, env)
            val = self.eval(node.value_expr, env)
            if not isinstance(target, list):
                raise TypeError(f"[Mozhi] Ithu varisai (list) illa da! Can't ullapodu.")
            target.append(val)

        elif isinstance(node, ArrayPop):
            target = self.eval(node.array_expr, env)
            if not isinstance(target, list):
                raise TypeError(f"[Mozhi] Ithu varisai (list) illa da! Can't veliyapodu.")
            if len(target) == 0:
                 raise IndexError(f"[Mozhi] Varisai is empty! Can't veliyapodu.")
            target.pop()

        elif isinstance(node, FuncCall) or isinstance(node, MethodCall):
            self.eval(node, env)

        else:
            raise RuntimeError(f"[Mozhi] Exec theriyala: {type(node).__name__}")

    def eval(self, node, env):
        if isinstance(node, Num):   return node.value
        if isinstance(node, Str):   return node.value
        if isinstance(node, Bool):  return node.value
        if isinstance(node, Var):   return env.get(node.name)
        
        if isinstance(node, ArrayLiteral):
             return [self.eval(e, env) for e in node.elements]
             
        if isinstance(node, ObjectInstantiation):
             cls = env.get(node.class_name)
             if not isinstance(cls, MozhiClass):
                  raise TypeError(f"[Mozhi] '{node.class_name}' vagai (class) illa da!")
             return MozhiObject(cls)

        if isinstance(node, ArrayIndex):
             arr = self.eval(node.array_expr, env)
             idx = self.eval(node.index_expr, env)
             if not isinstance(arr, list):
                  raise TypeError(f"[Mozhi] Enna da panni vechiruka? {type(arr).__name__} is not a varisai.")
             if not isinstance(idx, int):
                  raise TypeError(f"[Mozhi] Index must be a number, not {type(idx).__name__}.")
             try:
                 return arr[idx]
             except IndexError:
                 raise IndexError(f"[Mozhi] Index out of range da! List length is {len(arr)}.")

        if isinstance(node, BinOp):
            l = self.eval(node.left, env)
            r = self.eval(node.right, env)
            op = node.op
            
            # String concatenation
            if op == '+' or op == 'kooda':
                 if isinstance(l, str) or isinstance(r, str):
                     return str(l) + str(r)
                 return l + r
            
            if op in CMP:           
                try:
                    return CMP[op](l, r)
                except TypeError:
                    raise TypeError(f"[Mozhi] Enna da panni vechiruka? Can't compare {type(l).__name__} with {type(r).__name__}")
            if op == '-':           return l - r
            if op == '*':           return l * r
            if op == '/':           return l / r
            if op == '%':           return l % r
            if op == '**':          return l ** r
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
                
        if isinstance(node, MethodCall):
            obj = self.eval(node.obj_expr, env)
            if not isinstance(obj, MozhiObject):
                raise TypeError(f"[Mozhi] That's not a porul (object)! Can't call method '{node.method_name}'.")
            
            if node.method_name not in obj.mozhi_class.methods:
                raise AttributeError(f"[Mozhi] '{obj.mozhi_class.name}' vagai la '{node.method_name}' method illa da!")
                
            method_def = obj.mozhi_class.methods[node.method_name]
            
            # Methods must have at least 'self' (let's call it 'naan' in Mozhi)
            if len(method_def.params) == 0:
                raise TypeError(f"[Mozhi] Method '{node.method_name}' must have at least one parameter for 'naan' (self).")
                
            if len(node.args) != len(method_def.params) - 1:
                raise TypeError(f"[Mozhi] Method '{node.method_name}' expects {len(method_def.params) - 1} args, got {len(node.args)}.")
                
            call_env = Environment(method_def.closure)
            # Bind the object instance to the first parameter ('naan')
            call_env.set(method_def.params[0], obj)
            for p, a in zip(method_def.params[1:], node.args):
                call_env.set(p, self.eval(a, env))
                
            try:
                self.exec_block(method_def.body, call_env)
                return None
            except ReturnSignal as r:
                return r.value

        raise RuntimeError(f"[Mozhi] Eval theriyala: {type(node).__name__}")

    def truthy(self, v):
        return v not in (None, False, 0, 0.0, '', [])

    def mozhi_repr(self, v):
        if v is True:  return 'true'
        if v is False: return 'false'
        if v is None:  return 'onnum illa'
        if isinstance(v, list): return '[' + ', '.join(self.mozhi_repr(x) for x in v) + ']'
        if isinstance(v, float) and v.is_integer(): return str(int(v))
        return str(v)

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