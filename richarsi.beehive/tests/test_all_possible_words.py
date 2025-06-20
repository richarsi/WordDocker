import unittest
from unittest.mock import patch, Mock
from richarsi.beehive.subsequencer import all_possible_words, get_first_word_starting_with

# Mock response for the API call to simulate successful and unsuccessful scenarios
def mock_get_one_word_starting_with(sequence):
    valid_sequences = ['a', 'ab', 'abc']
    current_string = ''.join([element[0] for element in sequence])
    return current_string in valid_sequences

def mock_get_first_word_starting_with(sequence):
    valid_word = 'cab'
    current_string = ''.join([element[0] for element in sequence])
    if valid_word.startswith(current_string):
        return valid_word 
    else:
        None
 
class TestAllPossibleWords(unittest.TestCase):

    @patch('richarsi.beehive.subsequencer.get_first_word_starting_with',mock_get_first_word_starting_with)
    def test_basic_functionality(self):
        letters = ['a', 'b', 'c']
        result = list(all_possible_words(letters))
        expected = [ 'cab' ]
        self.assertEqual(result, expected)

    @patch('richarsi.beehive.subsequencer.get_first_word_starting_with', mock_get_first_word_starting_with)
    def test_max_length_exceeded(self):
        letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
        with self.assertRaises(ValueError):
            list(all_possible_words(letters))

    @patch('richarsi.beehive.subsequencer.get_first_word_starting_with', mock_get_first_word_starting_with)
    def test_empty_input(self):
        letters = []
        result = list(all_possible_words(letters))
        expected = []
        self.assertEqual(result, expected)

    @patch('richarsi.beehive.subsequencer.get_first_word_starting_with', mock_get_first_word_starting_with)
    def test_minimum_length(self):
        letters = ['a', 'b', 'c']
        result = list(all_possible_words(letters, min_length = 4))
        expected = [ ]
        self.assertEqual(result, expected)

class TestGetFirstWordStartingWith(unittest.TestCase):
    
    @patch('richarsi.beehive.subsequencer.requests.get')  
    def test_successful_api_call(self, mock_get):
        # Set up the mock to return a successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'first_word': 'example'}
        mock_get.return_value = mock_response
        
        sequence = ['e', 'x']
        result = get_first_word_starting_with(sequence)
        self.assertEqual(result, 'example')

    @patch('richarsi.beehive.subsequencer.requests.get')
    def test_no_word_found(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'first_word': None}
        mock_get.return_value = mock_response
        
        sequence = ['n','o']
        result = get_first_word_starting_with(sequence)
        self.assertIsNone(result)

    @patch('richarsi.beehive.subsequencer.requests.get')
    def test_empty_sequence(self, mock_get):
        result = get_first_word_starting_with([])
        self.assertFalse(result)
        mock_get.assert_not_called()

    @patch('richarsi.beehive.subsequencer.requests.get')
    def test_api_failure(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        sequence = ['f', 'a']
        with self.assertRaises(Exception) as context:
            get_first_word_starting_with(sequence)
        
        self.assertIn("API request failed with status code", str(context.exception))

# To run the tests if this script is executed directly
if __name__ == '__main__':
    unittest.main()
