import os
from flask import Flask, request, jsonify, Response
from pymongo import MongoClient
from bson.objectid import ObjectId
from http import HTTPStatus
from datetime import datetime, timezone

app = Flask(__name__)

# Establish MongoDB connection using connection string from environment variable
mongodb_connstring = os.getenv('MONGODB_CONNSTRING', 'mongodb://localhost:27017/')
client = MongoClient(mongodb_connstring)
db = client.wordsdb
tasks_collection = db.tasks
words_collection = db.words
workitems_collection = db.work_items

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    """
    Check the database health.

    Returns:
        - 200 OK: If the database is operational.
        - 503 Service Unavailable: If there's a database issue.
    """
    try:
        # Perform a simple database operation to check connectivity
        db.command("ping")
        return Response(status=200, response='Database is operational.')
    except Exception as e:
        # Log the error and return service unavailable
        print(f"Database connection error: {str(e)}")
        return Response(status=503, response='Database is unavailable.')

@app.route('/tasks', methods=['POST'])
def create_task():
    """
    Create a new task with the given letters.

    Expects a JSON body containing "letters".
    Inserts a new document into the tasks collection with status "NEW".
    
    Returns:
        - 202 Accepted: On successful creation.
        - 400 Bad Request: If input validation fails.
        - 500 Internal Server Error: If there is an exception during execution.
    """
    try:
        data = request.json
        letters = data.get('letters')
        
        if not letters:
            return Response(status=400, response='Invalid input: "letters" required.')

        # Define task structure
        task = {
            "status": "NEW",
            "letters": letters,
            "lastUpdated": datetime.now(timezone.utc),
            "started": None,
            "completed": None
        }

        # Insert the task into the database
        result = tasks_collection.insert_one(task)
        task_id = str(result.inserted_id)

        response = Response(status=202)
        response.headers['Location'] = f'/status/{task_id}'
        return response

    except Exception as e:
        # Return 500 error with exception details
        return Response(status=500, response=str(e))

@app.route('/tasks/<string:task_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_task(task_id):
    """
    Manage a task specified by its ID.

    Path Parameters:
        - task_id: The ID of the task to be managed.
    
    HTTP Methods:
        - GET: Retrieve the task information.
        - PUT: Update the task status.
        - DELETE: Remove the task from the collection.
    
    Returns:
        - 200 OK: On successful retrieval, update, or deletion.
        - 400 Bad Request: If the task is not found with GET method.
        - 404 Not Found: If the task is not found with PUT or DELETE methods.
        - 500 Internal Server Error: For any exceptions during execution.
    """
    try:
        if request.method == 'GET':
            # Retrieve the task by its ID
            task = tasks_collection.find_one({'_id': ObjectId(task_id)})
            if task:
                # Convert the ObjectId to a string for JSON serialisation
                task['_id'] = str(task['_id'])
                return jsonify(task), 200  # Task found
            else:
                print("task not found")
                return Response(status=400, response='Task not found.')  # Task not found
        
        elif request.method == 'PUT':
            data = request.json
            new_status = data.get('status')
            if new_status not in {'NEW', 'SCHEDULING', 'SCHEDULED', 'RUNNING', 'COMPLETED'}:
                return Response(status=400, response='Invalid status value.')

            # Find and update the task status
            update_data = {
                'status': new_status,
                'lastUpdated': datetime.now(timezone.utc)
            }
            
            if new_status == 'SCHEDULED':
                update_data['scheduled_items_count'] = data.get('scheduled_items_count')

            if new_status == 'RUNNING':
                update_data['started'] = datetime.now(timezone.utc)

            if new_status == 'COMPLETED':
                update_data['completed'] = datetime.now(timezone.utc)

            result = tasks_collection.update_one(
                {'_id': ObjectId(task_id)},
                {'$set': update_data}
            )

            if result.matched_count:
                return Response(status=200, response='Task updated successfully.')
            else:
                return Response(status=404, response='Task not found.')

        elif request.method == 'DELETE':
            # Delete the task by its ID
            result = tasks_collection.delete_one({'_id': ObjectId(task_id)})

            if result.deleted_count:
                return Response(status=200, response='Task deleted successfully.')
            else:
                return Response(status=404, response='Task not found.')

    except Exception as e:
        # Return 500 error with exception details
        return Response(status=500, response=str(e))

@app.route('/status/<string:_id>', methods=['GET'])
def get_task_status(_id):
    """
    Get the status of a task by its ID.

    Args:
        _id (str): The unique identifier of the task.

    Returns:
        - 200 OK: If the task status is retrieved successfully.
        - 303 See Other: If the task is complete and redirects to /tasks/{_id}.
        - 404 Not Found: If the task does not exist.
        - 500 Internal Server Error: If there is an exception during execution.
    """
    try:
        # Find the task by ID
        task = tasks_collection.find_one({"_id": ObjectId(_id)})

        if not task:
            return Response(status=404, response='Task not found.')

        if task['status'] == 'COMPLETED':
            response = Response(status=303)
            response.headers['Location'] = f'/tasks/{_id}/words'
            return response
        else:
            last_updated = task['lastUpdated']
            return jsonify(lastUpdated=last_updated.isoformat()), 200

    except Exception as e:
        # Return 500 error with exception details
        return Response(status=500, response=str(e))
    
@app.route('/tasks', methods=['GET'])
def get_tasks_by_status():
    """
    Retrieve tasks based on their status.

    Query Parameters:
        - status (optional): The status of tasks to be retrieved, one of {"NEW", "SCHEDULING", "SCHEDULED", "RUNNING", "COMPLETED"}.
    
    Returns:
        - 200 OK: With a list of tasks matching the specified status.
        - 400 Bad Request: If the status query parameter is invalid.
        - 404 Not Found: If no tasks match the criteria.
        - 500 Internal Server Error: If there is an exception during execution.
    """
    try:
        # Valid statuses
        valid_statuses = {"NEW", "SCHEDULING", "SCHEDULED", "RUNNING", "COMPLETED"}

        # Get status from query parameters
        status = request.args.get('status')

        # Validate status if provided
        if status and status not in valid_statuses:
            return Response(
                status=400,
                response=f'Invalid status "{status}". Permissible values are {valid_statuses}.'
            )

        # Create query filter based on the status
        query_filter = {}
        if status:
            query_filter['status'] = status

        # Find tasks based on the query filter
        tasks = list(tasks_collection.find(query_filter))

        if not tasks:
            return Response(status=404, response='Nothing found.')

        # Convert ObjectId to string for JSON serialization
        for task in tasks:
            task['_id'] = str(task['_id'])

        return jsonify(tasks), 200

    except Exception as e:
        # Return 500 error with exception details
        return Response(status=500, response=str(e))

@app.route('/tasks/<string:task_id>/words', methods=['POST'])
def add_word_to_task(task_id):
    """
    Add a word record to a task.

    Path Parameters:
        - task_id: The ID of the task to which the word should be added.
    
    Request Body:
        - word: The word to be added to the task.
    
    Returns:
        - 200 OK: If the word is successfully added to the task.
        - 403 Forbidden: If the task's status is not "COMPLETED".
        - 404 Not Found: If the task is not found.
        - 500 Internal Server Error: If there is an exception during execution.
    """
    try:
        # Find the task by its ID
        task = tasks_collection.find_one({'_id': ObjectId(task_id)})

        # Check if the task exists
        if not task:
            return Response(status=404, response='Task not found.')

        # Check if the task status is "COMPLETED"
        if task['status'] == 'COMPLETED':
            return Response(
                status=403,
                response=f'Task "{task_id}" status is "{task["status"]}" and cannot add any more words to it.'
            )

        # Get the word from the request body
        word = request.json.get('word')

        # Insert the word into the words collection with the foreign key as task_id
        word_record = {
            'task_id': ObjectId(task_id),
            'word': word
        }
        
        result = words_collection.insert_one(word_record)

        # Check if insertion was successful
        if result.acknowledged:
            return Response(status=200, response='Word added successfully.')

    except Exception as e:
        # Return 500 error with exception details
        return Response(status=500, response=str(e))

@app.route('/tasks/<string:_id>/words', methods=['GET'])
def get_words_for_task(_id):
    """
    Retrieve all words for a completed task specified by _id.

    Args:
        _id (str): The unique identifier of the task.

    Returns:
        - 200 OK: With the task details and words if the task is completed.
        - 404 Not Found: If no completed task is found with the given ID.
        - 500 Internal Server Error: If there is an exception during execution.
    """
    try:
        # Aggregate query to lookup words related to the task
        # pipeline = [
        #     {"$match": {"_id": ObjectId(_id), "status": "COMPLETED"}},
        #     {"$lookup": {
        #         "from": "words",
        #         "localField": "_id",
        #         "foreignField": "task_id",
        #         "as": "task_words"
        #     }},
        #     {"$project": {
        #         "task_details": "$$ROOT",
        #         "task_words": {
        #             "$map": {
        #                 "input": "$task_words",
        #                 "as": "word_entry",
        #                 "in": "$$word_entry.word"
        #             }
        #         }
        #     }}
        # ]
        pipeline = [
            {"$match": {"_id": ObjectId(_id), "status": "COMPLETED"}},
            {"$lookup": {
                "from": "words",
                "localField": "_id",
                "foreignField": "task_id",
                "as": "task_words"
            }},
            {"$project": {
                "_id": 1,
                "status": 1,
                "letters": 1,
                "lastUpdated": 1,
                "started": 1,
                "completed": 1,
                "words": {
                    "$map": {
                    "input": "$task_words",
                    "in": "$$this.word"
                    }
                }
            }}
        ]
        tasks = list(tasks_collection.aggregate(pipeline))
        print(f"{tasks}")
        for task in tasks:
            # Convert the ObjectId to a string for JSON serialisation
            task['_id'] = str(task['_id'])
        if not tasks:
            return Response(status=404, response='No completed task found with the given ID.')

        return jsonify(tasks[0]), 200

    except Exception as e:
        # Return 500 error with exception details
        return Response(status=500, response=str(e))
   
@app.route('/tasks/<string:task_id>/workitems', methods=['POST'])
def add_workitems(task_id):
    """
    Adds work items to the specified task identified by _id if the task status 
    is 'SCHEDULING'. The work items are inserted into the workitems collection 
    with a default status of 'NEW'.

    Args:
        task_id (str): The task identifier as a string.

    Returns:
        Response: A JSON response containing a success message and HTTP 200 status 
                  on successful insertion of work items. Otherwise, returns an 
                  error message with the appropriate HTTP status.
    """
    # Fetch the task from the tasks collection using the provided _id
    task = tasks_collection.find_one({"_id": ObjectId(task_id)})
    
    # Check if the task exists
    if not task:
        return (
            jsonify({"error": "Task not found"}),
            HTTPStatus.NOT_FOUND,
        )
    
    # Check if the task's status is 'SCHEDULING'
    if task.get('status') != 'SCHEDULING':
        return (
            jsonify({"error": f"Task status is {task.get('status')}, not SCHEDULING."}),
            HTTPStatus.FORBIDDEN,
        )
    
    # Extract work items from the request body
    try:
        workitems_data = request.json.get('workitems', [])
        
        # Ensure that the workitems_data is a list
        if not isinstance(workitems_data, list):
            return (
                jsonify({"error": "Workitems should be a list"}),
                HTTPStatus.BAD_REQUEST,
            )
    except Exception as e:
        # Return an error response if there's an issue with parsing or retrieving
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400        

    for workitem in workitems_data:
        # Set default values for optional fields
        workitem.setdefault('current_sequence', '')
        workitem.setdefault('remaining_elements', '')

        # Prepare the work item record with additional required fields
        workitem_record = {
            'task_id': ObjectId(task_id),
            'status': 'NEW',
            'current_sequence': workitem['current_sequence'],
            'remaining_elements': workitem['remaining_elements'],
            'lastUpdated': datetime.now(timezone.utc)
        }

        try:
            # Insert work item record into the workitems collection
            workitems_collection.insert_one(workitem_record)
        except Exception as e:
            # Return an error response if the insertion fails
            return (
                jsonify({"error": str(e)}),
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
    
    # Return a success message if all operations succeed
    return jsonify({"message": "Workitems added successfully"}), HTTPStatus.OK

@app.route('/tasks/<string:task_id>/workitems', methods=['GET'])
def get_workitems(task_id):
    """
    Retrieves all work items for a specified task identified by _id.

    Args:
        task_id (str): The task identifier as a string.

    Returns:
        Response: A JSON response containing all work items and an HTTP 200 status 
                  if at least one work item is found, otherwise returns a 404 status.
    """
    try:
        # Fetch work items from the workitems collection using the provided task_id
        workitems = list(workitems_collection.find({"task_id": ObjectId(task_id)}))

        # Check if any work items were found
        if not workitems:
            return (
                jsonify({"error": "No workitems found for the specified task"}),
                HTTPStatus.NOT_FOUND,
            )
        
        # Format workitems for JSON response
        formatted_workitems = [{"id": str(item["_id"]), "task_id": str(item["task_id"]), "status": item["status"],
                                "current_sequence": item.get("current_sequence", ""),
                                "remaining_elements": item.get("remaining_elements", ""),
                                "lastUpdated": item["lastUpdated"]} for item in workitems]

        return jsonify(formatted_workitems), HTTPStatus.OK

    except Exception as e:
        # Return an error response in case of exceptions
        return (
            jsonify({"error": f"An error occurred: {str(e)}"}),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )

@app.route('/workitems', methods=['GET'])
def get_workitems_by_status():
    """
    Retrieve workitems based on their status.

    Query Parameters:
        - status (optional): The status of workitems to be retrieved, one of {"NEW", "RUNNING", "COMPLETED"}.
    
    Returns:
        - 200 OK: With a list of work items matching the specified status.
        - 400 Bad Request: If the status query parameter is invalid.
        - 404 Not Found: If no work items match the criteria.
        - 500 Internal Server Error: If there is an exception during execution.
    """
    try:
        # Valid statuses
        valid_statuses = {"NEW", "RUNNING", "COMPLETED"}

        # Get status from query parameters
        status = request.args.get('status')
        
        # Validate status if provided
        if status and status not in valid_statuses:
            return Response(
                status=400,
                response=f'Invalid status "{status}". Permissible values are {valid_statuses}.'
            )
        
        # Create query filter based on the status
        query_filter = {}
        if status:
            query_filter['status'] = status
        
        # Find tasks based on the query filter
        workitems = list(workitems_collection.find(query_filter))
        
        if not workitems:
            return Response(status=404, response='Nothing found.')
        
        # Convert ObjectId to string for JSON serialization
        for workitem in workitems:
            print(f"{workitem}")
            workitem['_id'] = str(workitem['_id'])
            workitem['task_id'] = str(workitem['task_id'])
        return jsonify(workitems), 200

    except Exception as e:
        # Return 500 error with exception details
        return Response(status=500, response=str(e))

@app.route('/workitems/<workitem_id>', methods=['PUT'])
def update_workitem(workitem_id):
    """
    Update the status of a work item in the MongoDB collection.

    Args:
        workitem_id (str): The ID of the work item to update.

    Request Body:
        JSON with a key 'status' having value 'NEW', 'RUNNING', or 'COMPLETED'.

    Returns:
        Response: JSON response with appropriate HTTP status code.
            - 200 OK: If the work item is successfully updated.
            - 400 Bad Request: If the status is invalid.
            - 404 Not Found: If the work item cannot be found.
            - 500 Internal Server Error: For any other errors.
    """
    try:
        # Retrieve the JSON payload from the request body
        data = request.json
        new_status = data.get('status')

        # Validate the status
        if new_status not in ['NEW', 'RUNNING', 'COMPLETED']:
            return jsonify({"error": "Invalid status value"}), 400

        # Get the current date-time in ISO format
        current_time = datetime.now(timezone.utc)

        # Prepare the update fields based on the new status
        update_fields = {'lastUpdated': current_time}

        if new_status == 'RUNNING':
            update_fields['started'] = current_time
        elif new_status == 'COMPLETED':
            update_fields['completed'] = current_time

        # Update the work item in the collection
        result = workitems_collection.update_one(
            {'_id': ObjectId(workitem_id)},
            {'$set': {'status': new_status, **update_fields}}
        )

        # Check if any document was modified
        if result.matched_count == 0:
            return jsonify({"error": "Work item not found"}), 404
        
        return jsonify({"message": "Work item updated successfully"}), 200
    
    except Exception as e:
        # Log the exception if needed
        print(f"An error occurred: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)
