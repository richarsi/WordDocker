"""
This module calculates permutations considering all possible subsets of a list of distinct characters.
The calculation involves generating permutations for every subset from size 1 to n (inclusive),
where n is the total number of characters.

Total permutations for input lists ranging from 1 to 8 characters are shown as examples below:

1 Character: 
    - Only one permutation (itself).

2 Characters: 
    - Permutations of size 1 and 2: ['a', 'b', 'ab', 'ba'] resulting in a total of 3 unique permutations.

3 Characters:
    - Consider permutations from sizes 1 to 3.

4 to 8 Characters:
    - As the set size increases, the number of permutations grows significantly. This is due to combinations of different subsets and their respective permutations.

Mathematically, the sum of permutations for a list of n distinct characters from size 1 to n is expressed by:
    
    Total permutations = ∑ (n! / (n-k)!) for k=1 to n

Below is the summary table for quick reference:
| Number of Characters | Total Permutations (Including Subsets) |
|----------------------|----------------------------------------|
| 1                    | 1                                      |
| 2                    | 3                                      |
| 3                    | 15                                     |
| 4                    | 64                                     |
| 5                    | 325                                    |
| 6                    | 1,956                                  |
| 7                    | 13,699                                 |
| 8                    | 109,601                                |

Note:
- The rapid growth in permutations is due to both combinatorial selection of subsets and their internal arrangements.
""" 

import requests
import os

wordchecker_url = None
wordchecker_host = os.getenv('WORDCHECKER_HOST', 'wordseach')
wordchecker_port = os.getenv('WORDCHECKER_PORT', '8000')
wordchecker_url = f"http://{wordchecker_host}:{wordchecker_port}/firstword"

def all_possible_subsequences(letters: list, max_length: int = 8, min_length: int = 0):
    """
    Generate all possible subsequences of 'letters' that maintain the original order 
    and have a length greater than or equal to 'min_length'.

    Parameters:
    - letters (list): A list of letters or strings
    - max_length (int, optional): The maximum length of the sequence. Default is 8.
    - min_length (int, optional): The minimum length of the sequence. Default is 0.
    """    

    def _all_possible_subsequences(current_sequence, remaining_elements):
        """
        Recursive helper function to generate subsequences.

        :param current_sequence: List that holds the sequences formed so far.
        :param remaining_elements: List containing the remaining letters to be processed.
        """
        
        # If the current sequence in 'current_sequence' is valid (meets min_length), yield it
        if current_sequence and len(current_sequence) > min_length - 1:
            yield [element[0] for element in current_sequence]
        
        # Iterate over the elements in 'remaining_elements'
        for i in range(len(remaining_elements)):
            # Create shallow copies to preserve the current state during recursion
            cs_copy = current_sequence.copy()
            re_copy = remaining_elements.copy()
            
            # Check if the order of letters is preserved
            for element in re_copy:
                if re_copy[i][0] == element[0] and re_copy[i][1] > element[1]:  # Order hasn't been preserved
                    break
            else:
                # Append the current letter to 'cs_copy' and remove it from 're_copy'
                cs_copy.append(re_copy.pop(i))
                # Recursively call _solve with updated 'cs_copy' and 're_copy'
                yield from _all_possible_subsequences(cs_copy, re_copy)

    # Check if the input exceeds the allowed maximum length
    if len(letters) > max_length:
        print(f"Input exceeded {max_length} characters and was truncated.")
        raise ValueError(f"Input exceeded {max_length} characters.")
    
    # Initialise empty list 'current_sequence' and 'remaining_elements' with tuples of (letter, original index)
    current_sequence = list()
    remaining_elements = [(letter, index) for index, letter in enumerate(letters)]
    
    # Start the recursive process by calling '_sequence'
    yield from _all_possible_subsequences(current_sequence, remaining_elements)

def get_first_word_starting_with(sequence: list):
    """
    Make a REST API call to check if there are any words that start with the current sequence.

    :param sequence: The current sequence for which to check word beginnings.
    :return: Return first word starting with 'sequence', None otherwise.
    """
    # Convert the list of characters into a string
    current_string = ''.join([element[0] for element in sequence])
    
    if not current_string:
        return False
    
    # Replace the URL and any required query parameters as necessary
    response = requests.get(f'{wordchecker_url}/{current_string}')
    
    # API returns a JSON object with a key 'first_word' that tells us if words exist
    if response.status_code == 200:
        data = response.json()
        return data.get('first_word', None)
    else:
        raise Exception(f"API request failed with status code {response.status_code}")

def all_possible_words(letters: list, max_length: int = 8, min_length: int = 0):
    """
    Generate all possible subsequences of 'letters' that maintain the original order,
    have a length greater than or equal to 'min_length', and are validated by a REST API.

    Parameters:
    - letters (list): A list of letters or strings
    - max_length (int, optional): The maximum length of the sequence. Default is 8.
    - min_length (int, optional): The minimum length of the sequence. Default is 0.
    """    

    def _all_possible_words(current_sequence, remaining_elements):
        """
        Recursive helper function to generate subsequences.

        :param current_sequence: List that holds the sequences formed so far.
        :param remaining_elements: List containing the remaining letters to be processed.
        """
        # Check with the API whether any words start with 'current_sequence'
        # Convert the list of characters into a string
        current_string = ''.join([element[0] for element in current_sequence])
        
        # Skip check if 'current_sequence' is empty because that will always return None
        first_word = get_first_word_starting_with(current_sequence)
        if current_sequence and not first_word:
            return
        
        # If the current sequence in 'current_sequence' is valid (meets min_length) and is a word then yield it
        if current_sequence and len(current_sequence) > min_length - 1 and current_string == first_word:
            yield first_word
        
        # Iterate over the elements in 'remaining_elements'
        for i in range(len(remaining_elements)):
            # Create shallow copies to preserve the current state during recursion
            cs_copy = current_sequence.copy()
            re_copy = remaining_elements.copy()
            
            # Check if the order of letters is preserved
            for element in re_copy:
                if re_copy[i][0] == element[0] and re_copy[i][1] > element[1]:  # Order hasn't been preserved
                    break
            else:
                # Append the current letter to 'cs_copy' and remove it from 're_copy'
                cs_copy.append(re_copy.pop(i))
                # Recursively call _all_possible_subsequences with updated 'cs_copy' and 're_copy'
                yield from _all_possible_words(cs_copy, re_copy)

    # Check if the input exceeds the allowed maximum length
    if len(letters) > max_length:
        print(f"Input exceeded {max_length} characters and was truncated.")
        raise ValueError(f"Input exceeded {max_length} characters.")
    
    # Initialise empty list 'current_sequence' and 'remaining_elements' with tuples of (letter, original index)
    current_sequence = list()
    remaining_elements = [(letter, index) for index, letter in enumerate(letters)]
    
    # Start the recursive process by calling '_all_possible_subsequences'
    yield from _all_possible_words(current_sequence, remaining_elements)

