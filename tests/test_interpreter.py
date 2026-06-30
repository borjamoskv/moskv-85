# MOSKV-85 Test Suite
# Author: Borja Moskv
# Reality Level: C5-REAL

import unittest
from moskv85 import Moskv85Interpreter, decode_b85

class TestMoskv85(unittest.TestCase):
    def setUp(self):
        self.vm = Moskv85Interpreter()

    def test_decode_b85(self):
        # Decode "!!!!+" which is 10
        self.assertEqual(decode_b85("!!!!+"), 10)
        # Decode "!!!"!" which is 85
        self.assertEqual(decode_b85("!!!\"!"), 85)

    def test_push_pop(self):
        self.vm.execute_block("5")
        self.assertEqual(self.vm.pop(), 5)
        self.assertEqual(self.vm.pop(), 0) # Default for empty stack

    def test_arithmetic(self):
        self.vm.execute_block("5 3 +")
        self.assertEqual(self.vm.pop(), 8)

        self.vm.execute_block("9 4 -")
        self.assertEqual(self.vm.pop(), 5)

        self.vm.execute_block("3 4 *")
        self.assertEqual(self.vm.pop(), 12)

        self.vm.execute_block("9 3 /")
        self.assertEqual(self.vm.pop(), 3)

        self.vm.execute_block("8 3 %")
        self.assertEqual(self.vm.pop(), 2)

        self.vm.execute_block("2 3 ^")
        self.assertEqual(self.vm.pop(), 8)

    def test_bitwise(self):
        self.vm.execute_block("5 !")
        self.assertEqual(self.vm.pop(), ~5)

        self.vm.execute_block("5 3 &")
        self.assertEqual(self.vm.pop(), 5 & 3)

        self.vm.execute_block("5 3 _") # Bitwise OR
        self.assertEqual(self.vm.pop(), 5 | 3)

        self.vm.execute_block("5 3 '") # Bitwise XOR
        self.assertEqual(self.vm.pop(), 5 ^ 3)

        self.vm.execute_block("1 3 <") # Left shift
        self.assertEqual(self.vm.pop(), 8)

        self.vm.execute_block("8 2 >") # Right shift
        self.assertEqual(self.vm.pop(), 2)

    def test_stack_manipulation(self):
        self.vm.execute_block("5 d")
        self.assertEqual(self.vm.stack, [5, 5])

        self.vm.execute_block("c 1 2 s")
        self.assertEqual(self.vm.stack, [2, 1])

        self.vm.execute_block("c 1 2 3 r") # ROT: [1, 2, 3] -> [2, 3, 1]
        self.assertEqual(self.vm.stack, [2, 3, 1])

        self.vm.execute_block("c 1 2 o") # OVER: [1, 2] -> [1, 2, 1]
        self.assertEqual(self.vm.stack, [1, 2, 1])

        self.vm.execute_block("c 1 2 3 :") # DUP3: [1, 2, 3] -> [1, 2, 3, 1, 2, 3]
        self.assertEqual(self.vm.stack, [1, 2, 3, 1, 2, 3])

        self.vm.execute_block("c 1 2 ;") # POP2: [1, 2] -> []
        self.assertEqual(self.vm.stack, [])

    def test_comparisons(self):
        self.vm.execute_block("5 5 =")
        self.assertEqual(self.vm.pop(), 1)

        self.vm.execute_block("5 3 =")
        self.assertEqual(self.vm.pop(), 0)

        self.vm.execute_block("3 5 a") # Less than
        self.assertEqual(self.vm.pop(), 1)

        self.vm.execute_block("5 3 b") # Greater than
        self.assertEqual(self.vm.pop(), 1)

        self.vm.execute_block("5 3 q") # Not equal
        self.assertEqual(self.vm.pop(), 1)

    def test_memory(self):
        self.vm.execute_block("H J 0 g 0 h")
        self.assertEqual(self.vm.pop(), 99)

    def test_custom_helpers(self):
        self.vm.execute_block("k") # Creator magic constant
        self.assertEqual(self.vm.pop(), 858585)

        self.vm.execute_block("V") # Version
        self.assertEqual(self.vm.pop(), 85)

        self.vm.execute_block("H") # 100
        self.assertEqual(self.vm.pop(), 100)

        self.vm.execute_block("K") # 1000
        self.assertEqual(self.vm.pop(), 1000)

        self.vm.execute_block("T") # 2
        self.assertEqual(self.vm.pop(), 2)

    def test_flow_control(self):
        # Conditional simple: cond=1, execute block [ 5 ]
        self.vm.execute_block("[5] 1 t")
        self.assertEqual(self.vm.pop(), 5)

        # Conditional simple: cond=0, execute block [ 5 ]
        self.vm.execute_block("[5] 0 t")
        self.assertEqual(self.vm.pop(), 0) # empty

        # Conditional If-Else: cond=1, false_block=[2], true_block=[3]
        self.vm.execute_block("[3] [2] 1 j")
        self.assertEqual(self.vm.pop(), 3)

        # Conditional If-Else: cond=0, false_block=[2], true_block=[3]
        self.vm.execute_block("[3] [2] 0 j")
        self.assertEqual(self.vm.pop(), 2)

    def test_string_literal(self):
        self.vm.execute_block("\\Hello\\")
        self.assertEqual(self.vm.pop(), "Hello")

    def test_file_io(self):
        import os
        # 1. Write file
        filepath = "/tmp/moskv85_test.m85"
        self.vm.execute_block(f"\\{filepath}\\ \\3 4 *\\ W")
        self.assertTrue(os.path.exists(filepath))
        # 2. Read file
        self.vm.execute_block(f"\\{filepath}\\ Z")
        self.assertEqual(self.vm.pop(), "3 4 *")
        # 3. Import/Execute file
        self.vm.execute_block(f"\\{filepath}\\ X")
        self.assertEqual(self.vm.pop(), 12)
        # Cleanup
        os.remove(filepath)

if __name__ == "__main__":
    unittest.main()
