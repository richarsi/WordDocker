# WordSearch Project

## Overview

Welcome to the WordSearch project! This project is a word search application that uses distributed processing to analyse strings and determine all possible words that can be made from those strings. The application is composed of multiple services running in Docker containers, leveraging modern technology stacks to provide efficient computing and a seamless user experience.

### Key Components

- **Blackboard**: Manages tasks and coordinates between different services.
- **MongoDB**: Acts as the database server for storing necessary information.
- **Website**: Frontend interface allowing users to input strings and view results.
- **WordChecker**: Service responsible for verifying word combinations.
- **WorkConsumer**: Processes scheduled tasks.
- **WorkScheduler**: Schedules new tasks.
- **WorkWatcher**: Monitors task progress and updates status.

## Prerequisites

Before you begin, ensure you have Docker and Docker Compose installed on your machine to run the application seamlessly.

## Installation and Running Instructions

Follow these steps to set up and run the WordSearch project locally:

1. **Clone the Repository**

   First, download the project files by cloning the GitHub repository:

   ```bash
   git clone <repository-url>
   ```

2. **Navigate to the Project Directory**

   Change your working directory to the project's folder:

   ```bash
   cd <project-directory>
   ```

3. **Build and Launch Services**

   Build and start all the services using Docker Compose:

   ```bash
   docker compose build
   docker compose up
   ```

4. **Check Running Containers**

   Verify all containers are up and running:

   ```bash
   docker compose ps -a
   ```

   Here you should see something similar to the output provided earlier, confirming all services are active with their respective ports.

5. **Access the Application**

   Open a web browser and navigate to [http://localhost:8080/](http://localhost:8080/) to use the application. Enter a string into the text box and click "Submit" to process it.

6. **Monitor Logs**

   Tail the logs to check if tasks are scheduled correctly:

   ```bash
   # Check if the task is scheduled successfully:
   workscheduler-1  | 2025-06-20 17:25:49,294 - root - INFO - Task 685599927736d7129267bbc6 scheduled successfully.
   ```

7. **Start WorkConsumer Service**

   To process the tasks, open a new terminal window, navigate back to the project directory, and start the `workconsumer` service:

   ```bash
   docker compose start workconsumer
   ```

   You should see confirmation:

   ```bash
   [+] Running 1/1
   ✔ Container wordsearch-workconsumer-1  Started
   ```

8. **Monitor WorkWatcher**

   The `workwatcher` service will periodically update task statuses:

   ```bash
   # Look for similar log entries:
   workwatcher-1    | 2025-06-20 17:27:49,348 - root - INFO - Checking the status of RUNNING tasks.
   ```

9. **View Results**

   Once the task completes, the website will automatically redirect to display the results. It will show a table containing all possible words derived from the entered string.

   ```bash
   website-1        | 172.19.0.1 - - [20/Jun/2025:17:28:16 +0000] "GET /status/685599927736d7129267bbc6 HTTP/1.1" 303 0 "http://localhost:8080/" ...
   ```

Enjoy using the WordSearch application! If you encounter any issues, please refer to the logs for troubleshooting.