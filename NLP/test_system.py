#!/usr/bin/env python3

# ============================================================================
# PROGRAM: test_system.py
# PURPOSE: Automated test script to verify the NLP-to-SQL system works
# ============================================================================

import socket
import time
import subprocess
import sys
import os
import signal


# ============================================================================
# CLASS: SystemTester
# PURPOSE: Tests the complete NLP-to-SQL system automatically
# ============================================================================
class SystemTester:
    """
    This class provides automated testing for the NLP-to-SQL system.
    
    It tests:
    - C++ server startup
    - Python client connection
    - SQL query execution
    - Response handling
    """

    def __init__(self):
        """Initialize the test environment."""
        self.server_process = None
        self.client_socket = None
        self.server_port = 8080
        self.server_host = "localhost"

    def start_server(self):
        """
        Start the C++ database server as a background process.
        
        Returns:
            bool: True if server started successfully
        """
        print("=" * 60)
        print("   Starting System Test")
        print("=" * 60)
        print()
        print("Step 1: Compiling C++ server...")

        # Check if server is already compiled
        if not os.path.exists("database_server"):
            # Compile the C++ server
            compile_result = subprocess.run(
                ["g++", "-o", "database_server", "database_server.cpp"],
                capture_output=True,
                text=True
            )

            if compile_result.returncode != 0:
                print("[Error] Compilation failed:")
                print(compile_result.stderr)
                return False

            print("[OK] Compilation successful!")
        else:
            print("[OK] Server already compiled.")

        print()
        print("Step 2: Starting C++ server...")

        try:
            # Start the server as a background process
            self.server_process = subprocess.Popen(
                ["./db_server"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait for server to start
            time.sleep(2)

            # Check if server is running
            if self.server_process.poll() is not None:
                print("[Error] Server failed to start:")
                stdout, stderr = self.server_process.communicate()
                print(f"STDOUT: {stdout}")
                print(f"STDERR: {stderr}")
                return False

            print("[OK] Server started successfully!")
            return True

        except Exception as e:
            print(f"[Error] Failed to start server: {e}")
            return False

    def connect_to_server(self):
        """
        Connect a test client to the server.
        
        Returns:
            bool: True if connection successful
        """
        print()
        print("Step 3: Connecting to server...")

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(5)
            self.client_socket.connect((self.server_host, self.server_port))
            
            print("[OK] Connected to server!")
            return True

        except socket.error as e:
            print(f"[Error] Connection failed: {e}")
            return False

    def send_and_receive(self, message):
        """
        Send a message to the server and get the response.
        
        Parameters:
            message (str): The message to send
            
        Returns:
            str: The server response
        """
        try:
            # Send message
            self.client_socket.sendall((message + "\n").encode('utf-8'))
            print(f"Sent: {message}")

            # Receive response
            response = ""
            while True:
                chunk = self.client_socket.recv(4096)
                if not chunk:
                    break
                response += chunk.decode('utf-8')
                if response.strip().endswith('\n'):
                    break

            return response

        except socket.error as e:
            return f"[Error] {e}"

    def run_tests(self):
        """
        Run a series of automated tests.
        
        Returns:
            bool: True if all tests passed
        """
        print()
        print("Step 4: Running automated tests...")
        print("-" * 60)

        test_cases = [
            {
                "name": "Select All Employees",
                "query": "SELECT * FROM employees",
                "expected_contains": ["Alice", "Bob", "Carol"]
            },
            {
                "name": "Select All Departments",
                "query": "SELECT * FROM departments",
                "expected_contains": ["Computer Science", "Electrical Engineering"]
            },
            {
                "name": "Select with Where Clause (Equals)",
                "query": "SELECT * FROM employees WHERE deptID = d10",
                "expected_contains": ["Alice", "Carol"]
            },
            {
                "name": "Select with Where Clause (Greater Than)",
                "query": "SELECT * FROM employees WHERE age > 35",
                "expected_contains": ["Carol", "Frank", "Jack"]
            },
            {
                "name": "Select with Where Clause (Less Than)",
                "query": "SELECT * FROM employees WHERE age < 30",
                "expected_contains": ["Alice", "David", "Grace"]
            }
        ]

        passed_tests = 0
        total_tests = len(test_cases)

        for test in test_cases:
            print()
            print(f"Test: {test['name']}")
            print(f"Query: {test['query']}")

            response = self.send_and_receive(test['query'])

            # Check if response contains expected data
            all_found = True
            for expected in test['expected_contains']:
                if expected not in response:
                    all_found = False
                    print(f"[Warning] Expected '{expected}' not found in response")

            if all_found:
                print("[PASS] Test passed!")
                passed_tests += 1
            else:
                print("[FAIL] Test failed!")
                print(f"Response: {response[:200]}...")

        print()
        print("-" * 60)
        print(f"Test Results: {passed_tests}/{total_tests} tests passed")
        print("-" * 60)

        return passed_tests == total_tests

    def cleanup(self):
        """
        Clean up test resources.
        """
        print()
        print("Step 5: Cleaning up...")

        # Close client socket
        if self.client_socket:
            self.client_socket.close()
            print("[OK] Client socket closed")

        # Stop server process
        if self.server_process:
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            print("[OK] Server process terminated")

        print()
        print("Test completed!")


# ============================================================================
# CLASS: ManualTester
# PURPOSE: Interactive testing mode for manual exploration
# ============================================================================
class ManualTester:
    """
    Interactive testing mode where users can manually test queries.
    """

    def __init__(self):
        """Initialize the manual tester."""
        self.socket = None
        self.server_host = "localhost"
        self.server_port = 8080

    def connect(self):
        """Connect to the server."""
        print("Connecting to server...")

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((self.server_host, self.server_port))
            print("[OK] Connected!")
            return True

        except socket.error as e:
            print(f"[Error] Connection failed: {e}")
            return False

    def send_query(self, query):
        """Send a query and return the response."""
        try:
            self.socket.sendall((query + "\n").encode('utf-8'))

            response = ""
            while True:
                chunk = self.socket.recv(4096)
                if not chunk:
                    break
                response += chunk.decode('utf-8')
                if response.strip().endswith('\n'):
                    break

            return response

        except socket.error as e:
            return f"[Error] {e}"

    def run(self):
        """Run the interactive testing loop."""
        print()
        print("Interactive Mode - Manual Testing")
        print("-" * 40)
        print("Type 'quit' to exit")
        print("Available tables: employees, departments")
        print()

        while True:
            try:
                query = input("SQL Query: ").strip()

                if query.lower() in ['quit', 'exit']:
                    print("Goodbye!")
                    break

                if not query:
                    continue

                print()
                response = self.send_query(query)

                print("Response:")
                print("=" * 40)
                print(response)
                print("=" * 40)
                print()

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break


# ============================================================================
# MAIN FUNCTION
# ============================================================================
def main():
    """
    Main entry point for the test script.
    """
    print()
    print("=" * 60)
    print("   NLP-to-SQL System Test Suite")
    print("=" * 60)
    print()

    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("Usage: python test_system.py [mode]")
            print()
            print("Modes:")
            print("  auto    Run automated tests (default)")
            print("  manual  Interactive manual testing")
            print("  help    Show this help message")
            print()
            sys.exit(0)

        mode = sys.argv[1].lower()
    else:
        mode = "auto"

    # Create tester
    tester = SystemTester()

    # Run automated tests
    if mode == "auto":
        # Start server
        if not tester.start_server():
            sys.exit(1)

        # Connect to server
        if not tester.connect_to_server():
            tester.cleanup()
            sys.exit(1)

        # Run tests
        success = tester.run_tests()

        # Cleanup
        tester.cleanup()

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    # Run manual tests
    elif mode == "manual":
        tester = ManualTester()

        if tester.connect():
            tester.run()
        else:
            print("Make sure the C++ server is running first!")
            sys.exit(1)

    else:
        print(f"[Error] Unknown mode: {mode}")
        print("Use: python test_system.py help")
        sys.exit(1)


# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    main()
