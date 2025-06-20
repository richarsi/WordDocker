import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify
from bson.objectid import ObjectId
from pymongo.collection import Collection
from bson.objectid import ObjectId
from http import HTTPStatus
from richarsi.blackboard.app import app  # Import your Flask app
import datetime
import json

class TestFlaskApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = app.test_client()
        cls.app.testing = True

    def test_heartbeat(self):
        """Test /healthcheck endpoint."""
        with patch('richarsi.blackboard.app.db.command', return_value={'ok': 1.0}) as mock_db_command:
            response = self.app.get('/healthcheck')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data.decode('utf-8'), 'Database is operational.')
            mock_db_command.assert_called_once_with("ping")

    @patch('richarsi.blackboard.app.tasks_collection.insert_one')
    def test_create_task_success(self, mock_insert_one):
        """Test successful task creation."""
        new_task_id = '60bb4b001f3850f5c7b48c2a'
        
        mock_result = MagicMock()
        mock_result.inserted_id = ObjectId(new_task_id)
        mock_insert_one.return_value = mock_result
        
        response = self.app.post('/tasks', json={'letters': 'abcd'})
        self.assertEqual(response.status_code, 202)
        self.assertIn('/status/60bb4b001f3850f5c7b48c2a', response.headers['Location'])

    def test_create_task_failure(self):
        """Test task creation failure due to missing letters."""
        response = self.app.post('/tasks', json={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.decode('utf-8'), 'Invalid input: "letters" required.')

    @patch('richarsi.blackboard.app.tasks_collection.find_one')
    def test_get_task_not_found(self, mock_find_one):
        """Test getting a non-existing task."""
        mock_find_one.return_value = None
        
        response = self.app.get('/tasks/60bb4b001f3850f5c7b48c2a')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.decode('utf-8'), 'Task not found.')

class TestManageTask(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('richarsi.blackboard.app.tasks_collection.find_one')
    def test_get_task_found(self, mock_find_one):
        # Mock successful find operation
        mock_find_one.return_value = {'_id': ObjectId('6564bff6985caa24ef000001'), 'name': 'Test Task', 'status': 'NEW'}
        
        response = self.app.get('/tasks/6564bff6985caa24ef000001')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'_id': '6564bff6985caa24ef000001', 'name': 'Test Task', 'status': 'NEW'})

    @patch('richarsi.blackboard.app.tasks_collection.find_one')
    def test_get_task_not_found(self, mock_find_one):
        # Mock task not found
        mock_find_one.return_value = None
        
        response = self.app.get('/tasks/6564bff6985caa24ef000002')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.decode(), 'Task not found.')

    @patch('richarsi.blackboard.app.tasks_collection.update_one')
    def test_put_task_update_successful(self, mock_update_one):
        # Mock successful update
        mock_update_one.return_value.matched_count = 1
        
        response = self.app.put(
            '/tasks/6564bff6985caa24ef000001',
            json={'status': 'COMPLETED'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), 'Task updated successfully.')

    @patch('richarsi.blackboard.app.tasks_collection.update_one')
    def test_put_task_not_found(self, mock_update_one):
        # Mock update failed, task not found
        mock_update_one.return_value.matched_count = 0
        
        response = self.app.put(
            '/tasks/6564bff6985caa24ef000002',
            json={'status': 'RUNNING'}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data.decode(), 'Task not found.')

    @patch('richarsi.blackboard.app.tasks_collection.delete_one')
    def test_delete_task_successful(self, mock_delete_one):
        # Mock successful delete
        mock_delete_one.return_value.deleted_count = 1
        
        response = self.app.delete('/tasks/6564bff6985caa24ef000001')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), 'Task deleted successfully.')

    @patch('richarsi.blackboard.app.tasks_collection.delete_one')
    def test_delete_task_not_found(self, mock_delete_one):
        # Mock delete failed, task not found
        mock_delete_one.return_value.deleted_count = 0
        
        response = self.app.delete('/tasks/6564bff6985caa24ef000002')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data.decode(), 'Task not found.')

    @patch('richarsi.blackboard.app.tasks_collection.find_one')
    def test_internal_server_error(self, mock_find_one):
        # Induce an exception during find operation
        mock_find_one.side_effect = Exception("Database error")

        response = self.app.get('/tasks/6564bff6985caa24ef000003')
        self.assertEqual(response.status_code, 500)
        self.assertIn("Database error", response.data.decode())

class TestGetTaskStatus(unittest.TestCase):
    def setUp(self):
        # Set up the Flask test client
        self.app = app.test_client()
        self.app.testing = True

    @patch('richarsi.blackboard.app.tasks_collection.find_one')
    def test_get_task_status_found_completed(self, mock_find_one):
        # Mock find_one to return a task with status 'COMPLETED'
        mock_find_one.return_value = {
            '_id': ObjectId('6564bff6985caa24ef000001'),
            'status': 'COMPLETED',
            'lastUpdated': None
        }

        response = self.app.get('/status/6564bff6985caa24ef000001')
        
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers['Location'], '/tasks/6564bff6985caa24ef000001/words')

    @patch('richarsi.blackboard.app.tasks_collection.find_one')
    def test_get_task_status_found_running(self, mock_find_one):
        # Mock find_one to return a task with status other than 'COMPLETED'
        mock_find_one.return_value = {
            '_id': ObjectId('6564bff6985caa24ef000002'),
            'status': 'RUNNING',
            'lastUpdated': datetime.datetime(2023, 10, 1, 0, 0, 0)  # Example timestamp
        }

        response = self.app.get('/status/6564bff6985caa24ef000002')
        
        self.assertEqual(response.status_code, 200)
        expected_data = {"lastUpdated": "2023-10-01T00:00:00"}
        self.assertEqual(response.json, expected_data)

    @patch('richarsi.blackboard.app.tasks_collection.find_one')
    def test_get_task_status_not_found(self, mock_find_one):
        # Mock find_one to return None
        mock_find_one.return_value = None

        response = self.app.get('/status/6564bff6985caa24ef000003')
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data.decode(), 'Task not found.')

    @patch('richarsi.blackboard.app.tasks_collection.find_one')
    def test_get_task_status_exception(self, mock_find_one):
        # Mock find_one to raise an exception
        mock_find_one.side_effect = Exception('Database error')

        response = self.app.get('/status/6564bff6985caa24ef000004')
        
        self.assertEqual(response.status_code, 500)
        self.assertIn('Database error', response.data.decode())

class TestGetTasksByStatus(unittest.TestCase):

    def setUp(self):
        # Set up the Flask test client for testing
        self.app = app.test_client()
        self.app.testing = True

    @patch('richarsi.blackboard.app.tasks_collection.find')
    def test_get_tasks_by_valid_status(self, mock_find):
        # Mock the database response for a valid status query
        mock_find.return_value = [
            {'_id': ObjectId('6564bff6985caa24ef000001'), 'status': 'NEW'}
        ]

        response = self.app.get('/tasks?status=NEW')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]['status'], 'NEW')

    @patch('richarsi.blackboard.app.tasks_collection.find')
    def test_get_tasks_by_invalid_status(self, mock_find):
        # No need to mock find as it should not be called
        response = self.app.get('/tasks?status=INVALID_STATUS')

        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid status', response.data.decode())

    @patch('richarsi.blackboard.app.tasks_collection.find')
    def test_get_tasks_no_status(self, mock_find):
        # Mock find with no filter (i.e., return all tasks)
        mock_find.return_value = [
            {'_id': ObjectId('6564bff6985caa24ef000001'), 'status': 'NEW'},
            {'_id': ObjectId('6564bff6985caa24ef000002'), 'status': 'COMPLETED'}
        ]

        response = self.app.get('/tasks')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)

    @patch('richarsi.blackboard.app.tasks_collection.find')
    def test_get_tasks_by_status_not_found(self, mock_find):
        # Mock find to return an empty list simulating no matching tasks
        mock_find.return_value = []

        response = self.app.get('/tasks?status=RUNNING')

        self.assertEqual(response.status_code, 404)
        self.assertIn('Nothing found.', response.data.decode())

    @patch('richarsi.blackboard.app.tasks_collection.find')
    def test_get_tasks_exception(self, mock_find):
        # Mock find to raise an exception
        mock_find.side_effect = Exception('Database error')

        response = self.app.get('/tasks')

        self.assertEqual(response.status_code, 500)
        self.assertIn('Database error', response.data.decode())

class TestAddWordToTask(unittest.TestCase):

    def setUp(self):
        # Setup the Flask test client for testing
        self.app = app.test_client()
        self.app.testing = True

    @patch('richarsi.blackboard.app.tasks_collection.find_one')
    @patch('richarsi.blackboard.app.words_collection.insert_one')
    def test_add_word_to_task_success(self, mock_insert_one, mock_find_one):
        # Mock finding a task with status "RUNNING"
        mock_find_one.return_value = {'_id': ObjectId('6564bff6985caa24ef000001'), 'status': 'RUNNING'}
        # Mock successful word insertion
        mock_insert_one.return_value = MagicMock(acknowledged=True)

        response = self.app.post(
            '/tasks/6564bff6985caa24ef000001/words',
            json={'word': 'example'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('Word added successfully', response.data.decode())

    @patch('richarsi.blackboard.app.tasks_collection.find_one')
    def test_add_word_to_non_existent_task(self, mock_find_one):
        # Mock not finding the task
        mock_find_one.return_value = None

        response = self.app.post(
            '/tasks/6564bff6985caa24ef000002/words',
            json={'word': 'example'}
        )

        self.assertEqual(response.status_code, 404)
        self.assertIn('Task not found.', response.data.decode())

    @patch('richarsi.blackboard.app.tasks_collection.find_one')
    def test_add_word_to_task_wrong_status(self, mock_find_one):
        # Mock finding a task with status "NEW"
        mock_find_one.return_value = {'_id': ObjectId('6564bff6985caa24ef000003'), 'status': 'COMPLETED'}

        response = self.app.post(
            '/tasks/6564bff6985caa24ef000003/words',
            json={'word': 'example'}
        )

        self.assertEqual(response.status_code, 403)
        self.assertIn('Task "6564bff6985caa24ef000003" status is "COMPLETED" and cannot add any more words to it.', response.data.decode())

    @patch('richarsi.blackboard.app.tasks_collection.find_one')
    @patch('richarsi.blackboard.app.words_collection.insert_one')
    def test_add_word_insertion_failure(self, mock_insert_one, mock_find_one):
        # Mock finding a task with status "RUNNING"
        mock_find_one.return_value = {'_id': ObjectId('6564bff6985caa24ef000004'), 'status': 'RUNNING'}
        # Mock unsuccessful word insertion
        mock_insert_one.return_value = MagicMock(acknowledged=False)

        response = self.app.post(
            '/tasks/6564bff6985caa24ef000004/words',
            json={'word': 'example'}
        )

        # In case of failure in insertion, it should return an error code, assuming logic handles such cases.
        self.assertNotEqual(response.status_code, 200)

    @patch('richarsi.blackboard.app.tasks_collection.find_one')
    def test_add_word_exception(self, mock_find_one):
        # Mock an exception during task search
        mock_find_one.side_effect = Exception('Database error')

        response = self.app.post(
            '/tasks/6564bff6985caa24ef000005/words',
            json={'word': 'example'}
        )

        self.assertEqual(response.status_code, 500)
        self.assertIn('Database error', response.data.decode())


class TestGetWordsForTask(unittest.TestCase):

    def setUp(self):
        # Setup the Flask test client for testing
        self.app = app.test_client()
        self.app.testing = True

    @patch('richarsi.blackboard.app.tasks_collection.aggregate')
    def test_get_words_for_completed_task_success(self, mock_aggregate):
        # Mock a successful task retrieval with words
        mock_aggregate.return_value = [{
            "_id": ObjectId('6564bff6985caa24ef000001'),
            "status": 'COMPLETED',
            "letters": 'testing',
            "lastUpdated": datetime.datetime(2023, 10, 1, 0, 0, 0), # Example timestamp
            "started": datetime.datetime(2023, 10, 1, 0, 0, 0), # Example timestamp
            "completed": datetime.datetime(2023, 10, 1, 0, 0, 0), # Example timestamp
            "words": [ 'word1', 'word2' ]
        }]
        response = self.app.get('/tasks/6564bff6985caa24ef000001/words')

        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data.decode())
        self.assertEqual(data['status'], 'COMPLETED')
        self.assertIn('word1', data['words'])
        self.assertIn('word2', data['words'])

    @patch('richarsi.blackboard.app.tasks_collection.aggregate')
    def test_get_words_for_non_existent_task(self, mock_aggregate):
        # Mock no tasks found
        mock_aggregate.return_value = []

        response = self.app.get('/tasks/6564bff6985caa24ef000002/words')

        self.assertEqual(response.status_code, 404)
        self.assertIn('No completed task found with the given ID.', response.data.decode())

    @patch('richarsi.blackboard.app.tasks_collection.aggregate')
    def test_get_words_for_task_exception(self, mock_aggregate):
        # Mock an exception during aggregation
        mock_aggregate.side_effect = Exception('Database error')

        response = self.app.get('/tasks/6564bff6985caa24ef000003/words')

        self.assertEqual(response.status_code, 500)
        self.assertIn('Database error', response.data.decode())

class AddWorkitemsTestCase(unittest.TestCase):
    def setUp(self):
        # Set up a Flask test client
        self.app = app.test_client()
        self.app.testing = True

        # Mock collections
        self.tasks_collection = MagicMock(spec=Collection)
        self.workitems_collection = MagicMock(spec=Collection)

        # Patch the collections in your module
        patcher1 = patch('richarsi.blackboard.app.tasks_collection', self.tasks_collection)
        patcher2 = patch('richarsi.blackboard.app.workitems_collection', self.workitems_collection)

        patcher1.start()
        patcher2.start()

        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)

    def test_task_not_found(self):
        # Simulate task not found
        self.tasks_collection.find_one.return_value = None

        response = self.app.post('/tasks/507f191e810c19729de860ea/workitems')
        
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertIn('Task not found', response.get_json()['error'])

    def test_task_status_not_scheduling(self):
        # Simulate task with incorrect status
        self.tasks_collection.find_one.return_value = {'status': 'COMPLETED'}

        response = self.app.post('/tasks/507f191e810c19729de860ea/workitems')

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertIn('not SCHEDULING', response.get_json()['error'])

    def test_invalid_workitems_format(self):
        # Simulate correct task status
        self.tasks_collection.find_one.return_value = {'status': 'SCHEDULING'}

        # Send invalid workitems format (not a list)
        response = self.app.post(
            '/tasks/507f191e810c19729de860ea/workitems',
            json={'workitems': "invalid-format"}
        )

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertIn('Workitems should be a list', response.get_json()['error'])

    def test_successful_workitems_addition(self):
        # Simulate correct task status
        self.tasks_collection.find_one.return_value = {'status': 'SCHEDULING'}

        # Send valid workitems
        response = self.app.post(
            '/tasks/507f191e810c19729de860ea/workitems',
            json={'workitems': [{'current_sequence': 'seq1', 'remaining_elements': 'rem1'}]}
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn('Workitems added successfully', response.get_json()['message'])
        self.workitems_collection.insert_one.assert_called()

    def test_insertion_error(self):
        # Simulate correct task status
        self.tasks_collection.find_one.return_value = {'status': 'SCHEDULING'}

        # Simulate an insertion error
        self.workitems_collection.insert_one.side_effect = Exception("Insertion failed")

        response = self.app.post(
            '/tasks/507f191e810c19729de860ea/workitems',
            json={'workitems': [{'current_sequence': 'seq1', 'remaining_elements': 'rem1'}]}
        )

        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertIn('Insertion failed', response.get_json()['error'])

class GetWorkitemsTestCase(unittest.TestCase):
    def setUp(self):
        """Setup method executed before each test."""
        self.app = app.test_client()
        self.app.testing = True

    @patch('richarsi.blackboard.app.workitems_collection.find')
    def test_get_workitems_found(self, mock_find):
        """Test case where work items are found."""
        mock_find.return_value = [
            {
                "_id": "item_id_1",
                "task_id": "507f191e810c19729de860ea",
                "status": "in_progress",
                "lastUpdated": "2023-10-12"
            }
        ]
        response = self.app.get('/tasks/507f191e810c19729de860ea/workitems')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.is_json)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['task_id'], "507f191e810c19729de860ea")

    @patch('richarsi.blackboard.app.workitems_collection.find')
    def test_get_workitems_not_found(self, mock_find):
        """Test case where no work items are found."""
        mock_find.return_value = []
        response = self.app.get('/tasks/507f191e810c19729de860ea/workitems')

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(response.is_json)
        data = response.get_json()
        self.assertEqual(data['error'], "No workitems found for the specified task")

    @patch('richarsi.blackboard.app.workitems_collection.find', side_effect=Exception("Database connection error"))
    def test_get_workitems_error(self, mock_find):
        """Test case where an exception occurs."""
        response = self.app.get('/tasks/error_task/workitems')

        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertTrue(response.is_json)
        data = response.get_json()
        self.assertIn("An error occurred", data['error'])

class GetWorkItemsByStatusTestCase(unittest.TestCase):

    def setUp(self):
        # Create a test client for the application
        self.app = app.test_client()
        self.app.testing = True

    @patch('richarsi.blackboard.app.workitems_collection.find')
    def test_get_workitems_valid_status(self, mock_find):
        # Mock response for a valid status
        mock_data = [{'_id': '123', 'task_id': '456', 'status': 'NEW'}]
        mock_find.return_value = mock_data

        # Test with a valid status
        response = self.app.get('/workitems?status=NEW')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, mock_data)

    def test_get_workitems_invalid_status(self):
        # Test with an invalid status
        response = self.app.get('/workitems?status=INVALID_STATUS')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Invalid status "INVALID_STATUS"', response.data)

    @patch('richarsi.blackboard.app.workitems_collection.find')
    def test_get_workitems_status_not_found(self, mock_find):
        # Mock empty response for a valid status
        mock_find.return_value = []

        # Test with a valid status but no items found
        response = self.app.get('/workitems?status=COMPLETED')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Nothing found.', response.data)

    @patch('richarsi.blackboard.app.workitems_collection.find')
    def test_get_workitems_exception_handling(self, mock_find):
        # Force an exception
        mock_find.side_effect = Exception("Database error")

        # Test with exception to ensure it returns a 500
        response = self.app.get('/workitems')
        self.assertEqual(response.status_code, 500)
        self.assertIn(b'Database error', response.data)

class TestUpdateWorkitem(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    @patch('richarsi.blackboard.app.workitems_collection')
    def test_update_workitem_success(self, mock_collection):
        # Mocking MongoDB collection's update_one method
        mock_collection.update_one.return_value.matched_count = 1

        workitem_id = '617e443bfc13ae4c668c3fda'  # Example ObjectId
        response = self.app.put(f'/workitems/{workitem_id}',
                                data=json.dumps({'status': 'RUNNING'}),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Work item updated successfully"})

    @patch('richarsi.blackboard.app.workitems_collection')
    def test_update_workitem_invalid_status(self, mock_collection):
        workitem_id = '617e443bfc13ae4c668c3fda'
        response = self.app.put(f'/workitems/{workitem_id}',
                                data=json.dumps({'status': 'INVALID_STATUS'}),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Invalid status value"})
    
    @patch('richarsi.blackboard.app.workitems_collection')
    def test_update_workitem_not_found(self, mock_collection):
        # Simulate no documents matched for update
        mock_collection.update_one.return_value.matched_count = 0

        workitem_id = '617e443bfc13ae4c668c3fda'
        response = self.app.put(f'/workitems/{workitem_id}',
                                data=json.dumps({'status': 'COMPLETED'}),
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"error": "Work item not found"})

    @patch('richarsi.blackboard.app.workitems_collection')
    def test_update_workitem_internal_error(self, mock_collection):
        # Simulating an exception when updating
        mock_collection.update_one.side_effect = Exception("Database error")

        workitem_id = '617e443bfc13ae4c668c3fda'
        response = self.app.put(f'/workitems/{workitem_id}',
                                data=json.dumps({'status': 'NEW'}),
                                content_type='application/json')

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json, {"error": "Internal server error"})

# Run the tests
if __name__ == '__main__':
    unittest.main()
