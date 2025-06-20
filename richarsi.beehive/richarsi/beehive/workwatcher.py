import os
import requests
import time
from datetime import datetime
import schedule
import logging

WORKWATCHER_LOG_LEVEL = os.getenv('WORKWATCHER_LOG_LEVEL', 'INFO').upper()
# Convert the string representation of the log level to a numeric value
log_level = getattr(logging, WORKWATCHER_LOG_LEVEL, logging.INFO)
# Set up the logger
logging.basicConfig(
    level=log_level,  # Set log level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Output logs to the console (stdout)
    ]
)

# TODO use the threadsafe approach that the workscheduler used to create a singleton.
class WorkWatcher:
    _instance = None
    
    @staticmethod
    def get_instance():
        if WorkWatcher._instance is None:
            WorkWatcher()
        return WorkWatcher._instance
    
    def __init__(self):
        if WorkWatcher._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            WorkWatcher._instance = self
        self.blackboard_host = os.getenv('BLACKBOARD_HOST', 'blackboard')
        self.blackboard_port = os.getenv('BLACKBOARD_PORT', '8000')
        self.base_url = f"http://{self.blackboard_host}:{self.blackboard_port}"
        self.poll_time = int(os.getenv('WORKWATCHER_POLLTIME', 60))

    def check_scheduled_tasks(self):
        logging.info("Checking the status of SCHEDULED tasks.")
        try:
            response = requests.get(f"{self.base_url}/tasks", params={'status': 'SCHEDULED'})
            
            if response.status_code in [200, 404]:
                tasks = response.json() if response.status_code == 200 else []
                for task in tasks:
                    task_id = task['_id']
                    workitems_response = requests.get(f"{self.base_url}/tasks/{task_id}/workitems")
                    
                    if workitems_response.status_code in [200, 404]:
                        workitems = workitems_response.json() if workitems_response.status_code == 200 else []
                        for workitem in workitems:
                            if workitem['status'] != 'NEW':
                                update_data = {
                                    'status': 'RUNNING',
                                    'lastupdated': datetime.now().isoformat(),
                                    'started': datetime.now().isoformat()
                                }
                                put_response = requests.put(f"{self.base_url}/tasks/{task_id}", json=update_data)
                                if put_response.status_code != 200:
                                    logging.error(f"Failed to update task {task_id}. Error: {put_response.text}")
                                break
                    else:
                        logging.error(f"Error retrieving workitems for task {task_id}: {workitems_response.status_code} - {workitems_response.text}")
            else:
                logging.error(f"Error retrieving scheduled tasks: {response.status_code} - {response.text}")
        
        except requests.exceptions.RequestException as e:
            logging.error(f"An error occurred: {str(e)}")

    def check_running_tasks(self):
        logging.info("Checking the status of RUNNING tasks.")
        try:
            response = requests.get(f"{self.base_url}/tasks", params={'status': 'RUNNING'})
            
            if response.status_code in [200, 404]:
                tasks = response.json() if response.status_code == 200 else []
                for task in tasks:
                    task_id = task['_id']
                    workitems_response = requests.get(f"{self.base_url}/tasks/{task_id}/workitems")
                    
                    if workitems_response.status_code == 200:
                        workitems = workitems_response.json()
                        all_completed = all(workitem['status'] == 'COMPLETED' for workitem in workitems)
                        
                        if all_completed:
                            update_data = {
                                'status': 'COMPLETED',
                                'lastupdated': datetime.now().isoformat(),
                                'completed': datetime.now().isoformat()
                            }
                            put_response = requests.put(f"{self.base_url}/tasks/{task_id}", json=update_data)
                            if put_response.status_code != 200:
                                logging.error(f"Failed to update task {task_id}. Error: {put_response.text}")
                    else:
                        logging.error(f"Error retrieving workitems for task {task_id}: {workitems_response.status_code} - {workitems_response.text}")
            else:
                logging.error(f"Error retrieving running tasks: {response.status_code} - {response.text}")
        
        except requests.exceptions.RequestException as e:
            logging.error(f"An error occurred: {str(e)}")

    def poll_tasks(self):
        self.check_scheduled_tasks()
        self.check_running_tasks()

def main():
    watcher = WorkWatcher.get_instance()
    # Schedule the job at regular intervals based on `poll_time`
    schedule.every(watcher.poll_time).seconds.do(watcher.poll_tasks)

    logging.info("Starting Watcher...") 
    while True:
        schedule.run_pending()
        time.sleep(1)  # Wait for a short period to prevent high CPU usage

if __name__ == "__main__":
    main()