import unittest
from unittest.mock import patch, MagicMock
import unittest.mock
from datetime import datetime
from richarsi.beehive.workscheduler import TaskAgent  # Assuming your code is in a file named task_agent.py

class TestTaskAgent(unittest.TestCase):

    @patch('richarsi.beehive.workscheduler.requests.Session.get')
    def test_fetch_new_tasks(self, mock_get):
        # Mock response for status 200 with JSON data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"_id": "1", "letters": "ABC"}]
        mock_get.return_value = mock_response
        
        agent = TaskAgent()
        tasks = agent.fetch_new_tasks()

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["_id"], "1")

    @patch('richarsi.beehive.workscheduler.requests.Session.put')
    def test_update_task_status_success(self, mock_put):
        # Mock response for successful update
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_put.return_value = mock_response
        
        agent = TaskAgent()
        success = agent.update_task_status("1", "SCHEDULING")

        self.assertTrue(success)

    @patch('richarsi.beehive.workscheduler.requests.Session.post')
    def test_send_workitems_success(self, mock_post):
        # Mock response for successful post
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        agent = TaskAgent()
        success = agent.send_workitems("1", "DEF")

        self.assertTrue(success)

    @patch('richarsi.beehive.workscheduler.requests.Session.get')
    @patch('richarsi.beehive.workscheduler.requests.Session.put')
    @patch('richarsi.beehive.workscheduler.requests.Session.post')
    def test_process_tasks(self, mock_post, mock_put, mock_get):
        # helper method
        def _is_isoformat_string(value):
            try:
                # Attempt to parse the string value back into a datetime object
                datetime.fromisoformat(value)
                return True
            except ValueError:
                return False

        # Mock responses for fetch, update, and post calls
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = [{"_id": "1", "letters": "ABC"}]
        mock_get.return_value = mock_get_response
        
        mock_put_response = MagicMock()
        mock_put_response.status_code = 200
        mock_put.return_value = mock_put_response
        
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post.return_value = mock_post_response

        agent = TaskAgent()
        agent.process_tasks()

        mock_get.assert_called_once() 
        mock_put.assert_called_with(f'{agent.BASE_URL}/1', json={'status': 'SCHEDULED', 'lastUpdated': unittest.mock.ANY, 'scheduled_items_count': 1})
        mock_post.assert_called_once()

        # Retrieve the actual call arguments
        args, kwargs = mock_put.call_args

        # Check that 'lastUpdated' in the json argument is a valid ISO format string
        if 'json' in kwargs and 'lastUpdated' in kwargs['json']:
            assert _is_isoformat_string(kwargs['json']['lastUpdated']), "lastUpdated is not in ISO format"
        else:
            raise AssertionError("lastUpdated key not found in json")

    def test_singleton_behavior(self):
        instance1 = TaskAgent()
        instance2 = TaskAgent()
        self.assertIs(instance1, instance2, "TaskAgent did not follow singleton pattern.")

if __name__ == '__main__':
    unittest.main()