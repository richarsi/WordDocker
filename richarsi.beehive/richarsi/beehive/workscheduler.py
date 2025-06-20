import os
import requests
import schedule
import time
from datetime import datetime, timezone
from threading import Lock
import logging

WORKSCHEDULER_LOG_LEVEL = os.getenv('WORKSCHEDULER_LOG_LEVEL', 'INFO').upper()
# Convert the string representation of the log level to a numeric value
log_level = getattr(logging, WORKSCHEDULER_LOG_LEVEL, logging.INFO)
# Set up the logger
logging.basicConfig(
    level=log_level,  # Set log level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Output logs to the console (stdout)
    ]
)
class SingletonMeta(type):
    """
    A thread-safe implementation of Singleton pattern using a metaclass.
    
    This ensures that only one instance of a class exists throughout the application.
    """

    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        """
        Controls the instantiation of instances to ensure a single instance.

        Returns:
            The single instance of the class.
        """
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]

class TaskAgent(metaclass=SingletonMeta):
    """
    Agent responsible for fetching, processing, and updating tasks on a blackboard server.
    """
    BLACKBOARD_HOST = os.getenv('BLACKBOARD_HOST', 'localhost')
    BLACKBOARD_PORT = os.getenv('BLACKBOARD_PORT', '8000')
    BASE_URL = f'http://{BLACKBOARD_HOST}:{BLACKBOARD_PORT}/tasks'

    def __init__(self):
        """
        Initializes a TaskAgent instance with an HTTP session for persistent connections.
        """
        self.session = requests.Session()

    def fetch_new_tasks(self):
        """
        Fetches new tasks from the server with status NEW.

        Returns:
            list: A list of tasks or an empty list if no tasks are found.
        """
        response = self.session.get(f'{self.BASE_URL}?status=NEW')

        if response.status_code == 404:
            logging.info("No tasks to process … just loop")
            return []

        if response.status_code != 200:
            logging.info(f"Error fetching tasks: {response.status_code}")
            return []

        try:
            tasks = response.json()
        except ValueError as e:
            logging.info(f"Error decoding JSON: {str(e)}")
            return []

        return tasks

    def update_task_status(self, task_id, status):
        """
        Updates the status of a specified task.

        Args:
            task_id (str): The ID of the task to update.
            status (str): The new status to set for the task.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        url = f'{self.BASE_URL}/{task_id}'
        payload = {
            "status": status,
            "lastUpdated": datetime.now(timezone.utc).isoformat()
        }
        response = self.session.put(url, json=payload)
        return response.status_code == 200

    def send_workitems(self, task_id, letters):
        """
        Sends work items corresponding to a given task ID.

        Args:
            task_id (str): The ID of the task for which to send work items.
            letters (str): Letters associated with the task.

        Returns:
            bool: True if sending work items was successful, False otherwise.
        """
        url = f'{self.BASE_URL}/{task_id}/workitems'
        workitems = [{
            "current_sequence": "",
            "remaining_elements": letters
        }]

        payload = {"workitems": workitems}
        response = self.session.post(url, json=payload)
        return response.status_code == 200

    def process_tasks(self):
        """
        Processes tasks by fetching new ones, setting their status, and sending work items.
        """
        tasks = self.fetch_new_tasks()

        for task in tasks:
            task_id = task["_id"]
            letters = task["letters"]

            if not self.update_task_status(task_id, "SCHEDULING"):
                continue

            if not self.send_workitems(task_id, letters):
                continue

            payload = {
                "status": "SCHEDULED",
                "lastUpdated": datetime.now(timezone.utc).isoformat(),
                "scheduled_items_count": 1
            }
            url = f'{self.BASE_URL}/{task_id}'
            response = self.session.put(url, json=payload)

            if response.status_code == 200:
                logging.info(f"Task {task_id} scheduled successfully.")
            else:
                logging.info(f"Failed to update task {task_id} to SCHEDULED.")

def job():
    """
    Scheduled job to create a TaskAgent instance and process tasks.
    """
    agent = TaskAgent()
    agent.process_tasks()

if __name__ == "__main__":
    # Get poll time from environment variable or default to 60 seconds
    poll_time = int(os.getenv('WORKSCHEDULER_POLLTIME', 60))

    # Schedule the job to run based on poll time
    schedule.every(poll_time).seconds.do(job)

    logging.info("Starting Task Agent...")
    while True:
        schedule.run_pending()
        time.sleep(1)  # Sleep to prevent high CPU usage
