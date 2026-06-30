# MOSKV-85 SYSTEM KERNEL
# Author: Borja Moskv (borjamoskv)
# Reality Level: C5-REAL
# Version: 2.0.0 (Ouroboros AST Compiler)

import sys
import random
import argparse

ALPHABET = "!\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstu"
ALPHABET_SET = set(ALPHABET)

def decode_b85(chars):
    val = 0
    for c in chars:
        if c not in ALPHABET_SET:
            raise ValueError(f"Character {c} is not in the MOSKV-85 alphabet.")
        val = val * 85 + (ord(c) - 33)
    return val

class Moskv85Interpreter:
    def __init__(self):
        self.stack = []
        self.memory = {}
        self.running = True

    def push(self, val):
        self.stack.append(val)

    def pop(self):
        if not self.stack:
            return 0
        return self.stack.pop()

    def peek(self):
        if not self.stack:
            return 0
        return self.stack[-1]

    def compile_aot(self, raw_code):
        """
        Transmutes raw MOSKV-85 strings into a dense C5-REAL AST (lists of opcodes, integers, and sub-blocks).
        """
        ast = []
        i = 0
        n = len(raw_code)
        while i < n:
            c = raw_code[i]
            
            # Comments
            if c == "`":
                while i < n and raw_code[i] != "\n":
                    i += 1
                i += 1
                continue
                
            # String literals
            if c == "\\":
                i += 1
                str_chars = []
                while i < n and raw_code[i] != "\\":
                    str_chars.append(raw_code[i])
                    i += 1
                ast.append("".join(str_chars))
                i += 1
                continue
                
            if c not in ALPHABET_SET:
                i += 1
                continue
                
            # Block parsing -> recursive AOT
            if c == "[":
                depth = 1
                start_idx = i + 1
                idx = start_idx
                while idx < n:
                    if raw_code[idx] == "[": depth += 1
                    elif raw_code[idx] == "]":
                        depth -= 1
                        if depth == 0: break
                    idx += 1
                if depth != 0: raise SyntaxError("Unbalanced brackets '['")
                sub_ast = self.compile_aot(raw_code[start_idx:idx])
                ast.append(sub_ast)
                i = idx + 1
                continue
                
            # 32-bit literal
            if c == "#":
                lit_chars = raw_code[i+1 : i+6]
                val = decode_b85(lit_chars)
                if val >= 0x80000000: val -= 0x100000000
                ast.append(val)
                i += 6
                continue
                
            # 64-bit literal
            if c == "$":
                lit_chars = raw_code[i+1 : i+11]
                val = decode_b85(lit_chars)
                if val >= 0x8000000000000000: val -= 0x10000000000000000
                ast.append(val)
                i += 11
                continue
                
            # Direct digits 0-9
            if c in "0123456789":
                ast.append(int(c))
                i += 1
                continue
                
            # Normal opcode
            ast.append(c)
            i += 1
            
        return ast

    def execute_block(self, source_code):
        # Legacy entrypoint: compile then execute
        ast = self.compile_aot(source_code)
        self.execute_ast(ast)

    def execute_ast(self, ast):
        for node in ast:
            if not self.running:
                break
            
            # Direct Push Dispatch
            if isinstance(node, int):
                self.push(node)
            elif isinstance(node, list):
                self.push(node)
            elif isinstance(node, str) and len(node) > 1:
                self.push(node)
            else:
                # Opcode execution
                try:
                    self.step(node)
                except Exception as e:
                    sys.stderr.write(f"\nExecution error at opcode '{node}': {str(e)}\n")
                    self.running = False
                    break

    def step(self, inst):
        # Arithmetic
        if inst == "+":
            b = self.pop()
            a = self.pop()
            self.push(a + b)
        elif inst == "-":
            b = self.pop()
            a = self.pop()
            self.push(a - b)
        elif inst == "*":
            b = self.pop()
            a = self.pop()
            self.push(a * b)
        elif inst == "/":
            b = self.pop()
            a = self.pop()
            self.push(a // b if b != 0 else 0)
        elif inst == "%":
            b = self.pop()
            a = self.pop()
            self.push(a % b if b != 0 else 0)
        elif inst == "^":
            b = self.pop()
            a = self.pop()
            self.push(a ** b)

        # Bitwise
        elif inst == "!":
            self.push(~self.pop())
        elif inst == "\"":
            if len(self.stack) < 2:
                raise IndexError("Stack underflow on DUP2")
            b = self.stack[-1]
            a = self.stack[-2]
            self.push(a)
            self.push(b)
        elif inst == "&":
            b = self.pop()
            a = self.pop()
            self.push(a & b)
        elif inst == "'":
            b = self.pop()
            a = self.pop()
            self.push(a ^ b)
        elif inst == "(":
            self.push(-1)
        elif inst == ")":
            self.push(255)
        elif inst == "<":
            b = self.pop()
            a = self.pop()
            self.push(a << b)
        elif inst == ">":
            b = self.pop()
            a = self.pop()
            self.push(a >> b)
        elif inst == "_":
            b = self.pop()
            a = self.pop()
            self.push(a | b)

        # Comparisons and Logic
        elif inst == "=":
            b = self.pop()
            a = self.pop()
            self.push(1 if a == b else 0)
        elif inst == "a":
            b = self.pop()
            a = self.pop()
            self.push(1 if a < b else 0)
        elif inst == "b":
            b = self.pop()
            a = self.pop()
            self.push(1 if a > b else 0)
        elif inst == "q":
            b = self.pop()
            a = self.pop()
            self.push(1 if a != b else 0)

        # Stack Manipulation
        elif inst == "d":
            self.push(self.peek())
        elif inst == "s":
            if len(self.stack) < 2:
                raise IndexError("Stack underflow on SWAP")
            self.stack[-1], self.stack[-2] = self.stack[-2], self.stack[-1]
        elif inst == "p":
            self.pop()
        elif inst == "o":
            if len(self.stack) < 2:
                raise IndexError("Stack underflow on OVER")
            self.push(self.stack[-2])
        elif inst == "r":
            if len(self.stack) < 3:
                raise IndexError("Stack underflow on ROT")
            c = self.pop()
            b = self.pop()
            a = self.pop()
            self.push(b)
            self.push(c)
            self.push(a)
        elif inst == "c":
            self.stack.clear()
        elif inst == "l":
            self.push(len(self.stack))

        # Memory Operations
        elif inst == "g":
            addr = self.pop()
            val = self.pop()
            self.memory[addr] = val
        elif inst == "h":
            addr = self.pop()
            self.push(self.memory.get(addr, 0))

        # Flow Control
        elif inst == "e":
            block = self.pop()
            if isinstance(block, list):
                self.execute_ast(block)
            elif isinstance(block, str):
                self.execute_ast(self.compile_aot(block))
            else:
                self.step(chr(block % 256))
        elif inst == "t":
            cond = self.pop()
            block = self.pop()
            if cond != 0:
                if isinstance(block, list):
                    self.execute_ast(block)
                elif isinstance(block, str):
                    self.execute_ast(self.compile_aot(block))
                else:
                    self.step(chr(block % 256))
        elif inst == "j":
            cond = self.pop()
            false_block = self.pop()
            true_block = self.pop()
            chosen_block = true_block if cond != 0 else false_block
            if isinstance(chosen_block, list):
                self.execute_ast(chosen_block)
            elif isinstance(chosen_block, str):
                self.execute_ast(self.compile_aot(chosen_block))
            else:
                self.step(chr(chosen_block % 256))
        elif inst == "f":
            body_block = self.pop()
            cond_block = self.pop()
            if not isinstance(cond_block, list) or not isinstance(body_block, list):
                raise TypeError("While loop requires AST execution blocks")
            
            while self.running:
                self.execute_ast(cond_block)
                if not self.running:
                    break
                cond_val = self.pop()
                if cond_val == 0:
                    break
                self.execute_ast(body_block)

        # Input/Output
        elif inst == ".":
            sys.stdout.write(str(self.pop()))
            sys.stdout.flush()
        elif inst == ",":
            val = self.pop()
            if isinstance(val, str):
                sys.stdout.write(val)
            else:
                sys.stdout.write(chr(val % 256))
            sys.stdout.flush()
        elif inst == "i":
            c = sys.stdin.read(1)
            self.push(ord(c) if c else 0)
        elif inst == "n":
            val = ""
            while True:
                c = sys.stdin.read(1)
                if not c:
                    break
                if c.isspace():
                    if val:
                        break
                    continue
                val += c
            try:
                self.push(int(val))
            except ValueError:
                self.push(0)

        # Meta & Diagnostic
        elif inst == "m":
            sys.stdout.write("\n========================================\n")
            sys.stdout.write("MOSKV-85 Sovereign Virtual Machine\n")
            sys.stdout.write("Creator: Borja Moskv (borjamoskv)\n")
            sys.stdout.write("Reality level: C5-REAL\n")
            sys.stdout.write("State: Ouroboros AST Execution Matrix\n")
            sys.stdout.write("========================================\n")
            sys.stdout.flush()
        elif inst == "k":
            self.push(858585)
        elif inst == "u":
            self.running = False

        # Custom math / system helpers (A-Z)
        elif inst == "A":
            self.push(abs(self.pop()))
        elif inst == "B":
            val = self.pop()
            self.push(val.bit_length() if hasattr(val, "bit_length") else 0)
        elif inst == "C":
            self.push(str(self.pop()))
        elif inst == "D":
            self.push(self.pop() * 2)
        elif inst == "E":
            self.push(2 ** self.pop())
        elif inst == "F":
            self.push(0)
        elif inst == "G":
            b = self.pop()
            a = self.pop()
            self.push(1 if a >= b else 0)
        elif inst == "H":
            self.push(100)
        elif inst == "I":
            self.push(self.pop() + 1)
        elif inst == "J":
            self.push(self.pop() - 1)
        elif inst == "K":
            self.push(1000)
        elif inst == "L":
            b = self.pop()
            a = self.pop()
            self.push(1 if a <= b else 0)
        elif inst == "M":
            b = self.pop()
            a = self.pop()
            self.push(max(a, b))
        elif inst == "N":
            b = self.pop()
            a = self.pop()
            self.push(min(a, b))
        elif inst == "O":
            self.push(1)
        elif inst == "P":
            self.push(314159)
        elif inst == "Q":
            self.push(int(self.pop() ** 0.5))
        elif inst == "R":
            limit = self.pop()
            self.push(random.randint(0, max(0, limit - 1)) if limit > 0 else 0)
        elif inst == "S":
            val = self.pop()
            self.push(-1 if val < 0 else (1 if val > 0 else 0))
        elif inst == "T":
            self.push(2)
        elif inst == "U":
            self.push(len(self.stack))
        elif inst == "V":
            self.push(85)
        elif inst == "Y":
            pass # NOP
        elif inst == ":":
            if len(self.stack) < 3:
                raise IndexError("Stack underflow on DUP3")
            c = self.stack[-1]
            b = self.stack[-2]
            a = self.stack[-3]
            self.push(a)
            self.push(b)
            self.push(c)
        elif inst == ";":
            self.pop()
            self.pop()
        elif inst == "@":
            if len(self.stack) < 3:
                raise IndexError("Stack underflow on ROT_LEFT")
            c = self.pop()
            b = self.pop()
            a = self.pop()
            self.push(b)
            self.push(c)
            self.push(a)
        elif inst == "?":
            sys.stderr.write(f"\n[DEBUG] Stack: {self.stack} | Memory: {self.memory}\n")
            sys.stderr.flush()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MOSKV-85 Interpreter - Sovereign Base-85 Kernel")
    parser.add_argument("file", help="Path to the MOSKV-85 source file")
    parser.add_argument("-d", "--debug", action="store_true", help="Print debug dump at halt")
    args = parser.parse_args()

    try:
        with open(args.file, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception as e:
        sys.stderr.write(f"Failed to read file {args.file}: {str(e)}\n")
        sys.exit(1)

    interpreter = Moskv85Interpreter()
    interpreter.execute_block(source)

    if args.debug:
        sys.stderr.write(f"\n[FINAL DEBUG] Stack: {interpreter.stack}\n")
        sys.stderr.write(f"[FINAL DEBUG] Memory: {interpreter.memory}\n")
