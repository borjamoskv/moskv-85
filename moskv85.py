# MOSKV-85 SYSTEM KERNEL
# Author: Borja Moskv (borjamoskv)
# Reality Level: C5-REAL
# Version: 1.0.0 (Base-85 Spec)

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
        self.pc = 0
        self.code = ""
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

    def parse_block(self, code_str, start_idx):
        depth = 1
        idx = start_idx + 1
        block_chars = []
        while idx < len(code_str):
            c = code_str[idx]
            if c == "[":
                depth += 1
            elif c == "]":
                depth -= 1
                if depth == 0:
                    return "".join(block_chars), idx
            block_chars.append(c)
            idx += 1
        raise SyntaxError("Unbalanced brackets: '[' has no matching ']'")

    def parse_string(self, code_str, start_idx):
        idx = start_idx + 1
        str_chars = []
        while idx < len(code_str):
            c = code_str[idx]
            if c == "\\":
                return "".join(str_chars), idx
            str_chars.append(c)
            idx += 1
        raise SyntaxError("Unbalanced string literal: '\\' has no matching '\\'")

    def lex_purge(self, raw_code):
        # Anergy Purge Engine (AOT Lexer)
        purged = []
        i = 0
        while i < len(raw_code):
            c = raw_code[i]
            if c == "`":
                while i < len(raw_code) and raw_code[i] != "\n":
                    i += 1
                i += 1
                continue
            if c == "\\":
                purged.append(c)
                i += 1
                while i < len(raw_code):
                    purged.append(raw_code[i])
                    if raw_code[i] == "\\":
                        i += 1
                        break
                    i += 1
                continue
            if c in ALPHABET_SET:
                purged.append(c)
            i += 1
        return "".join(purged)

    def execute_block(self, block_code, pre_purged=False):
        # Save current state
        old_code = self.code
        old_pc = self.pc
        
        self.code = block_code if pre_purged else self.lex_purge(block_code)
        self.pc = 0
        
        while self.pc < len(self.code) and self.running:
            c = self.code[self.pc]
            
            # Core instruction dispatch
            try:
                self.step(c)
            except Exception as e:
                sys.stderr.write(f"\nExecution error at token '{c}' (pos {self.pc}): {str(e)}\n")
                self.running = False
                break
            
            self.pc += 1

        # Restore state
        self.code = old_code
        self.pc = old_pc

    def step(self, inst):
        # 1. Literals and Constants
        if inst in "0123456789":
            self.push(int(inst))
        elif inst == "#":
            # 32-bit literal
            if self.pc + 5 >= len(self.code):
                raise IndexError("Unexpected End Of File reading 32-bit literal")
            lit_chars = self.code[self.pc+1 : self.pc+6]
            val = decode_b85(lit_chars)
            # Apply signed 32-bit conversion
            if val >= 0x80000000:
                val -= 0x100000000
            self.push(val)
            self.pc += 5
        elif inst == "$":
            # 64-bit literal
            if self.pc + 10 >= len(self.code):
                raise IndexError("Unexpected End Of File reading 64-bit literal")
            lit_chars = self.code[self.pc+1 : self.pc+11]
            val = decode_b85(lit_chars)
            # Apply signed 64-bit conversion
            if val >= 0x8000000000000000:
                val -= 0x10000000000000000
            self.push(val)
            self.pc += 10

        # 2. Arithmetic
        elif inst == "+":
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

        # 3. Bitwise
        elif inst == "!":
            self.push(~self.pop())
        elif inst == "\"":
            # DUP2
            if len(self.stack) < 2:
                raise IndexError("Stack underflow on DUP2")
            b = self.stack[-1]
            a = self.stack[-2]
            self.push(a)
            self.push(b)
            self.push(a)
            self.push(b)
        elif inst == "&":
            b = self.pop()
            a = self.pop()
            self.push(a & b)
        elif inst == "'":
            # Bitwise XOR
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
            # Bitwise OR
            b = self.pop()
            a = self.pop()
            self.push(a | b)

        # 4. Comparisons and Logic
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

        # 5. Stack Manipulation
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
            # ROT: [a, b, c] -> [b, c, a]
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

        # 6. Memory Operations
        elif inst == "g":
            # Store
            addr = self.pop()
            val = self.pop()
            self.memory[addr] = val
        elif inst == "h":
            # Load
            addr = self.pop()
            self.push(self.memory.get(addr, 0))

        # 7. Flow Control
        elif inst == "[":
            block_code, new_pc = self.parse_block(self.code, self.pc)
            self.push(block_code)
            self.pc = new_pc
        elif inst == "]":
            raise SyntaxError("Unexpected closing bracket ']'")
        elif inst == "e":
            block = self.pop()
            if isinstance(block, str):
                self.execute_block(block, pre_purged=True)
            else:
                # If it is an integer, execute as instruction of that ASCII
                self.step(chr(block % 256))
        elif inst == "t":
            # Cond
            cond = self.pop()
            block = self.pop()
            if cond != 0:
                if isinstance(block, str):
                    self.execute_block(block, pre_purged=True)
                else:
                    self.step(chr(block % 256))
        elif inst == "j":
            # If-Else
            cond = self.pop()
            false_block = self.pop()
            true_block = self.pop()
            chosen_block = true_block if cond != 0 else false_block
            if isinstance(chosen_block, str):
                self.execute_block(chosen_block, pre_purged=True)
            else:
                self.step(chr(chosen_block % 256))
        elif inst == "f":
            # While loop: cond_block, body_block
            body_block = self.pop()
            cond_block = self.pop()
            if not isinstance(cond_block, str) or not isinstance(body_block, str):
                raise TypeError("While loop requires execution blocks")
            
            while self.running:
                self.execute_block(cond_block, pre_purged=True)
                if not self.running:
                    break
                cond_val = self.pop()
                if cond_val == 0:
                    break
                self.execute_block(body_block, pre_purged=True)

        # 8. Input/Output
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

        # 9. Meta & Diagnostic
        elif inst == "m":
            # Metadata / Version / Creator
            sys.stdout.write("\n========================================\n")
            sys.stdout.write("MOSKV-85 Sovereign Virtual Machine\n")
            sys.stdout.write("Creator: Borja Moskv (borjamoskv)\n")
            sys.stdout.write("Reality level: C5-REAL\n")
            sys.stdout.write("State: Stable Termodinamic Equilibrium\n")
            sys.stdout.write("========================================\n")
            sys.stdout.flush()
        elif inst == "k":
            # Creator magic constant
            self.push(858585)
        elif inst == "u":
            # Halt
            self.running = False

        # 10. String literal parser
        elif inst == "\\":
            str_val, new_pc = self.parse_string(self.code, self.pc)
            self.push(str_val)
            self.pc = new_pc

        # 11. Custom math / system helpers (A-Z)
        elif inst == "A":
            self.push(abs(self.pop()))
        elif inst == "B":
            val = self.pop()
            self.push(val.bit_length() if hasattr(val, "bit_length") else 0)
        elif inst == "C":
            # Convert to string representation
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
            # DUP3
            if len(self.stack) < 3:
                raise IndexError("Stack underflow on DUP3")
            c = self.stack[-1]
            b = self.stack[-2]
            a = self.stack[-3]
            self.push(a)
            self.push(b)
            self.push(c)
        elif inst == ";":
            # POP2
            self.pop()
            self.pop()
        elif inst == "@":
            # ROT_LEFT: [a, b, c] -> [b, c, a]
            if len(self.stack) < 3:
                raise IndexError("Stack underflow on ROT_LEFT")
            c = self.pop()
            b = self.pop()
            a = self.pop()
            self.push(b)
            self.push(c)
            self.push(a)
        elif inst == "?":
            # System state dump
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
