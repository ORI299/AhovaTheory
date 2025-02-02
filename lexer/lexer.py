import re

class ScriptError(Exception):
    pass

class Token:
    def __init__(self, type, value, real_type="None", options={}):
        self.type = type
        self.value = value
        self.options = options
        self.i = None
    def __repr__(self):
        return f'Token({self.type}, {self.value}, {self.i})'

class Lexer:
    def __init__(self, code):
        self.code = code
        self.pos = 0

    def get_token(self):
        if self.pos >= len(self.code):
            return Token('EOF', None)

        match = re.match(r'\s+', self.code[self.pos:])
        if match:
            self.pos += match.end()
            return self.get_token()

        if self.code[self.pos] == "#":
            self.pos += 1
            temp = ""
            while self.pos < len(self.code):
                self.pos += 1
                try:
                    temp += self.code[self.pos]
                except:
                    raise ScriptError(f"unclosed SKIP token!")
                if self.code[self.pos] == '#':
                    self.pos += 1
                    break
            
            return Token('SKIP', temp)

        if self.code.startswith('for', self.pos):
            self.pos += 3
            return Token('FOR', 'for')

        if self.code.startswith('in', self.pos):
            self.pos += 3
            return Token('IN', 'in')

        # Add new tokens for groups/lists
        if self.code[self.pos] == '{':
            self.pos += 1
            return Token('LGROUP', '{')

        if self.code[self.pos] == '}':
            self.pos += 1
            return Token('RGROUP', '}')

        if self.code[self.pos] == '<':
            self.pos += 1
            return Token('LANGLE', '<')

        if self.code[self.pos] == '>':
            self.pos += 1
            return Token('RANGLE', '>')

        if self.code[self.pos] == ',':
            self.pos += 1
            return Token('COMMA', ',')

        if self.code.startswith('echo', self.pos):
            self.pos += 4
            return Token('ECHO', 'echo')

        if self.code.startswith('let', self.pos):
            self.pos += 3
            return Token('LET', 'let')

        if self.code.startswith('if', self.pos):
            self.pos += 2
            return Token('IF', 'if')

        if self.code.startswith('else', self.pos):
            self.pos += 4
            return Token('ELSE', 'else')

        if self.code.startswith('while', self.pos):
            self.pos += 5
            return Token('WHILE', 'while')



        if self.code[self.pos] == '=':
            if self.code.startswith('==', self.pos):
                self.pos += 2
                return Token('EQ', '==')
            self.pos += 1
            return Token('ASSIGN', '=')

        if self.code.startswith('>=', self.pos):
            self.pos += 2
            return Token('GTE', '>=')

        if self.code.startswith('<=', self.pos):
            self.pos += 2
            return Token('LTE', '<=')

        if self.code.startswith('!=', self.pos):
            self.pos += 2
            return Token('NEQ', '!=')

        if self.code.startswith('calc(', self.pos):
            self.pos += 5
            return Token('CALCLPAREN', 'calc(')

        if self.code[self.pos] == '>':
            self.pos += 1
            return Token('GT', '>')

        if self.code[self.pos] == '<':
            self.pos += 1
            return Token('LT', '<')

        if self.code[self.pos] == '(':
            self.pos += 1
            return Token('LPAREN', '(')

        if self.code[self.pos] == ')':
            self.pos += 1
            return Token('RPAREN', ')')

        if self.code[self.pos].isdigit():
            num = ''
            while self.pos < len(self.code) and self.code[self.pos].isdigit():
                num += self.code[self.pos]
                self.pos += 1
            return Token('NUM', int(num))

        if self.code[self.pos] == '.':
            num = ''
            while self.pos < len(self.code) and (self.code[self.pos].isdigit() or self.code[self.pos] == '.'):
                num += self.code[self.pos]
                self.pos += 1
            return Token('FLOAT', float(num))


        if self.code[self.pos] in ('"', "'"):  # Detect string start
            quote_char = self.code[self.pos]
            self.pos += 1
            string_value = ''
        
            while self.pos < len(self.code) and self.code[self.pos] != quote_char:
                string_value += self.code[self.pos]
                self.pos += 1
        
            if self.pos < len(self.code) and self.code[self.pos] == quote_char:
                self.pos += 1  # Move past the closing quote
                return Token('STRING', string_value)
        
            raise Exception("Unterminated string literal")

        if self.code[self.pos] == 'f' and self.code[self.pos + 1] in ('"', "'"):  # Detect f-string start
            quote_char = self.code[self.pos + 1]
            self.pos += 2  # Move past 'f' and opening quote
            string_value = ''
            options = {"IDENTIFIERS": []}
            temp = False
            identifier = ""

            while self.pos < len(self.code) and self.code[self.pos] != quote_char:
                if self.code[self.pos] == "{":
                    temp = True
                    identifier = ""  # Start collecting the identifier
                elif self.code[self.pos] == "}":
                    temp = False
                    if identifier:
                        options["IDENTIFIERS"].append(identifier)  # Store complete identifier
                elif temp:
                    identifier += self.code[self.pos]  # Collect identifier characters
                
                string_value += self.code[self.pos]
                self.pos += 1

            if self.pos < len(self.code) and self.code[self.pos] == quote_char:
                self.pos += 1  # Move past the closing quote
                return Token('FSTRING', string_value, options)

            raise Exception("Unterminated f-string literal")


        #TODO: replace isalpha with a different method that allows _
        if self.code[self.pos].isalpha():  # This handles identifiers
            name = ''
            while self.pos < len(self.code) and (self.code[self.pos].isalpha() or self.code[self.pos].isdigit()):
                name += self.code[self.pos]
                self.pos += 1
            return Token('IDENTIFIER', name)

        if self.code[self.pos] == '+':
            self.pos += 1
            return Token('ADD', '+')

        if self.code[self.pos] == '-':
            self.pos += 1
            return Token('SUB', '-')

        if self.code[self.pos] == '*':
            self.pos += 1
            return Token('MUL', '*')

        if self.code[self.pos] == '/':
            self.pos += 1
            return Token('DIV', '/')

        if self.code[self.pos] == '%':
            self.pos += 1
            return Token('MOD', '%')

        if self.code[self.pos] == ';':
            self.pos += 1
            return Token('SEMICOLON', ';')

        raise ScriptError(f'Invalid character: {self.code[self.pos]}')

    def tokenize(self):
        tokens = []
        n = 0
        while True:
            n += 1
            token = self.get_token()
            token.i = n
            tokens.append(token)
            if token.type == 'EOF':
                break
        return tokens