import unittest
from richarsi.wordchecker.app import app
# from richarsi.wordsearch.trie import Trie

class TestIsWordEndpoint(unittest.TestCase):
    def setUp(self):
        """
        Set up the testing environment before each test is run.
        
        Initializes the Flask test client for the application.
        """
        # Create a test client using the Flask application configured for testing
        self.app = app.test_client()
        self.app.testing = True
    
    def test_is_word_exists(self):
        """
        Test case for verifying if an existing word is recognized by the Trie.
        """
        # Assume 'hello' is a word in the Trie
        response = self.app.get('/isword/hello')
        
        # Decode the response data (JSON) into a dictionary
        data = response.get_json()
        
        # Check if the JSON response contains the expected result
        self.assertEqual(data['result'], True)
        # Check that the HTTP status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

    def test_is_word_not_exists(self):
        """
        Test case for verifying if a non-existent word is correctly reported as missing.
        """
        # Assume 'xyzabc' is NOT a word in the Trie
        response = self.app.get('/isword/xyzabc')
        
        # Decode the response data (JSON) into a dictionary
        data = response.get_json()
        
        # Check if the JSON response contains the expected result
        self.assertEqual(data['result'], False)
        # Check that the HTTP status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
    
    # Add more test cases as necessary

class TestStartsWithEndpoint(unittest.TestCase):
    def setUp(self):
        """Set up the test client for the Flask application."""
        self.app = app.test_client()
        self.app.testing = True

    # HOW DO YOU CREATE THE APP WITHOUT LOADING FROM THE FILESYSTEM?
    # def test_startswith_valid_prefix(self):
    #     """Test the startswith endpoint with a valid prefix."""
    #     response = self.app.get('/startswith/app')  # Replace 'app' with any prefix you want to test
    #     self.assertEqual(response.status_code, 200)
    #     expected_words = ['apple', 'appetite', 'application']
    #     data = response.get_json()
    #     self.assertEqual(sorted(data['result']), sorted(expected_words))

    def test_startswith_invalid_prefix(self):
        """Test the startswith endpoint with an invalid prefix."""
        response = self.app.get('/startswith/zexyz')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['result'], [])  # Expecting an empty list for a non-existent prefix

    def test_startswith_empty_prefix(self):
        """Test the startswith endpoint with an empty prefix."""
        response = self.app.get('/startswith/')
        self.assertEqual(response.status_code, 404)  # Could be a 404 if route isn't configured for empty string

if __name__ == '__main__':
    # Run the test suite
    unittest.main()

# run from the command line
# python -m unittest ./tests/test_flask_app.py
# python -m unittest ./tests/test*.py