import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from richarsi.beehive.workwatcher import WorkWatcher

class TestWorkWatcher(unittest.TestCase):

    @patch('richarsi.beehive.workwatcher.requests.get')
    @patch('richarsi.beehive.workwatcher.requests.put')
    def test_check_scheduled_tasks(self, mock_put, mock_get):
        # Setup mock response for GET request
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {'_id': 'task1', 'status': 'SCHEDULED'}
        ]

        # Setup workitems response
        mock_workitems_response = MagicMock()
        mock_workitems_response.status_code = 200
        mock_workitems_response.json.return_value = [
            {'status': 'IN_PROGRESS'}
        ]
        
        # Chaining the mock for second GET call
        mock_get.side_effect = [mock_get.return_value, mock_workitems_response]

        # Initialize instance and execute method
        watcher = WorkWatcher.get_instance()
        watcher.check_scheduled_tasks()

        # Assertions
        self.assertTrue(mock_put.called)
        mock_put.assert_called_with(f'{watcher.base_url}/tasks/task1', json={
            'status': 'RUNNING',
            'lastupdated': unittest.mock.ANY,
            'started': unittest.mock.ANY
        })

    @patch('richarsi.beehive.workwatcher.requests.get')
    @patch('richarsi.beehive.workwatcher.requests.put')
    def test_check_running_tasks(self, mock_put, mock_get):
        # Setup mock response for GET request
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {'_id': 'task2', 'status': 'RUNNING'}
        ]

        # Setup workitems response with all completed status
        mock_workitems_response = MagicMock()
        mock_workitems_response.status_code = 200
        mock_workitems_response.json.return_value = [
            {'status': 'COMPLETED'}, {'status': 'COMPLETED'}
        ]

        # Chaining the mock for second GET call
        mock_get.side_effect = [mock_get.return_value, mock_workitems_response]

        # Initialize instance and execute method
        watcher = WorkWatcher.get_instance()
        watcher.check_running_tasks()

        # Assertions
        self.assertTrue(mock_put.called)
        mock_put.assert_called_with(f'{watcher.base_url}/tasks/task2', json={
            'status': 'COMPLETED',
            'lastupdated': unittest.mock.ANY,
            'completed': unittest.mock.ANY
        })

    def test_singleton(self):
        # Test that only one instance is created
        instance1 = WorkWatcher.get_instance()
        instance2 = WorkWatcher.get_instance()
        self.assertIs(instance1, instance2)

if __name__ == '__main__':
    unittest.main()