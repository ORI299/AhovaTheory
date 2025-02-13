from colorama import Fore, init
from sys import stdout
from lexer.lexer import ScriptError

import re

# Initialize colorama
init(convert=False)

class Token:
    def __init__(self, type, value, real_type="None", options={}):
        self.type = type
        self.value = value
        self.options = options

    def __repr__(self):
        return f'Token({self.type}, {self.value})'

class Interpreter:
    def __init__(self):
        self.variables = {}
        self.pos = 0
        self.tokens = []
        
    def error(self, message):
        token = self.peek()
        raise ScriptError(f"Runtime Error at token {token.i}: {message}")
        
    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token('EOF', None)
        
    def advance(self):
        token = self.peek()
        self.pos += 1
        return token
    
    def deadvance(self):
        self.pos -= 1
        
        return self.tokens[self.pos]

    def expect(self, type):
        token = self.advance()
        if token.type != type:
            self.error(f"Expected {type}, got {token.type}")
        return token

    def parse_primary(self):
        token = self.peek()
        
        if token.type in ('NUM', 'FLOAT'):
            self.advance()
            return token.value
            
        elif token.type == 'STRING':
            self.advance()
            return token.value
            
        elif token.type == 'FSTRING':
            self.advance()
            result = token.value

            # Regular expression to find placeholders within curly braces
            matches = re.findall(r"{(.*?)}", result)

            for match in matches:
                if match not in self.variables:
                    self.error(f"Undefined variable '{match}' in f-string")
                result = result.replace("{" + match + "}", str(self.variables[match]))

            return result
            
        elif token.type == 'IDENTIFIER':
            self.advance()
            if token.value not in self.variables:
                self.error(f"Undefined variable '{token.value}'")
            return self.variables[token.value]
            
        elif token.type == 'LPAREN':
            self.advance()
            value = self.evaluate_expression()
            self.expect('RPAREN')
            return value
            
        elif token.type == 'CALCLPAREN':
            self.advance()
            value = self.evaluate_expression()
            self.expect('RPAREN')
            return value

        elif token.type in ('ADD', 'SUB'):
            op = self.advance()
            value = self.parse_primary()
            return value if op.type == 'ADD' else -value
        elif token.type == "COMMA":
            self.advance()
            return self.parse_primary() 
        elif token.type == "RSET":
            return token.type

        self.error(f"Unexpected token {token.type}")

    def parse_factor(self):
        left = self.parse_primary()
        
        while self.peek().type in ('MUL', 'DIV', 'MOD'):
            op = self.advance()
            right = self.parse_primary()
            
            if op.type == 'MUL':
                left *= right
            elif op.type == 'DIV':
                if right == 0:
                    self.error("Division by zero")
                left /= right
            elif op.type == 'MOD':
                left %= right
                
        return left

    def parse_term(self):
        left = self.parse_factor()
        
        while self.peek().type in ('ADD', 'SUB'):
            op = self.advance()
            right = self.parse_factor()
            
            if op.type == 'ADD':
                left += right
            elif op.type == 'SUB':
                left -= right
                
        return left

    def parse_comparison(self):
        left = self.parse_term()

        # map token types to comparison operators
        comparisons = {
            'EQ': lambda x, y: x == y,
            'NEQ': lambda x, y: x != y,
            'GT': lambda x, y: x > y,
            'LT': lambda x, y: x < y,
            'GTE': lambda x, y: x >= y,
            'LTE': lambda x, y: x <= y,
            'LANGLE': lambda x, y: x < y,  # Added support for < token
            'RANGLE': lambda x, y: x > y   # Added support for > token
        }
        
        if self.peek().type in comparisons:
            op = self.advance()
            right = self.parse_term()
            return comparisons[op.type](left, right)
                
        return left

    def evaluate_expression(self):
        
        if self.peek().type == "LSET":
            return self.evaluate_set()

        return self.parse_comparison()
    
    def evaluate_set(self):
        self.expect("LSET")
        l = []
        while self.peek().type != "RSET":
            l.append(self.evaluate_expression())
            
        self.advance()


        return l       

    def execute_statement(self):
        token = self.peek()
        
        if token.type == 'LET':
            self.advance()
            var_name = self.expect('IDENTIFIER').value
            self.expect('ASSIGN')
            value = self.evaluate_expression()
            self.variables[var_name] = value
            self.expect('SEMICOLON')
            
        elif token.type == 'ECHO':
            self.advance()
            value = self.evaluate_expression()
            print(value)
            self.expect('SEMICOLON')
            
        elif token.type == 'IF':
            self.advance()
            condition = self.evaluate_expression()
            self.expect('LGROUP')
            
            if condition:
                self.execute_block()
                self.expect('RGROUP')
                
                if self.peek().type == 'ELSE':
                    self.advance()
                    self.expect('LGROUP')
                    self.skip_block()
                    self.expect('RGROUP')
            else:
                self.skip_block()
                self.deadvance()
                self.expect('RGROUP')
                
                if self.peek().type == 'ELSE':
                    self.advance()
                    self.expect('LGROUP')
                    self.execute_block()
                    self.expect('RGROUP')
                    
        elif token.type == 'WHILE':
            start_pos = self.pos
            self.advance()
            
            while True:
                self.pos = start_pos + 1  # Reset to start of condition
                condition = self.evaluate_expression()
                if not condition:
                    break
                    
                self.expect('LGROUP')
                self.execute_block()
                self.expect('RGROUP')
            
            # Skip the block if we never entered the loop
            if self.peek().type == 'LGROUP':
                self.expect('LGROUP')
                self.skip_block()
                self.deadvance()
                self.expect('RGROUP')
            
        elif token.type == 'FOR':
            self.advance()
            var_name = self.expect('IDENTIFIER').value
            self.expect('IN')
            if self.peek().type == "RANGE":
                self.advance()
                self.expect("LPAREN")

                start = int(self.evaluate_expression())
                self.expect('COMMA')
                end = int(self.evaluate_expression())
                self.expect('RPAREN')
                self.expect('LGROUP')


                block_start = self.pos
                for i in range(start, end):
                    self.variables[var_name] = i
                    self.pos = block_start
                    self.execute_block()
                    if i < end - 1:
                        self.pos = block_start
                

            elif self.peek().type == "IDENTIFIER":
                value = self.variables[self.advance().value]
                if type(value) != list:
                    self.error(f"expected list at {self.token}")
                    return
                
                self.expect('LGROUP')
                                
                block_start = self.pos
                for i in value:
                    self.variables[var_name] = i
                    self.pos = block_start
                    self.execute_block()

            elif self.peek().type == "LSET":
                value = self.evaluate_set()
                
                self.expect('LGROUP')
                                
                block_start = self.pos
                for i in value:
                    self.variables[var_name] = i
                    self.pos = block_start
                    self.execute_block()
                
            self.expect('RGROUP')
            
        else:
            self.error(f"Unexpected token {token.type}")
            
    def execute_block(self):
        while self.peek().type not in ('RGROUP', 'EOF'):
            self.execute_statement()
            
    def skip_block(self):
        depth = 1
        while depth > 0 and self.peek().type != 'EOF':
            token = self.advance()
            if token.type == 'LGROUP':
                depth += 1
            elif token.type == 'RGROUP':
                depth -= 1
                
    def interpret(self, tokens):
        self.tokens = tokens
        self.pos = 0
        
        while self.peek().type != 'EOF':
            self.execute_statement()
        
        return self.variables

