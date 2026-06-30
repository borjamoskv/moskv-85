# MOSKV-85 CAUSAL MAPPING

## 1. OPCODE MAPPING (Base-85 Alphabet)
The sovereign alphabet ranges from ASCII 33 (`!`) to 117 (`u`). Total 85 characters.

### 1.1 Numerics (Literals & Resolvers)
* `0` - `9`: Push literal integer 0-9.
* `#`: 32-bit Integer Resolver (Consumes next 5 Base-85 characters).
* `$`: 64-bit Integer Resolver (Consumes next 10 Base-85 characters).

### 1.2 Arithmetic
* `+`: Add
* `-`: Subtract
* `*`: Multiply
* `/`: Divide
* `%`: Modulo
* `^`: Power (Exponent)
* `A`: Absolute Value
* `D`: Double (x * 2)
* `E`: Power of 2 (2^x)
* `I`: Increment (+1)
* `J`: Decrement (-1)
* `Q`: Square Root (Integer)

### 1.3 Bitwise Logic
* `!`: Bitwise NOT
* `&`: Bitwise AND
* `_`: Bitwise OR
* `'`: Bitwise XOR
* `<`: Bitwise Left Shift
* `>``: Bitwise Right Shift
* `B`: Bit_length (pop x -> pushes length of bits)

### 1.4 Constants & Helpers
* `(`: Push -1
* `)`: Push 255
* `F`: Push 0
* `H`: Push 100
* `K`: Push 1000
* `O`: Push 1
* `P`: Push 314159 (Pi approximation)
* `T`: Push 2
* `V`: Push 85 (Base length)
* `k`: Push Creator Magic Constant (858585)

### 1.5 Stack Manipulation
* `d`: DUP (Duplicate top item)
* `"`: DUP2 (Duplicate top two items)
* `:`: DUP3 (Duplicate top three items)
* `s`: SWAP (Swap top two items)
* `p`: POP (Discard top item)
* `;`: POP2 (Discard top two items)
* `o`: OVER (Copy second item to top)
* `r`: ROT (Rotate top three items: a b c -> b c a)
* `@`: ROT_LEFT (Rotate left: a b c -> c a b)
* `c`: CLEAR (Empty the stack)
* `l` / `U`: LEN (Push current stack size)

### 1.6 Flow Control
* `e`: EVAL (Pop block -> Execute AST)
* `t`: IF (Pop block, Pop condition -> if cond!=0 Execute AST)
* `j`: IF-ELSE (Pop true_block, Pop false_block, Pop condition)
* `f`: WHILE (Pop body_block, Pop cond_block)

### 1.7 Memory I/O
* `g`: STORE (Pop val, Pop addr -> memory[addr] = val)
* `h`: LOAD (Pop addr -> push memory[addr])

### 1.8 Disk I/O & Modularity
* `W`: WRITE (Pop filepath, Pop string_data -> write to disk)
* `Z`: READ (Pop filepath -> push file content as string)
* `X`: IMPORT (Pop filepath -> compile AOT & execute in place)

### 1.9 System & I/O
* `.`: Print top of stack as raw value.
* `,`: Print top of stack as ASCII character.
* `i`: Read character from stdin.
* `n`: Read numeric sequence from stdin.
* `m`: Print System Metadata (Reality Level C5).
* `?`: Debug Dump (Stack & Memory).
* `u`: Halt / Exit.

---

## 2. MEMORY MAPPING (Hardware Spec)
The `g` and `h` opcodes interact with a sovereign unbounded dictionary memory. 
To guarantee C5-REAL interaction with external states, future kernels will restrict specific memory addresses for MMIO (Memory-Mapped I/O).

### 2.1 Proposed Virtual Address Space
* `0x0000` - `0x00FF`: Kernel Reserved / Trap Handlers.
* `0x0100` - `0x7FFF`: General Purpose RAM.
* `0x8000` - `0x800F`: Hardware RNG (Random Number Generators).
* `0x8010` - `0x801F`: High-Resolution Timers (System Clock).
* `0x8020` - `0x802F`: UART / Socket Buffer Pointers.
* `0x8030` - `0x803F`: Graphics Framebuffer Base Pointer.

*(Note: Currently `R` opcode provides hardware random. Full MMIO architecture requires pointer injection into `execute_ast`).*
