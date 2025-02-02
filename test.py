import sys
import os
import traceback
import time
import subprocess

# Import everything from interpreter and lexer
from interpreter import *
from lexer import *

# Terminal color codes
RESET = "\033[0m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"

# Path to store the last used test number
TEST_FILE = "last_test.txt"
TESTS_FOLDER = "tests"

def save_test_number(number):
    """Save the test number to a file."""
    with open(TEST_FILE, "w") as f:
        f.write(str(number))

def load_test_number():
    """Load the last saved test number."""
    if os.path.exists(TEST_FILE):
        with open(TEST_FILE, "r") as f:
            return f.read().strip()
    return None

def find_test_folder(test_number):
    """Find a test folder matching the given test number."""
    test_folders = [f for f in os.listdir(TESTS_FOLDER) if f.startswith(f"test{test_number}_") and os.path.isdir(os.path.join(TESTS_FOLDER, f))]
    
    if not test_folders:
        return None  # No matching test folder found
    
    return os.path.join(TESTS_FOLDER, test_folders[0])  # Return the first match

def run_test(test_number):
    """Run the test script and compare output with expected result."""
    test_folder = find_test_folder(test_number)

    if not test_folder:
        print(f"{RED}❌ No test folder found for number {test_number} in '{TESTS_FOLDER}/'.{RESET}")
        return

    code_file = os.path.join(test_folder, "code.at")
    result_file = os.path.join(test_folder, "result.txt")

    if not os.path.exists(code_file):
        print(f"{RED}⚠️ Missing 'code.at' file in {test_folder}.{RESET}")
        return

    if not os.path.exists(result_file):
        print(f"{RED}⚠️ Missing 'result.txt' file in {test_folder}.{RESET}")
        return

    try:
        print(f"{CYAN}\n🔍 Running Test: {test_folder} ...{RESET}")
        start_time = time.time()
        
        # Read the code to execute
        with open(code_file, "r") as f:
            code = f.read().strip()

        # Execute the code using Python subprocess
        process = subprocess.run(["python", "-c", code], capture_output=True, text=True)
        output = process.stdout.strip()

        # Read the expected result
        with open(result_file, "r") as f:
            expected_output = f.read().strip()

        end_time = time.time()
        elapsed_time = end_time - start_time

        print(f"\n{YELLOW}Expected Output:{RESET}")
        print(f"{GREEN}{expected_output}{RESET}")

        print(f"\n{YELLOW}Actual Output:{RESET}")
        print(f"{GREEN if output == expected_output else RED}{output}{RESET}")

        if output == expected_output:
            print(f"\n{GREEN}✅ Test passed in {elapsed_time:.3f} seconds.{RESET}")
        else:
            print(f"\n{RED}❌ Test failed in {elapsed_time:.3f} seconds.{RESET}")

    except Exception as e:
        print(f"\n{RED}❌ ERROR: Test execution failed!{RESET}")
        print(traceback.format_exc())

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Save test number if provided
        save_test_number(sys.argv[1])
        print(f"\n{GREEN}✅ Test {sys.argv[1]} set as default.{RESET}")
    else:
        # Load and run last saved test
        last_test = load_test_number()
        if last_test:
            run_test(last_test)
        else:
            print(f"\n{YELLOW}⚠️ No test number set. Use `py test.py <number>` first.{RESET}")
