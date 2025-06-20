import os
import sys
from datetime import datetime, timezone
import requests
import time
from richarsi.beehive.subsequencer import all_possible_words

def fetch_workitems(blackboard_url):
    """
    Fetches work items with a status of 'NEW' from the specified base URL.

    Args:
        blackboard_url (str): The base URL of the API endpoint.

    Returns:
        requests.Response: The response object from the HTTP GET request.
    """

    # Send an HTTP GET request to the '/workitems' endpoint with a query parameter 'status' set to 'NEW'.
    response = requests.get(f"{blackboard_url}/workitems", params={'status': 'NEW'})

    # Return the response received from the GET request.
    return response

def update_workitem_status(blackboard_url, workitem_id, status):
    """
    Updates the status of a specific work item using its ID.

    Args:
        blackboard_url (str): The base URL of the API endpoint.
        workitem_id (int or str): The unique identifier of the work item to be updated.
        status (str): The new status to set for the work item.

    Returns:
        requests.Response: The response object from the HTTP PUT request.
    """

    # Create a dictionary containing the data to be sent in the PUT request, specifically the new status.
    update_data = {
        'status': status,
    }

    # Send an HTTP PUT request to update the status of the work item identified by 'workitem_id'.
    # The 'json' parameter is used to send the update_data as a JSON payload.
    put_response = requests.put(f"{blackboard_url}/workitems/{workitem_id}", json=update_data)

    # Return the response received from the PUT request.
    return put_response

def update_task_status(blackboard_url, task_id, status):
    """
    Updates the status of a specific task using its ID.

    Args:
        blackboard_url (str): The base URL of the API endpoint.
        workitem_id (int or str): The unique identifier of the task to be updated.
        status (str): The new status to set for the task.

    Returns:
        requests.Response: The response object from the HTTP PUT request.
    """

    # Create a dictionary containing the data to be sent in the PUT request, specifically the new status.
    update_data = {
        'status': status,
    }

    # Send an HTTP PUT request to update the status of the task identified by 'task_id'.
    # The 'json' parameter is used to send the update_data as a JSON payload.
    put_response = requests.put(f"{blackboard_url}/tasks/{task_id}", json=update_data)

    # Return the response received from the PUT request.
    return put_response


def process_workitem(blackboard_url, task_id, current_sequence, remaining_elements):
    """
    Processes a task by generating all possible words from provided elements
    and sending them to an API endpoint.

    Args:
        blackboard_url (str): The base URL of the API endpoint.
        task_id (int or str): The unique identifier of the task being processed.
        current_sequence (Any): Current sequence data relevant for task processing.
        remaining_elements (list of str): Elements used to generate possible words.

    Returns:
        requests.Response: The response object from the last successful HTTP POST request,
        or the response from the first failed request if any error occurs.
    """

    # Initialize variable to store the response from the POST request.
    post_response = None

    # Iterate over all possible words generated from 'remaining_elements' where the word length
    # does not exceed the number of elements.
    for next_word in all_possible_words(letters=remaining_elements, max_length=len(remaining_elements)):
        # Create a dictionary containing the task id, generated word, and the current timestamp.
        word_data = {
            'task_id': task_id,
            'word': next_word,
            'lastUpdated': datetime.now(timezone.utc).isoformat() 
        }
        # TODO remove lastUpdated because the blackboard app ignores this.  But we do need to find
        # a way to update the lastUpdated on the task so that we see progress in the web UI

        # Send an HTTP POST request with the word data as JSON to the designated API endpoint.
        post_response = requests.post(f"{blackboard_url}/tasks/{task_id}/words", json=word_data)

        # Check if the POST request was unsuccessful, print an error message and return the response.
        if post_response.status_code != 200:
            print(f"Error adding word \'{next_word}\' to the task {task_id}: {post_response.status_code}")
            return post_response

    # Return the response from the last successful POST request.
    return post_response

def main():
    try:
        blackboard_host = os.getenv('BLACKBOARD_HOST', 'blackboard')
        blackboard_port = os.getenv('BLACKBOARD_PORT', '8000')
        blackboard_url = f"http://{blackboard_host}:{blackboard_port}"

        response = fetch_workitems(blackboard_url)

        if response.status_code == 404:
            print("Nothing to process, exiting.")
            sys.exit(0)

        if response.status_code != 200:
            print(f"Error retrieving workitems: {response.status_code} - {response.text}")
            sys.exit(1)

        workitems = response.json()

        if not workitems:
            print("No new workitems found.")
            sys.exit(0)

        workitem = workitems[0]
        workitem_id = workitem['_id']
        task_id = workitem['task_id']
        current_sequence = workitem['current_sequence']
        remaining_elements = workitem['remaining_elements']

        print(f"Processing workitem={workitem_id}, task={task_id}")

        # Update the workitem status to 'RUNNING'
        put_response = update_workitem_status(blackboard_url, workitem_id, 'RUNNING')

        if put_response.status_code != 200:
            print(f"Failed to update workitem {workitem_id}. Error: {put_response.status_code} - {put_response.text}")
            sys.exit(1)

        # The watcher updates the task status to 'RUNNING'
        # Update the task status to 'RUNNING'
        # put_response = update_task_status(blackboard_url, task_id, 'RUNNING')

        # if put_response.status_code != 200:
        #     print(f"Failed to update task {task_id}. Error: {put_response.status_code} - {put_response.text}")
        #     sys.exit(1)

        post_response = process_workitem(blackboard_url,task_id,current_sequence,remaining_elements)
        
        if post_response.status_code != 200:
            print(f"Failed to process workitem {workitem_id}. Error: {post_response.status_code} - {post_response.text}")
            sys.exit(1) 

        complete_response = update_workitem_status(blackboard_url, workitem_id, 'COMPLETED')

        if complete_response.status_code != 200:
            print(f"Failed to complete workitem {workitem_id}. Error: {complete_response.status_code} - {complete_response.text}")
            sys.exit(1)

        sys.exit(0)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
