import unittest
import os
import unsubscriber

# Save the original filename from the main script so we can restore it later
ORIGINAL_ALLOW_LIST_FILE = unsubscriber.ALLOW_LIST_FILE

class TestAllowList(unittest.TestCase):
    def setUp(self):
        """This runs before the test to create a temporary test file."""
        self.test_filename = "temp_test_allow_list.txt"
        with open(self.test_filename, "w") as f:
            f.write("safedomain.com\n")
            f.write("safeuser@anotherdomain.com\n")
        # Temporarily point the main script to our test file
        unsubscriber.ALLOW_LIST_FILE = self.test_filename

    def tearDown(self):
        """This runs after the test to clean up."""
        os.remove(self.test_filename)
        # Restore the original filename in the main script
        unsubscriber.ALLOW_LIST_FILE = ORIGINAL_ALLOW_LIST_FILE

    def test_allow_list_logic(self):
        """Tests if the script correctly identifies allowed senders."""
        allow_list = unsubscriber.load_allow_list()

        # Case 1: Sender from an allowed domain (should be identified)
        sender_on_domain = "Test User <user@safedomain.com>"
        email1 = unsubscriber.extract_email(sender_on_domain)
        domain1 = email1.split('@')[-1]
        self.assertTrue(email1 in allow_list or domain1 in allow_list)

        # Case 2: Sender with a specific allowed email (should be identified)
        sender_by_email = "Safe User <safeuser@anotherdomain.com>"
        email2 = unsubscriber.extract_email(sender_by_email)
        domain2 = email2.split('@')[-1]
        self.assertTrue(email2 in allow_list or domain2 in allow_list)

        # Case 3: Sender not on the list (should NOT be identified)
        unsafe_sender = "Unsafe User <user@randomdomain.com>"
        email3 = unsubscriber.extract_email(unsafe_sender)
        domain3 = email3.split('@')[-1]
        self.assertFalse(email3 in allow_list or domain3 in allow_list)

if __name__ == '__main__':
    unittest.main()