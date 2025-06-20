import unittest
from unittest.mock import patch
from flask import Flask, jsonify
from richarsi.wordchecker.app import app
# from richarsi.wordchecker.trie import Trie  # Replace 'your_module' with the actual module name where the function is defined.

# Assuming the Trie and Flask app are setup elsewhere
# app = Flask(__name__)

class TestFirstWordFunction(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('richarsi.wordchecker.trie.Trie.find_first_with_prefix')
    def test_firstword_successful_response(self, mock_find_first_with_prefix):
        """
        Test that a successful response is returned with a valid prefix.
        """
        mock_find_first_with_prefix.return_value = 'prefix'

        response = self.app.get('/firstword/pre')
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn('first_word', data)
        self.assertEqual(data['first_word'], 'prefix')

    @patch('richarsi.wordchecker.trie.Trie.find_first_with_prefix')
    def test_no_matching_word(self, mock_find_first):
        """
        Test that the response handles no matching word case.
        """
        mock_find_first.return_value = None
        
        response = self.app.get('/firstword/xyz')
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(data['first_word'])
    
    # TODO: get this to work!!!
    # # @patch('richarsi.wordchecker.trie.Trie.find_first_with_prefix')
    # def test_performance_logging(self, mock_find_first):
    #     """
    #     Test the logging of time taken to find a word.
    #     """
    #     with self.assertLogs('richarsi.wordchecker.app.logging', level='INFO') as log:
    #         mock_find_first.return_value = 'prefix'
            
    #         _ = self.app.get('/firstword/pre')

    #         print(f"log.output={log.output}")
    #         self.assertTrue(any("Time taken to find the first word starting with 'pre':" in message 
    #                             for message in log.output))

    # see: https://docs.python.org/3/library/unittest.mock.html#where-to-patch
    # TODO: get this to work!!!
    # @patch('richarsi.wordchecker.app.Trie')
    # def test_no_matching_word2(self, mock_trie):
    #     """
    #     Test that the response handles no matching word case.
    #     """
    #     mock_trie.build_trie_from_file.return_value = None
    #     mock_trie.find_first_with_prefix.return_value = None
        
    #     response = self.app.get('/firstword/xyz')
    #     data = response.get_json()

    #     self.assertEqual(response.status_code, 200)
    #     self.assertIsNone(data['first_word'])


if __name__ == '__main__':
    unittest.main()
