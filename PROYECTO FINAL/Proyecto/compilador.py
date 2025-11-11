# compilador.py
import re
import sys
from typing import List, Tuple, Dict, Any

# ------------------------
# TOKENS
# ------------------------
TOKENS = [
    ("PASS", r"\bpass\b"),
    ("NUMBER", r"\d+(\.\d+)?"),
    ("STRING", r"f?\".*?\"|f?'.*?'"),
    ("DEF", r"\bdef\b"),
    ("CLASS", r"\bclass\b"),
    ("IF", r"\bif\b"),
    ("ELSE", r"\belse\b"),
    ("ELIF", r"\belif\b"),
    ("FOR", r"\bfor\b"),
    ("WHILE", r"\bwhile\b"),
    ("RETURN", r"\breturn\b"),
    ("IN", r"\bin\b"),
    ("TRUE", r"\bTrue\b"),
    ("FALSE", r"\bFalse\b"),
    ("NONE", r"\bNone\b"),
    ("CONST", r"\bconst\b"),
    ("PRINT", r"\bprint\b"),
    ("INPUT", r"\binput\b"),
    ("IDENT", r"[A-Za-z_]\w*"),
    ("COMMENT", r"#.*"),
    ("AND", r"\band\b"),
    ("OR", r"\bor\b"),
    ("NOT", r"\bnot\b"),
    ("EQ", r"=="),
    ("NEQ", r"!="),
    ("LE", r"<="),
    ("GE", r">="),
    ("LT", r"<"),
    ("GT", r">"),
    ("PLUS", r"\+"),
    ("MINUS", r"-"),
    ("MUL", r"\*"),
    ("DIV", r"/"),
    ("MOD", r"%"),
    ("ASSIGN", r"="),
    ("COLON", r":"),
    ("COMMA", r","),
    ("DOT", r"\."),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("NEWLINE", r"\n"),
    ("SKIP", r"[ \t]+"),
    ("MISMATCH", r"."),
]

# ------------------------
# LEXER
# ------------------------
class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.tokens: List[Tuple[str,str,int,int]] = []
        self.tokenize()

    def tokenize(self):
        line_num = 1
        line_start = 0
        token_regex = "|".join("(?P<%s>%s)" % pair for pair in TOKENS)
        
        for mo in re.finditer(token_regex, self.code):
            kind = mo.lastgroup
            value = mo.group()
            column = mo.start() - line_start + 1
            
            if kind == "NEWLINE":
                line_num += 1
                line_start = mo.end()
                self.tokens.append((kind, value, line_num, column))
                continue
            elif kind in ("SKIP", "COMMENT"):
                continue
            elif kind == "MISMATCH":
                raise SyntaxError(f"❌ Error léxico (línea {line_num}, col {column}): carácter inesperado '{value}'")
            else:
                self.tokens.append((kind, value, line_num, column))

# ------------------------
# PARSER CORREGIDO
# ------------------------
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else ("EOF", "", 0, 0)

    def peek_type(self, type_):
        return self.peek()[0] == type_

    def match(self, *expected):
        tok = self.peek()
        if tok[0] in expected:
            self.pos += 1
            return tok
        raise SyntaxError(f"❌ Error sintáctico línea {tok[2]}: se esperaba {expected} y se encontró {tok[0]}")

    def parse(self):
        statements = []
        while not self.peek_type("EOF"):
            if self.peek_type("NEWLINE"):
                self.pos += 1
                continue
            stmt = self.statement()
            if stmt:
                statements.append(stmt)
        return ("program", statements)

    def statement(self):
        if self.peek_type("EOF"):
            return None
            
        tok = self.peek()

        # Retorno de funciones
        if self.peek_type("RETURN"):
            self.match("RETURN")
            expr = self.expression()
            return ("return", expr, tok[2])

        # Estructuras de control
        if self.peek_type("IF"):
            return self.if_stmt()
        if self.peek_type("FOR"):
            return self.for_stmt()
        if self.peek_type("WHILE"):
            return self.while_stmt()

        # Función
        if self.peek_type("DEF"):
            return self.func_def()

        # Clase
        if self.peek_type("CLASS"):
            return self.class_def()

        # Asignación o llamada
        if self.peek_type("IDENT"):
            ident = self.match("IDENT")
            
            # Acceso a atributo: obj.attr = value
            if self.peek_type("DOT"):
                self.match("DOT")
                attr = self.match("IDENT")[1]
                if self.peek_type("ASSIGN"):
                    self.match("ASSIGN")
                    expr = self.expression()
                    return ("attr_assign", ident[1], attr, expr, ident[2])
                elif self.peek_type("LPAREN"):
                    # Llamada a método: obj.method()
                    args = self.call_args()
                    return ("method_call", ident[1], attr, args, ident[2])
                else:
                    # Solo acceso: obj.attr
                    return ("attr_access", ident[1], attr, ident[2])
            
            elif self.peek_type("ASSIGN"):
                self.match("ASSIGN")
                expr = self.expression()
                return ("assign", ident[1], expr, ident[2])
            elif self.peek_type("LPAREN"):
                args = self.call_args()
                return ("call", ident[1], args, ident[2])
            else:
                return ("var", ident[1], ident[2])

        # Print
        if self.peek_type("PRINT"):
            self.match("PRINT")
            args = self.call_args()
            return ("print", args, tok[2])

        # Input
        if self.peek_type("INPUT"):
            self.match("INPUT")
            args = self.call_args()
            return ("input", args, tok[2])

        # Pass
        if self.peek_type("PASS"):
            self.match("PASS")
            return ("pass", tok[2])

        return None

    def func_def(self):
        self.match("DEF")
        name = self.match("IDENT")[1]
        self.match("LPAREN")
        params = []
        while not self.peek_type("RPAREN"):
            param = self.match("IDENT")[1]
            params.append(param)
            if self.peek_type("COMMA"):
                self.match("COMMA")
        self.match("RPAREN")
        self.match("COLON")
        
        if self.peek_type("NEWLINE"):
            self.match("NEWLINE")
        
        body = []
        while not self.peek_type("EOF"):
            if self.peek_type("DEF"):
                break
            
            if self.peek_type("NEWLINE"):
                self.match("NEWLINE")
                continue
                
            stmt = self.statement()
            if stmt:
                body.append(stmt)
            else:
                break
        
        return ("func_def", name, params, body)

    def class_def(self):
        self.match("CLASS")
        name = self.match("IDENT")[1]
        self.match("COLON")
        
        if self.peek_type("NEWLINE"):
            self.match("NEWLINE")
        
        methods = []
        while not self.peek_type("EOF"):
            if self.peek_type("CLASS") or self.peek_type("DEF"):
                # Si encontramos otra clase o función global, salir
                if self.peek_type("CLASS"):
                    break
                # Si es DEF, verificar si es un método de la clase
                if self.peek_type("DEF"):
                    method = self.func_def()
                    methods.append(method)
            elif self.peek_type("NEWLINE"):
                self.match("NEWLINE")
                continue
            elif self.peek_type("PASS"):
                self.match("PASS")
                if self.peek_type("NEWLINE"):
                    self.match("NEWLINE")
                break
            else:
                break
        
        return ("class_def", name, methods)

    def if_stmt(self):
        self.match("IF")
        condition = self.expression()
        self.match("COLON")
        
        if self.peek_type("NEWLINE"):
            self.match("NEWLINE")
        
        if_body = []
        while (not self.peek_type("EOF") and 
               not self.peek_type("ELSE") and 
               not self.peek_type("ELIF")):
            
            if self.peek_type("NEWLINE"):
                self.match("NEWLINE")
                continue
                
            stmt = self.statement()
            if stmt:
                if_body.append(stmt)
            else:
                break
        
        elif_cases = []
        while self.peek_type("ELIF"):
            self.match("ELIF")
            elif_condition = self.expression()
            self.match("COLON")
            
            if self.peek_type("NEWLINE"):
                self.match("NEWLINE")
            
            elif_body = []
            while (not self.peek_type("EOF") and 
                   not self.peek_type("ELSE") and 
                   not self.peek_type("ELIF")):
                
                if self.peek_type("NEWLINE"):
                    self.match("NEWLINE")
                    continue
                    
                stmt = self.statement()
                if stmt:
                    elif_body.append(stmt)
                else:
                    break
            
            elif_cases.append((elif_condition, elif_body))
        
        # Manejar else
        else_body = []
        if self.peek_type("ELSE"):
            self.match("ELSE")
            self.match("COLON")
            
            if self.peek_type("NEWLINE"):
                self.match("NEWLINE")
            
            while not self.peek_type("EOF"):
                if self.peek_type("NEWLINE"):
                    self.match("NEWLINE")
                    continue
                    
                stmt = self.statement()
                if stmt:
                    else_body.append(stmt)
                else:
                    break
        
        return ("if", condition, if_body, elif_cases, else_body)

    def for_stmt(self):
        self.match("FOR")
        var = self.match("IDENT")[1]
        self.match("IN")
        iterable = self.expression()
        self.match("COLON")
        
        if self.peek_type("NEWLINE"):
            self.match("NEWLINE")
        
        body = []
        while not self.peek_type("EOF"):
            if self.peek_type("NEWLINE"):
                self.match("NEWLINE")
                continue
                
            stmt = self.statement()
            if stmt:
                body.append(stmt)
            else:
                break
        
        return ("for", var, iterable, body)

    def while_stmt(self):
        self.match("WHILE")
        condition = self.expression()
        self.match("COLON")
        
        if self.peek_type("NEWLINE"):
            self.match("NEWLINE")
        
        body = []
        while not self.peek_type("EOF"):
            if self.peek_type("NEWLINE"):
                self.match("NEWLINE")
                continue
                
            stmt = self.statement()
            if stmt:
                body.append(stmt)
            else:
                break
        
        return ("while", condition, body)

    def call_args(self):
        args = []
        self.match("LPAREN")
        while not self.peek_type("RPAREN"):
            args.append(self.expression())
            if self.peek_type("COMMA"):
                self.match("COMMA")
        self.match("RPAREN")
        return args

    def expression(self):
        return self.logical_or()

    def logical_or(self):
        expr = self.logical_and()
        while self.peek_type("OR"):
            op_tok = self.match("OR")
            op = op_tok[1]
            right = self.logical_and()
            expr = ("binop", op, expr, right, op_tok[2])
        return expr

    def logical_and(self):
        expr = self.comparison()
        while self.peek_type("AND"):
            op_tok = self.match("AND")
            op = op_tok[1]
            right = self.comparison()
            expr = ("binop", op, expr, right, op_tok[2])
        return expr

    def comparison(self):
        expr = self.addition()
        while self.peek_type("EQ") or self.peek_type("NEQ") or self.peek_type("LT") or \
            self.peek_type("GT") or self.peek_type("LE") or self.peek_type("GE"):
            op_tok = self.match("EQ", "NEQ", "LT", "GT", "LE", "GE")
            op = op_tok[1]
            right = self.addition()
            expr = ("binop", op, expr, right, op_tok[2])
        return expr

    def addition(self):
        expr = self.term()
        while self.peek_type("PLUS") or self.peek_type("MINUS"):
            op_tok = self.match("PLUS", "MINUS")
            op = op_tok[1]
            right = self.term()
            expr = ("binop", op, expr, right, op_tok[2])
        return expr

    def term(self):
        expr = self.factor()
        while self.peek_type("MUL") or self.peek_type("DIV") or self.peek_type("MOD"):
            op_tok = self.match("MUL", "DIV", "MOD")
            op = op_tok[1]
            right = self.factor()
            expr = ("binop", op, expr, right, op_tok[2])
        return expr

    def factor(self):
        tok = self.peek()
        if tok[0] == "NUMBER":
            self.match("NUMBER")
            return ("number", tok[1])
        elif tok[0] == "STRING":
            self.match("STRING")
            return ("string", tok[1])
        elif tok[0] == "IDENT":
            ident = self.match("IDENT")
            
            # Acceso a atributo o método
            if self.peek_type("DOT"):
                self.match("DOT")
                attr = self.match("IDENT")[1]
                if self.peek_type("LPAREN"):
                    # Llamada a método
                    args = self.call_args()
                    return ("method_call", ident[1], attr, args, tok[2])
                else:
                    # Acceso a atributo
                    return ("attr_access", ident[1], attr, tok[2])
            
            elif self.peek_type("LPAREN"):
                args = self.call_args()
                return ("call", ident[1], args, tok[2])
            else:
                return ("var", ident[1], tok[2])
        elif tok[0] == "LPAREN":
            self.match("LPAREN")
            expr = self.expression()
            self.match("RPAREN")
            return expr
        elif tok[0] in ("TRUE", "FALSE"):
            self.match(tok[0])
            return ("bool", tok[1], tok[2])
        elif tok[0] == "INPUT":
            self.match("INPUT")
            args = self.call_args()
            return ("call", "input", args, tok[2])
        else:
            raise SyntaxError(f"❌ Error sintáctico línea {tok[2]}: expresión inesperada '{tok[1]}'")

# ------------------------
# SEMANTIC ANALYZER
# ------------------------
class SemanticAnalyzer:
    def __init__(self, tokens: List[Tuple[str,str,int,int]]):
        self.global_scope: Dict[str,Dict[str,Any]] = {}
        self.scopes: List[Dict[str,Dict[str,Any]]] = [self.global_scope]
        self.errors: List[str] = []
        self.tokens = tokens

        self.define('print', {"kind":"builtin","type":"function","params":["*args"],"line":0})
        self.define('input', {"kind":"builtin","type":"function","params":["prompt"],"line":0})
        self.define('int', {"kind":"builtin","type":"function","params":["x"],"line":0})
        self.define('range', {"kind":"builtin","type":"function","params":["start","stop"],"line":0})

    def define(self, name: str, info: Dict[str,Any]):
        sc = self.current_scope()
        if name in sc:
            self.errors.append(f"Ln {info.get('line','?')}: Símbolo '{name}' ya definido en este scope")
        sc[name] = info

    def current_scope(self):
        return self.scopes[-1]

    def analyze(self, ast: List[Any]):
        # Análisis simplificado
        for node in ast:
            if not node: continue
            kind = node[0]
            if kind == "assign":
                name = node[1]; line = node[3]
                self.define(name, {"kind":"var","type":"unknown","line":line})
            elif kind == "func_def":
                name = node[1]; line = 0
                self.define(name, {"kind":"function","type":"function","line":line})

# ------------------------
# EJECUTOR DEL AST MEJORADO
# ------------------------
class Executor:
    def __init__(self, ast, symbols):
        self.ast = ast
        self.symbols = symbols
        self.functions = {}  # Almacenar definiciones de funciones
        self.classes = {}    # Almacenar definiciones de clases
        self.return_value = None  # Para manejar return

    def run(self):
        try:
            for node in self.ast:
                result = self.execute(node)
                if self.return_value is not None:
                    val = self.return_value
                    self.return_value = None
                    return val
        except Exception as e:
            print(f"Error durante la ejecución: {e}")

    def execute(self, node):
        if node is None:
            return

        node_type = node[0]

        if node_type == "assign":
            _, name, value_node, _ = node
            val = self.eval_expr(value_node)
            if name not in self.symbols:
                self.symbols[name] = {"value": val}
            else:
                self.symbols[name]["value"] = val

        elif node_type == "attr_assign":
            # obj.attr = value
            _, obj_name, attr_name, value_node, _ = node
            val = self.eval_expr(value_node)
            
            if obj_name in self.symbols:
                obj = self.symbols[obj_name].get("value")
                if isinstance(obj, dict) and "__class__" in obj:
                    obj["__dict__"][attr_name] = val
            elif obj_name == "self" and "self" in self.symbols:
                obj = self.symbols["self"].get("value")
                if isinstance(obj, dict) and "__class__" in obj:
                    obj["__dict__"][attr_name] = val

        elif node_type == "if":
            condition = node[1]
            if_body = node[2]
            elif_cases = node[3] if len(node) > 3 else []
            else_body = node[4] if len(node) > 4 else []
            
            cond = self.eval_expr(condition)
            if cond:
                for stmt in if_body:
                    self.execute(stmt)
            else:
                # Probar elif cases
                executed = False
                for elif_cond, elif_body in elif_cases:
                    if self.eval_expr(elif_cond):
                        for stmt in elif_body:
                            self.execute(stmt)
                        executed = True
                        break
                
                if not executed and else_body:
                    for stmt in else_body:
                        self.execute(stmt)

        elif node_type == "call":
            _, func_name, args, line = node
            
            # Funciones builtin
            if func_name == "print":
                vals = [self.eval_expr(arg) for arg in args]
                print(*vals)
                return None
            elif func_name == "input":
                prompt = self.eval_expr(args[0]) if args else ""
                user_input = input(prompt)
                return user_input
            elif func_name == "int":
                val = self.eval_expr(args[0])
                return int(val) if val else 0
            elif func_name == "range":
                if len(args) == 1:
                    return range(self.eval_expr(args[0]))
                elif len(args) == 2:
                    return range(self.eval_expr(args[0]), self.eval_expr(args[1]))
                elif len(args) == 3:
                    return range(self.eval_expr(args[0]), self.eval_expr(args[1]), self.eval_expr(args[2]))
            
            # Funciones definidas por el usuario
            elif func_name in self.functions:
                func_def = self.functions[func_name]
                params = func_def['params']
                body = func_def['body']
                
                # Crear nuevo scope para la función
                old_symbols = self.symbols.copy()
                
                # Asignar argumentos a parámetros
                for i, param in enumerate(params):
                    if i < len(args):
                        self.symbols[param] = {"value": self.eval_expr(args[i])}
                
                # Ejecutar cuerpo de la función
                result = None
                for stmt in body:
                    self.execute(stmt)
                    if self.return_value is not None:
                        result = self.return_value
                        self.return_value = None
                        break
                
                # Restaurar scope anterior
                self.symbols = old_symbols
                return result
            
            # Instanciación de clases
            elif func_name in self.classes:
                class_def = self.classes[func_name]
                instance = {"__class__": func_name, "__dict__": {}}
                
                # Buscar y ejecutar __init__ si existe
                if "__init__" in class_def['methods']:
                    init_method = class_def['methods']['__init__']
                    old_symbols = self.symbols.copy()
                    
                    # self es la instancia
                    self.symbols['self'] = {"value": instance}
                    
                    # Asignar argumentos (sin contar self)
                    params = init_method['params'][1:]  # Saltar 'self'
                    for i, param in enumerate(params):
                        if i < len(args):
                            self.symbols[param] = {"value": self.eval_expr(args[i])}
                    
                    # Ejecutar __init__
                    for stmt in init_method['body']:
                        self.execute(stmt)
                    
                    self.symbols = old_symbols
                
                return instance
            else:
                return None

        elif node_type == "method_call":
            # obj.method(args)
            _, obj_name, method_name, args, _ = node
            
            # Obtener el objeto
            obj = None
            if obj_name in self.symbols:
                obj = self.symbols[obj_name].get("value")
            
            if obj and isinstance(obj, dict) and "__class__" in obj:
                class_name = obj["__class__"]
                if class_name in self.classes:
                    class_def = self.classes[class_name]
                    if method_name in class_def['methods']:
                        method = class_def['methods'][method_name]
                        
                        old_symbols = self.symbols.copy()
                        
                        # self es el objeto
                        self.symbols['self'] = {"value": obj}
                        
                        # Asignar argumentos (sin contar self)
                        params = method['params'][1:] if method['params'] else []
                        for i, param in enumerate(params):
                            if i < len(args):
                                self.symbols[param] = {"value": self.eval_expr(args[i])}
                        
                        # Ejecutar método
                        result = None
                        for stmt in method['body']:
                            self.execute(stmt)
                            if self.return_value is not None:
                                result = self.return_value
                                self.return_value = None
                                break
                        
                        self.symbols = old_symbols
                        return result
            
            return None

        elif node_type == "func_def":
            # Guardar la definición de función
            _, name, params, body = node
            self.functions[name] = {
                'params': params,
                'body': body
            }
            # También agregar a symbols para el análisis semántico
            if name not in self.symbols:
                self.symbols[name] = {"kind": "function", "value": None}

        elif node_type == "class_def":
            # Guardar la definición de clase
            _, name, methods = node
            class_methods = {}
            
            # Procesar cada método
            for method in methods:
                if method[0] == "func_def":
                    method_name = method[1]
                    method_params = method[2]
                    method_body = method[3]
                    class_methods[method_name] = {
                        'params': method_params,
                        'body': method_body
                    }
            
            self.classes[name] = {
                'methods': class_methods
            }
            # También agregar a symbols
            if name not in self.symbols:
                self.symbols[name] = {"kind": "class", "value": None}

        elif node_type == "for":
            _, var, iterable, body = node
            iter_val = self.eval_expr(iterable)
            
            # Iterar sobre el iterable
            for item in iter_val:
                self.symbols[var] = {"value": item}
                for stmt in body:
                    self.execute(stmt)
                    if self.return_value is not None:
                        return

        elif node_type == "while":
            _, condition, body = node
            while self.eval_expr(condition):
                for stmt in body:
                    self.execute(stmt)
                    if self.return_value is not None:
                        return

        elif node_type == "return":
            _, expr, line = node
            self.return_value = self.eval_expr(expr)
            return self.return_value

        elif node_type == "print":
            _, args, line = node
            vals = [self.eval_expr(arg) for arg in args]
            print(*vals)

        elif node_type == "input":
            _, args, line = node
            prompt = self.eval_expr(args[0]) if args else ""
            user_input = input(prompt)
            return user_input

    def eval_expr(self, expr):
        if expr is None:
            return None
            
        etype = expr[0]
        
        if etype == "number":
            val = expr[1]
            if '.' in val:
                return float(val)
            else:
                return int(val)
                
        elif etype == "string":
            val = expr[1]
            return val.strip('"\'')
            
        elif etype == "bool":
            val = expr[1]
            return val == "True"
            
        elif etype == "var":
            name = expr[1]
            if name in self.symbols:
                return self.symbols[name].get("value", None)
            else:
                return f"[Variable {name} no definida]"
        
        elif etype == "attr_access":
            # obj.attr
            _, obj_name, attr_name, _ = expr
            
            if obj_name in self.symbols:
                obj = self.symbols[obj_name].get("value")
                if isinstance(obj, dict) and "__class__" in obj:
                    return obj["__dict__"].get(attr_name, None)
            elif obj_name == "self" and "self" in self.symbols:
                obj = self.symbols["self"].get("value")
                if isinstance(obj, dict) and "__class__" in obj:
                    return obj["__dict__"].get(attr_name, None)
            
            return None
        
        elif etype == "method_call":
            return self.execute(expr)
                
        elif etype == "call":
            return self.execute(expr)
            
        elif etype == "binop":
            _, op, left, right, _ = expr
            left_val = self.eval_expr(left)
            right_val = self.eval_expr(right)
            
            if op == '+':
                return left_val + right_val
            elif op == '-':
                return left_val - right_val
            elif op == '*':
                return left_val * right_val
            elif op == '/':
                return left_val / right_val if right_val != 0 else "indefinida"
            elif op == '%':
                return left_val % right_val
            elif op == '==':
                return left_val == right_val
            elif op == '!=':
                return left_val != right_val
            elif op == '<':
                return left_val < right_val
            elif op == '>':
                return left_val > right_val
            elif op == '<=':
                return left_val <= right_val
            elif op == '>=':
                return left_val >= right_val
            elif op == 'and':
                return left_val and right_val
            elif op == 'or':
                return left_val or right_val
                
        return None

# ------------------------
# MAIN SIMPLIFICADO
# ------------------------
def main():
    import os

    path = input("Ingresa la ruta del archivo .py a compilar: ").strip()

    if not os.path.exists(path):
        print("❌ El archivo no existe.")
        return

    with open(path, "r", encoding="utf-8") as file:
        code = file.read()

    try:
        exec(code, {})
        
    except Exception as e:
        print(f"❌ Error durante la ejecución: {e}")

if __name__ == "__main__":
    main()