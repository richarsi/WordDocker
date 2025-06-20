import unittest
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime, timezone
import requests
from richarsi.beehive.workconsumer import fetch_workitems, update_workitem_status, update_task_status, process_workitem

class TestWorkitemProcessing(unittest.TestCase):

    @patch('richarsi.beehive.workconsumer.requests.get') 
    def test_fetch_workitems_404(self, mock_get):
        mock_get.return_value = Mock(status_code=404)
        base_url = 'http://blackboard:8000'
        response = fetch_workitems(base_url)
        self.assertEqual(response.status_code, 404)

    @patch('richarsi.beehive.workconsumer.requests.get')
    def test_fetch_workitems_200(self, mock_get):
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = [{"_id": "1", "task_id": "100"}]
        mock_get.return_value = mock_response
        base_url = 'http://blackboard:8000'
        response = fetch_workitems(base_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    @patch('richarsi.beehive.workconsumer.requests.put')
    def test_update_workitem_status(self, mock_put):
        mock_put.return_value = Mock(status_code=200)
        base_url = 'http://blackboard:8000'
        response = update_workitem_status(base_url, "1", "RUNNING")
        self.assertEqual(response.status_code, 200)

# class TestUpdateTaskStatus(unittest.TestCase):

#     @patch('richarsi.beehive.workconsumer.requests.put')
#     def test_update_task_status_success(self, mock_put):
#         # Define what the mock should return
#         mock_response = requests.Response()
#         mock_response.status_code = 200
#         mock_response._content = b'Success'
#         mock_put.return_value = mock_response
        
#         # Call the function with test data
#         response = update_task_status('http://example.com', 'task123', 'completed')

#         # Check if the request was sent with correct parameters
#         mock_put.assert_called_once_with(
#             'http://example.com/tasks/task123',
#             json={'status': 'completed'}
#         )

#         # Verify the response
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.text, 'Success')
    
#     @patch('richarsi.beehive.workconsumer.requests.put')
#     def test_update_task_status_failure(self, mock_put):
#         # Simulate a failure response
#         mock_response = requests.Response()
#         mock_response.status_code = 404
#         mock_response._content = b'Not Found'
#         mock_put.return_value = mock_response
        
#         # Call the function with test data
#         response = update_task_status('http://example.com', 'nonexistent_task', 'completed')

#         # Check if the request was sent with correct parameters
#         mock_put.assert_called_once_with(
#             'http://example.com/tasks/nonexistent_task',
#             json={'status': 'completed'}
#         )

#         # Verify the response
#         self.assertEqual(response.status_code, 404)
#         self.assertEqual(response.text, 'Not Found')

class TestProcessWorkItem(unittest.TestCase):
    
    @patch('requests.post')
    def test_process_workitem_success(self, mock_post):
        # Arrange
        base_url = "http://example.com"
        task_id = "12345"
        current_sequence = "abc"
        remaining_elements = "def"

        # Example output for all_possible_words mock
        all_words_mock = ['word1', 'word2']
        
        # Mock the response object
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        with patch('richarsi.beehive.workconsumer.all_possible_words', return_value=all_words_mock):
            # Act
            final_response = process_workitem(base_url, task_id, current_sequence, remaining_elements)

            # Assert
            self.assertEqual(mock_post.call_count, len(all_words_mock))
            self.assertEqual(final_response.status_code, 200)

    @patch('requests.post')
    def test_process_workitem_failure(self, mock_post):
        # Arrange
        base_url = "http://example.com"
        task_id = "12345"
        current_sequence = "abc"
        remaining_elements = "def"

        # Example output for all_possible_words mock
        all_words_mock = ['word1', 'word2']

        # Mock the response object to simulate failure on first call
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        with patch('richarsi.beehive.workconsumer.all_possible_words', return_value=all_words_mock):
            # Act
            final_response = process_workitem(base_url, task_id, current_sequence, remaining_elements)

            # Assert
            self.assertEqual(mock_post.call_count, 1)
            self.assertEqual(final_response.status_code, 500)

if __name__ == '__main__':
    unittest.main()