import unittest
import os
import flet as ft # Required for app.py but not directly for these helper functions
import time # Required for app.py but not directly for these helper functions

# These are simplified versions of the functions that will be in unsubscriber.py
# We're simulating their behavior for testing the file operations.

ALLOW_LIST_TEST_FILE = "allow_list_test.txt"

def read_allow_list():
    if not os.path.exists(ALLOW_LIST_TEST_FILE):
        return []
    with open(ALLOW_LIST_TEST_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]

def write_allow_list(entries):
    with open(ALLOW_LIST_TEST_FILE, "w") as f:
        for entry in sorted(set(entries)): # Ensure unique and sorted
            f.write(entry + "\n")

class TestAllowListFileOperations(unittest.TestCase):

    def setUp(self):
        # Create a clean test file before each test
        if os.path.exists(ALLOW_LIST_TEST_FILE):
            os.remove(ALLOW_LIST_TEST_FILE)

    def tearDown(self):
        # Clean up the test file after each test
        if os.path.exists(ALLOW_LIST_TEST_FILE):
            os.remove(ALLOW_LIST_TEST_FILE)

    def test_initial_empty_list(self):
        """Test that an empty list is returned if the file doesn't exist."""
        self.assertEqual(read_allow_list(), [])

    def test_add_single_entry(self):
        """Test adding a single entry."""
        entries = ["test@example.com"]
        write_allow_list(entries)
        self.assertEqual(read_allow_list(), entries)

    def test_add_multiple_entries(self):
        """Test adding multiple entries, ensuring sorting and uniqueness."""
        entries = ["domain.com", "test@example.com", "another@mail.net", "domain.com"]
        write_allow_list(entries)
        expected = ["another@mail.net", "domain.com", "test@example.com"]
        self.assertEqual(read_allow_list(), expected)

    def test_remove_entry(self):
        """Test removing an entry by writing a new list."""
        initial_entries = ["a@a.com", "b@b.com", "c@c.com"]
        write_allow_list(initial_entries)

        updated_entries = ["a@a.com", "c@c.com"]
        write_allow_list(updated_entries)
        self.assertEqual(read_allow_list(), updated_entries)

    def test_empty_file_after_write(self):
        """Test writing an empty list clears the file."""
        initial_entries = ["a@a.com"]
        write_allow_list(initial_entries)
        write_allow_list([])
        self.assertEqual(read_allow_list(), [])

if __name__ == '__main__':
    unittest.main()