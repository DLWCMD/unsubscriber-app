import unittest
import os
import unsubscriber # Imports our main script to test its functions

class TestHelperFunctions(unittest.TestCase):
    
    def test_extract_email(self):
        """Tests the extract_email function."""
        sender_with_name = "Sender Name <test@example.com>"
        sender_plain = "test@example.com"
        
        self.assertEqual(unsubscriber.extract_email(sender_with_name), "test@example.com")
        self.assertEqual(unsubscriber.extract_email(sender_plain), "test@example.com")

    def test_get_unsubscribe_mailto(self):
        """Tests the mailto link parsing function."""
        header1 = "<mailto:unsubscribe@example.com>"
        header2 = "<mailto:unsub@example.com?subject=unsubscribe>, <https://example.com/unsub>"
        header3 = "<https://example.com/unsub>"
        
        self.assertEqual(unsubscriber.get_unsubscribe_mailto(header1), "unsubscribe@example.com")
        self.assertEqual(unsubscriber.get_unsubscribe_mailto(header2), "unsub@example.com?subject=unsubscribe")
        self.assertIsNone(unsubscriber.get_unsubscribe_mailto(header3))

# This allows the test to be run from the command line
if __name__ == '__main__':
    unittest.main()