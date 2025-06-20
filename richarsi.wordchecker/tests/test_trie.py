import unittest
import os
from richarsi.wordchecker.trie import Trie

class TestTrieMethods(unittest.TestCase):

    def test_insert_single_word(self):
        trie = Trie()
        trie.insert("hello")
        
        node = trie.root
        for char in "hello":
            self.assertIn(char, node.children)
            node = node.children[char]
        self.assertTrue(node.is_end_of_word)

    def test_insert_multiple_words(self):
        trie = Trie()
        words = ["hello", "world"]
        for word in words:
            trie.insert(word)
        
        for word in words:
            node = trie.root
            for char in word:
                self.assertIn(char, node.children)
                node = node.children[char]
            self.assertTrue(node.is_end_of_word)
            
    def test_build_trie_from_file(self):
        # Create a temporary file to test
        file_path = 'test_file.txt'
        with open(file_path, 'w') as f:
            f.write('cat\n')
            f.write('dog\n')
        
        trie = Trie()
        trie.build_trie_from_file(file_path)

        # Check that 'cat' is correctly inserted
        node = trie.root
        for char in "cat":
            self.assertIn(char, node.children)
            node = node.children[char]
        self.assertTrue(node.is_end_of_word)

        # Check that 'dog' is correctly inserted
        node = trie.root
        for char in "dog":
            self.assertIn(char, node.children)
            node = node.children[char]
        self.assertTrue(node.is_end_of_word)

        # Clean up the temporary file
        os.remove(file_path)

class TestTrieContains(unittest.TestCase):
    
    def setUp(self):
        self.trie = Trie()
        self.trie.insert("hello")
        self.trie.insert("world")
        self.trie.insert("trie")
        self.trie.insert("worldly")

    def test_contains_existing_word(self):
        # Test if the trie contains a word that has been inserted
        self.assertTrue(self.trie.contains("hello"), "The word 'hello' should be found in the trie.")
        self.assertTrue(self.trie.contains("world"), "The word 'world' should be found in the trie.")
        self.assertTrue(self.trie.contains("worldly"), "The word 'worldly' should be found in the trie.")
        self.assertTrue(self.trie.contains("trie"), "The word 'trie' should be found in the trie.")

    def test_contains_non_existing_word(self):
        # Test if the trie returns False for a word not inserted
        self.assertFalse(self.trie.contains("helloo"), "The word 'helloo' should not be found in the trie.")
        self.assertFalse(self.trie.contains("worldl"), "The word 'worldl' should not be found in the trie.")
        self.assertFalse(self.trie.contains("tri"), "The partial word 'tri' should not be considered as complete in the trie.")
        
    def test_empty_trie(self):
        # Test with an empty trie
        empty_trie = Trie()
        self.assertFalse(empty_trie.contains("anything"), "No words should be found in an empty trie.")

class TestTrieFindWordsWithPrefix(unittest.TestCase):
    def setUp(self):
        # Setup the Trie with some initial words
        self.trie = Trie()
        self.words_to_insert = ["hello", "world", "help", "helicopter", "hire"]
        for word in self.words_to_insert:
            self.trie.insert(word)

    def test_find_words_with_prefix(self):
        # Test cases for various prefixes
        test_cases = [
            ("hel", ["hello", "help", "helicopter"]),
            ("hi", ["hire"]),
            ("wor", ["world"]),
            ("xyz", []),
            ("h", ["hello", "help", "helicopter", "hire"]),
        ]

        for prefix, expected in test_cases:
            with self.subTest(prefix=prefix):
                result = self.trie.find_words_with_prefix(prefix)
                self.assertCountEqual(result, expected, f"Failed for prefix: {prefix}")

class TestTrieStatisticsMethods(unittest.TestCase):
    
    def setUp(self):
        """Set up a Trie instance before each test."""
        self.trie = Trie()
        # words_to_insert = ["hello",  "help", "helicopter", "hire"]
        words_to_insert = ["hello", "world", "help", "helicopter", "hire"]
        for word in words_to_insert:
            self.trie.insert(word)

    def test_calculate_memory_usage(self):
        """Test that calculate_memory_usage returns a reasonable value."""
        memory_usage = self.trie.calculate_memory_usage()
        
        # Ensure that memory usage is greater than zero
        self.assertGreater(memory_usage, 0, "Memory usage should be greater than zero.")

    def test_count_nodes(self):
        """Test count_nodes to ensure it counts nodes correctly."""
        node_count = self.trie.count_nodes()
        
        # Expected node count after inserting the words
        expected_node_count = 22
        self.assertEqual(node_count, expected_node_count,
                         f"Expected {expected_node_count} nodes, but got {node_count}.")

    def test_count_words(self):
        """Test count_words to ensure it counts words correctly."""
        word_count = self.trie.count_words()
        
        # We inserted exactly 5 words into the Trie
        expected_word_count = 5
        self.assertEqual(word_count, expected_word_count,
                         f"Expected {expected_word_count} words, but got {word_count}.")

class TestTrieFindFirstWithPrefix(unittest.TestCase):
    def setUp(self):
        # Initialize the Trie
        self.trie = Trie()
        # Insert words into the Trie
        words = ["apple", "app", "apricot", "banana", "berry", "blueberry"]
        for word in words:
            self.trie.insert(word)

    def test_find_first_with_prefix_when_exists(self):
        # Test when a prefix exists and can form a valid word
        result = self.trie.find_first_with_prefix("app")
        self.assertEqual(result, "app", "Should find 'app' as the first match for prefix 'app'")
        
        result = self.trie.find_first_with_prefix("b")
        self.assertEqual(result, "banana", "Should find 'banana' as the first match for prefix 'b'")
        
        result = self.trie.find_first_with_prefix("blu")
        self.assertEqual(result, "blueberry", "Should find 'blueberry' as the first match for prefix 'blu'")

    def test_find_first_with_prefix_not_found(self):
        # Test when no word with the given prefix exists
        result = self.trie.find_first_with_prefix("z")
        self.assertEqual(result, '', "Should return '' for prefix 'z' which does not exist")

        result = self.trie.find_first_with_prefix("bat")
        self.assertEqual(result, '', "Should return '' for prefix 'bat' which does not exist")

    def test_find_first_with_prefix_empty_prefix(self):
        # Test for an empty prefix, should return the first word in lexicographical order
        result = self.trie.find_first_with_prefix("")
        self.assertEqual(result, "app", "Should find 'app' as the first match for empty prefix")

if __name__ == '__main__':
    unittest.main()