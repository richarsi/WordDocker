import unittest
from richarsi.beehive.subsequencer import all_possible_subsequences 

class TestAllPossibleSubsequences(unittest.TestCase):
    
    def test_sequence_no_min_length(self):
        letters = ['a', 'b', 'c']
        results = list(all_possible_subsequences(letters))
        expected = [['a'], ['a', 'b'], ['a', 'b', 'c'], ['a', 'c'], ['a', 'c', 'b'], 
                    ['b'], ['b', 'a'], ['b', 'a', 'c'], ['b', 'c'], ['b', 'c', 'a'], 
                    ['c'], ['c', 'a'], ['c', 'a', 'b'], ['c', 'b'], ['c', 'b', 'a']] 
        self.assertEqual(results, expected)
    
    def test_sequence_empty_list(self):
        letters = []
        results = list(all_possible_subsequences(letters))
        expected = []
        self.assertEqual(results, expected)

    def test_sequence_single_element(self):
        letters = ['x']
        results = list(all_possible_subsequences(letters))
        expected = [['x']]
        self.assertEqual(results, expected)
    
    def test_sequence_min_length_greater_than_length(self):
        letters = ['a', 'b']
        min_length = 3
        results = list(all_possible_subsequences(letters, min_length=min_length))
        expected = []
        self.assertEqual(results, expected)
    
    def test_sequence_min_length_two(self):
        letters = ['a', 'b', 'c']
        min_length = 2
        results = list(all_possible_subsequences(letters, min_length=min_length))
        expected = [['a', 'b'], ['a', 'b', 'c'], ['a', 'c'], ['a', 'c', 'b'], 
                    ['b', 'a'], ['b', 'a', 'c'], ['b', 'c'], ['b', 'c', 'a'], 
                    ['c', 'a'], ['c', 'a', 'b'], ['c', 'b'], ['c', 'b', 'a']] 
        self.assertEqual(results, expected)

    def test_sequence_max_length_two(self):
        letters = ['a', 'b', 'c']
        max_length = 2
        with self.assertRaises(ValueError) as context:
            results = list(all_possible_subsequences(letters, max_length=max_length))
        self.assertEqual(str(context.exception), "Input exceeded 2 characters.")

    def test_sequence_repeating_elements(self):
        letters = ['a', 'a', 'b']
        results = list(all_possible_subsequences(letters))
        expected = [['a'], ['a', 'a'], ['a', 'a', 'b'],['a', 'b'], ['a', 'b', 'a'], 
                    ['b'], ['b', 'a'], ['b', 'a', 'a'] ] 
        self.assertEqual(results, expected)


if __name__ == "__main__":
    unittest.main()