import os
from flask import Flask, jsonify, request
from richarsi.wordchecker.trie import Trie
import time
import logging
from socket import gethostname, gethostbyname

WORDCHECKER_LOG_LEVEL = os.getenv('WORDCHECKER_LOG_LEVEL', 'INFO').upper()
# Convert the string representation of the log level to a numeric value
log_level = getattr(logging, WORDCHECKER_LOG_LEVEL, logging.INFO)
# Set up Python logging
hostIP = gethostbyname(gethostname())
# Set up the logger
logging.basicConfig(
    level=log_level,  # Set log level
    format='%(asctime)s - %(name)s - {hostIP} - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Output logs to the console (stdout)
    ]
)

# Initialize a new Flask application
app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format=f'%(asctime)s - {hostIP} - %(levelname)s - %(message)s')

# Create a new instance of the Trie data structure
trie = Trie()

# Build the trie from a given file containing words
# Ensure the file path is correct and accessible
trie.build_trie_from_file('etc/anagram_dictionary.txt') # path/to/your/file.txt

# Log out statistics about the Trie
calculate_memory_usage = trie.calculate_memory_usage()
count_nodes = trie.count_nodes()
count_words = trie.count_words()
logging.info(f"Trie statistics: words={count_words}; nodes={count_nodes}; memory={calculate_memory_usage} bytes.")  # output trie statistics

@app.route('/isword/<string:word>', methods=['GET'])
def is_word(word):
    """
    Check if a given word exists in the Trie.

    This endpoint receives a word via URL parameter and checks its existence 
    within the Trie data structure.

    :param word: The word to be checked; passed as a string in the URL.
    :return: A JSON response containing a single property 'result', which indicates 
             whether the word is present (True) in the Trie or not (False).
    """
    
    # Call the contains method on the trie to determine presence of the word
    start_time = time.time()  # Start timing
    result = trie.contains(word)
    end_time = time.time()  # End timing
    elapsed_time = end_time - start_time  # Calculate duration in seconds
    logging.info(f"Time taken to search for '{word}': {elapsed_time:.6f} seconds")  # Log the time taken

    # Return the result as a JSON object
    return jsonify({'result': result})

# Define a route in the Flask app using a decorator
# The route '/startswith/<prefix>' handles GET requests
# '<prefix>' is a dynamic URL segment that captures input as a string
@app.route('/startswith/<string:prefix>', methods=['GET'])
def startswith(prefix):
    """
    Route for finding words that start with a given prefix.

    :param word: The word to be checked; passed as a string in the URL.

    Returns:
    Response: A JSON response containing a list of words starting with the given prefix.
    """
    start_time = time.time()  # Start timing
    result = trie.find_words_with_prefix(prefix)
    end_time = time.time()  # End timing
    elapsed_time = end_time - start_time  # Calculate duration in seconds
    logging.info(f"Time taken to search for words starting with '{prefix}': {elapsed_time:.6f} seconds")  # Log the time taken

    return jsonify({'result': result})

# Define a route in the Flask app using a decorator
# The route '/firstword/<prefix>' handles GET requests
# '<prefix>' is a dynamic URL segment that captures input as a string
@app.route('/firstword/<prefix>', methods=['GET'])
def firstword(prefix: str):
    """
    Find and return the first word with the given prefix.

    This function uses a Trie data structure to search for and retrieve the 
    first word in the dataset that starts with the specified prefix. The 
    result is returned as a JSON object.

    Args:
        prefix (str): The prefix string used to find the matching word.

    Returns:
        flask.Response: A JSON response containing the first word that matches 
        the given prefix, structured as {'first_word': <result>}.
    
    Example:
        >>> firstword('pre')
        # Assuming 'pre' is a valid prefix in the Trie, this will return a 
        # JSON response such as {'first_word': 'prefix'}.
    """
    # Call the Trie function to find the first word with the given prefix
    # 'prefix' is the string received from the URL
    start_time = time.time()  # Start timing
    result = trie.find_first_with_prefix(prefix)
    end_time = time.time()  # End timing
    elapsed_time = end_time - start_time  # Calculate duration in seconds
    logging.info(f"Time taken to find the first word starting with '{prefix}': {elapsed_time:.6f} seconds")  # Log the time taken    
    # Return the retrieved result as a JSON response
    # The response includes a key-value pair where 'first_word' is the key
    return jsonify({'first_word': result})

if __name__ == '__main__':
    # Start the Flask development server
    # Set debug=True for automatic reloading during development
    app.run(debug=True)