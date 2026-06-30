# MOSKV-85 SOVEREIGN REPL
# Author: Borja Moskv (borjamoskv)
# Reality Level: C5-REAL
# Version: 1.0.0

import sys
from moskv85 import Moskv85Interpreter, ALPHABET_SET

# Attempt to load readline for better command line editing experience
try:
    import readline
except ImportError:
    pass

def print_help():
    sys.stdout.write("\n=== MOSKV-85 REPL COMMANDS ===\n")
    sys.stdout.write("Type code to execute it on the Virtual Machine.\n")
    sys.stdout.write("Special CLI Commands:\n")
    sys.stdout.write("  .help    Show this command guide\n")
    sys.stdout.write("  .stack   Dump current stack explicitly\n")
    sys.stdout.write("  .memory  Dump current memory registers\n")
    sys.stdout.write("  .clear   Reset stack and memory\n")
    sys.stdout.write("  .exit    Halt and close REPL\n")
    sys.stdout.write("==============================\n\n")
    sys.stdout.flush()

def main():
    interpreter = Moskv85Interpreter()
    
    sys.stdout.write("==================================================\n")
    sys.stdout.write("  MOSKV-85 SOVEREIGN INTERACTIVE REPL\n")
    sys.stdout.write("  Creator: Borja Moskv (borjamoskv)\n")
    sys.stdout.write("  Reality level: C5-REAL\n")
    sys.stdout.write("  Type \".help\" for commands. Ctrl+D or \".exit\" to quit.\n")
    sys.stdout.write("==================================================\n\n")
    sys.stdout.flush()

    while interpreter.running:
        try:
            # Read
            prompt = "m85> "
            try:
                line = input(prompt)
            except EOFError:
                sys.stdout.write("\nExiting.\n")
                break
                
            stripped = line.strip()
            if not stripped:
                continue

            # Command Routing
            if stripped == ".exit" or stripped == ".quit":
                break
            elif stripped == ".help":
                print_help()
                continue
            elif stripped == ".stack":
                sys.stdout.write(f"Stack: {interpreter.stack}\n")
                sys.stdout.flush()
                continue
            elif stripped == ".memory":
                sys.stdout.write(f"Memory: {interpreter.memory}\n")
                sys.stdout.flush()
                continue
            elif stripped == ".clear":
                interpreter.stack.clear()
                interpreter.memory.clear()
                sys.stdout.write("State cleared.\n")
                sys.stdout.flush()
                continue

            # Execute
            interpreter.execute_block(line)
            
            # Print state summary
            sys.stdout.write(f" -> Stack: {interpreter.stack}\n")
            sys.stdout.flush()

        except KeyboardInterrupt:
            sys.stdout.write("\nKeyboardInterrupt. Type \".exit\" to exit.\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stderr.write(f"REPL Error: {str(e)}\n")
            sys.stderr.flush()

if __name__ == "__main__":
    main()
