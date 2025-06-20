import sys

# Supporting Node Class
class TrieNode:
    def __init__(self):
        # Dictionary to store children nodes of the current node
        self.children = {}

        # Boolean to indicate if the node represents the end of a complete word
        self.is_end_of_word = False

class Trie:
    def __init__(self):
        # Root node of the trie, typically empty or initialised with specific attributes
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        # Start at the root node for each new word insertion
        current = self.root

        # Process each character of the word to add it into the trie
        for char in word:
            # If the character does not exist as a child node, create a new TrieNode
            if char not in current.children:
                current.children[char] = TrieNode()

            # Move to the child node associated with the character
            current = current.children[char]

        # Mark the end of the word in the trie
        current.is_end_of_word = True

    def find_words_with_prefix(self, prefix):
        """
        Find all words in the trie that start with the given prefix.

        Parameters:
        prefix (str): The prefix to search for in the trie.

        Returns:
        List[str]: A list of words found in the trie that start with the specified prefix.
        """
        # Find the node that corresponds to the last character of the prefix
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []  # If the prefix is not present, return an empty list
            node = node.children[char]

        words = []
        self._find_words(node, prefix, words)
        return words

    def _find_words(self, node, prefix, words):
        """
        Helper method to recursively find all words starting from the given node.

        Parameters:
        node (TrieNode): The current node in the trie.
        prefix (str): The current prefix representing the path taken.
        words (List[str]): A list to collect words found during traversal.
        """
        # If the current node marks the end of a word, add the prefix to the words list
        if node.is_end_of_word:
            words.append(prefix)

        # Recursively find words for each child node
        for char, next_node in node.children.items():
            self._find_words(next_node, prefix + char, words)
    
    def find_first_with_prefix(self, prefix: str) -> str:
        # Start at the root node of the Trie
        node = self.root
        
        # Traverse through each character in the given prefix
        for char in prefix:
            # If the character exists in the current node's children
            if char in node.children:
                # Move to the child node that corresponds to the character
                node = node.children[char]
            else:
                # If any character in the prefix is not found, return an empty string
                return ""
        
        # At this point, all characters of the prefix are found.

        # Helper function to perform DFS to find the first word
        def dfs(current_node, path: str) -> str:
            # Check if the current node marks the end of a word
            if current_node.is_end_of_word:
                # Return the accumulated path as a complete word
                return path
            
            # Traverse children nodes in alphabetical order
            for char in sorted(current_node.children.keys()):
                # Perform DFS on each child and accumulate the path
                result = dfs(current_node.children[char], path + char)
                # If a valid word is found, return it
                if result:
                    return result
            
            # Return an empty string if no word is found
            return ""

        # Use DFS starting from the node where the prefix ends
        return dfs(node, prefix)

    def contains(self, word: str) -> bool:
        # Start from the root node of the trie structure
        current = self.root
        
        # Iterate through each character in the provided word
        for char in word:
            # If the character is not found among the children of the current node
            if char not in current.children:
                # The word does not exist in the trie; return False
                return False

            # Move to the child node that corresponds to the current character
            current = current.children[char]

        # After traversing all the characters, check if the current node marks the end of a valid word
        return current.is_end_of_word
    
    def calculate_memory_usage(self):
        """
        Calculate the total memory usage of the Trie.

        Returns:
            int: Total memory usage in bytes.
        """

        def size_of_node(node):
            # Compute the memory size of a single node, including its children and end word flag
            total_size = sys.getsizeof(node) + sys.getsizeof(node.children) + sys.getsizeof(node.is_end_of_word)
            # Recursively add the size of each child node
            for child in node.children.values():
                total_size += size_of_node(child)
            return total_size

        # Calculate the size starting from the root node
        total_size = size_of_node(self.root)
        
        return total_size

    def count_nodes(self):
        """
        Count the total number of nodes in the Trie.

        Returns:
            int: Total number of nodes.
        """

        def count_recursive(node):
            # Start with the current node
            count = 1
            # Recursively count all child nodes
            for child in node.children.values():
                count += count_recursive(child)
            return count

        # Count nodes starting from the root
        total_nodes = count_recursive(self.root)
        
        return total_nodes

    def count_words(self):
        """
        Count the total number of words stored in the Trie.

        Returns:
            int: Total number of complete words in the Trie.
        """

        def count_recursive(node):
            # Check if the current node marks the end of a word
            count = 1 if node.is_end_of_word else 0
            # Recursively count all complete words in the child nodes
            for child in node.children.values():
                count += count_recursive(child)
            return count

        # Count words starting from the root
        total_words = count_recursive(self.root)
        
        return total_words
    
    def build_trie_from_file(self,file_path):
        
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()  # Remove any leading/trailing whitespace or newline characters
                trie = Trie()
                self.insert(line)