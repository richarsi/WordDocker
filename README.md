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

3. **Build Services**

   Build the services using Docker Compose:

   ```bash
   docker compose build
   ```

4. **Run the Application in Kubernetes**

   Start all the services using Docker Kubernetes CLI:

   ```bash
   kubectl apply -f ./k8s
   ```

   The output should look something similar to the below:

   ```bash
   deployment.apps/blackboard-deployment created
   service/blackboard-service created
   deployment.apps/mongodb-deployment created
   service/mongodb-service created
   deployment.apps/website-deployment created
   service/website-service created
   deployment.apps/wordchecker-deployment created
   service/wordchecker-service created
   cronjob.batch/workconsumer-cronjob created
   deployment.apps/workscheduler created
   service/workscheduler-service created
   deployment.apps/workwatcher created
   service/workwatcher-service created
   ```

4. **Check Running Containers**

   Verify all containers are up and running:

   ```bash
   kubectl get all --show-labels
   ```

   The output should look something similar to the below:

   ```bash  
   NAME                                          READY   STATUS      RESTARTS   AGE     LABELS
   pod/blackboard-deployment-55c694b59b-thzfd    1/1     Running     0          2m15s   app=blackboard,pod-template-hash=55c694b59b
   pod/mongodb-deployment-7b6cbf5766-9sd64       1/1     Running     0          2m15s   app=mongodb,pod-template-hash=7b6cbf5766
   pod/website-deployment-5cb8dc9fb-ndxzt        1/1     Running     0          2m15s   app=website,pod-template-hash=5cb8dc9fb
   pod/wordchecker-deployment-74d47ff7b7-5xw8h   1/1     Running     0          2m15s   app=wordchecker,pod-template-hash=74d47ff7b7
   pod/wordchecker-deployment-74d47ff7b7-kzxxw   1/1     Running     0          2m15s   app=wordchecker,pod-template-hash=74d47ff7b7
   pod/wordchecker-deployment-74d47ff7b7-w25qn   1/1     Running     0          2m15s   app=wordchecker,pod-template-hash=74d47ff7b7
   pod/workconsumer-cronjob-29225766-bmlk5       0/1     Completed   0          83s     batch.kubernetes.io/controller-uid=2f747387-f7a0-456b-a302-1904e4280804,batch.kubernetes.io/job-name=workconsumer-cronjob-29225766,controller-uid=2f747387-f7a0-456b-a302-1904e4280804,job-name=workconsumer-cronjob-29225766
   pod/workconsumer-cronjob-29225767-g87dl       0/1     Completed   0          23s     batch.kubernetes.io/controller-uid=dcabf0cd-b813-463a-87ef-e71c9455fe83,batch.kubernetes.io/job-name=workconsumer-cronjob-29225767,controller-uid=dcabf0cd-b813-463a-87ef-e71c9455fe83,job-name=workconsumer-cronjob-29225767
   pod/workscheduler-6d6b88544-v2h29             1/1     Running     0          2m15s   app=workscheduler,pod-template-hash=6d6b88544
   pod/workwatcher-5dd947d78c-8pdjv              1/1     Running     0          2m15s   app=workwatcher,pod-template-hash=5dd947d78c

   NAME                            TYPE           CLUSTER-IP       EXTERNAL-IP   PORT(S)          AGE     LABELS
   service/blackboard-service      ClusterIP      10.103.115.174   <none>        8000/TCP         2m15s   app=blackboard
   service/kubernetes              ClusterIP      10.96.0.1        <none>        443/TCP          208d    component=apiserver,provider=kubernetes
   service/mongodb-service         ClusterIP      10.98.244.80     <none>        27017/TCP        2m15s   app=mongodb
   service/website-service         LoadBalancer   10.110.63.183    localhost     8080:30632/TCP   2m15s   app=website
   service/wordchecker-service     ClusterIP      10.108.116.255   <none>        8000/TCP         2m15s   app=wordchecker
   service/workscheduler-service   ClusterIP      None             <none>        <none>           2m15s   <none>
   service/workwatcher-service     ClusterIP      None             <none>        <none>           2m15s   <none>

   NAME                                     READY   UP-TO-DATE   AVAILABLE   AGE     LABELS
   deployment.apps/blackboard-deployment    1/1     1            1           2m15s   app=blackboard
   deployment.apps/mongodb-deployment       1/1     1            1           2m15s   app=mongodb
   deployment.apps/website-deployment       1/1     1            1           2m15s   app=website
   deployment.apps/wordchecker-deployment   3/3     3            3           2m15s   app=wordchecker
   deployment.apps/workscheduler            1/1     1            1           2m15s   <none>
   deployment.apps/workwatcher              1/1     1            1           2m15s   <none>

   NAME                                                DESIRED   CURRENT   READY   AGE     LABELS
   replicaset.apps/blackboard-deployment-55c694b59b    1         1         1       2m15s   app=blackboard,pod-template-hash=55c694b59b
   replicaset.apps/mongodb-deployment-7b6cbf5766       1         1         1       2m15s   app=mongodb,pod-template-hash=7b6cbf5766
   replicaset.apps/website-deployment-5cb8dc9fb        1         1         1       2m15s   app=website,pod-template-hash=5cb8dc9fb
   replicaset.apps/wordchecker-deployment-74d47ff7b7   3         3         3       2m15s   app=wordchecker,pod-template-hash=74d47ff7b7
   replicaset.apps/workscheduler-6d6b88544             1         1         1       2m15s   app=workscheduler,pod-template-hash=6d6b88544
   replicaset.apps/workwatcher-5dd947d78c              1         1         1       2m15s   app=workwatcher,pod-template-hash=5dd947d78c

   NAME                                 SCHEDULE    TIMEZONE   SUSPEND   ACTIVE   LAST SCHEDULE   AGE     LABELS
   cronjob.batch/workconsumer-cronjob   * * * * *   <none>     False     0        23s             2m15s   <none>

   NAME                                      STATUS     COMPLETIONS   DURATION   AGE   LABELS
   job.batch/workconsumer-cronjob-29225766   Complete   1/1           8s         83s   batch.kubernetes.io/controller-uid=2f747387-f7a0-456b-a302-1904e4280804,batch.kubernetes.io/job-name=workconsumer-cronjob-29225766,controller-uid=2f747387-f7a0-456b-a302-1904e4280804,job-name=workconsumer-cronjob-29225766
   job.batch/workconsumer-cronjob-29225767   Complete   1/1           7s         23s   batch.kubernetes.io/controller-uid=dcabf0cd-b813-463a-87ef-e71c9455fe83,batch.kubernetes.io/job-name=workconsumer-cronjob-29225767,controller-uid=dcabf0cd-b813-463a-87ef-e71c9455fe83,job-name=workconsumer-cronjob-29225767
   ```

5. **Access the Application**

   Open a web browser and navigate to [http://localhost:8080/](http://localhost:8080/) to use the application. Enter a string into the text box and click "Submit" to process it.  Because this application is based on a job scheduler which only polls every 30s it may take some time before you see text below the text field, as shown below:

   ```bash
   Last Updated: 2025-07-26T16:16:19.793000
   ```

6. **Monitor WorkScheduler**

   The `WorkScheduler` service will periodically update task statuses. Tail the logs to check if the task you have submitted has been scheduled correctly.

   ```bash
   # Identify the name of the workscheduler pod
   kubectl get pod --selector="app=workscheduler"
   NAME                            READY   STATUS    RESTARTS   AGE
   workscheduler-6d6b88544-v2h29   1/1     Running   0          7m50s
   # Tail the logs from the pod
   kubectl logs pod/workscheduler-6d6b88544-v2h29 --follow
   ```

   The output will show the task being scheduled.

   ```bash
   Defaulted container "workscheduler" out of: workscheduler, wait-for-blackboard (init)
   2025-07-26 16:14:19,651 - root - INFO - Starting Task Agent...
   2025-07-26 16:14:49,661 - root - INFO - No tasks to process … just loop
   2025-07-26 16:15:19,674 - root - INFO - No tasks to process … just loop
   2025-07-26 16:15:49,695 - root - INFO - No tasks to process … just loop
   2025-07-26 16:16:19,795 - root - INFO - Task 6884ff4ff1e57d12f85767dd scheduled successfully.
   2025-07-26 16:07:49,491 - root - INFO - No tasks to process … just loop
   2025-07-26 16:16:49,810 - root - INFO - No tasks to process … just loop
   ```

7. **Monitor WorkWatcher**

   The `WorkWatcher` service will periodically update task statuses:

   ```bash
   # Identify the name of the workwatcher pod
   kubectl get pod --selector="app=workwatcher"  
   NAME                           READY   STATUS    RESTARTS   AGE
   workwatcher-5dd947d78c-8pdjv   1/1     Running   0          19m
   # Tail the logs from the pod
   kubectl logs pod/workwatcher-5dd947d78c-8pdjv --follow
   ```

   The output will show the `WorkWatcher` checking for scheduled and running tasks.

   ```bash
   Defaulted container "workwatcher" out of: workwatcher, wait-for-blackboard (init)
   2025-07-26 16:05:50,499 - root - INFO - Starting Watcher...
   2025-07-26 16:06:50,515 - root - INFO - Checking the status of SCHEDULED tasks.
   2025-07-26 16:06:50,528 - root - INFO - Checking the status of RUNNING tasks.
   2025-07-26 16:07:50,558 - root - INFO - Checking the status of SCHEDULED tasks.
   2025-07-26 16:07:50,570 - root - INFO - Checking the status of RUNNING tasks.
   2025-07-26 16:08:50,594 - root - INFO - Checking the status of SCHEDULED tasks.
   ```

8. **Monitor Website**

   The `Website` runs on an `NGINX` image and by examining logs you can monitor client requests from the browser and the service responses.

   ```bash
   # Identify the name of the website pod
   kubectl get pod --selector="app=website"    
   NAME                                 READY   STATUS    RESTARTS   AGE
   website-deployment-5cb8dc9fb-ndxzt   1/1     Running   0          32m
   # Tail the logs from the pod
   kubectl logs pod/website-deployment-5cb8dc9fb-ndxzt --follow
   ```

   Once a request has been submitted the client will poll the server for status updates.  The below shows the initial loading of the website in the client's browser; then a `POST` request resulting in a http-202 response; and this is followed 5s later with the first poll for a status update.

   ```bash
   192.168.65.3 - - [26/Jul/2025:16:14:59 +0000] "GET / HTTP/1.1" 304 0 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
   192.168.65.3 - - [26/Jul/2025:16:16:15 +0000] "POST /tasks HTTP/1.1" 202 0 "http://localhost:8080/" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
   192.168.65.3 - - [26/Jul/2025:16:16:20 +0000] "GET /status/6884ff4ff1e57d12f85767dd HTTP/1.1" 200 45 "http://localhost:8080/" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
   ```

   Once the results are available the next poll will result in a redirect http-303 to the the results:

   ```bash
   192.168.65.3 - - [26/Jul/2025:16:31:55 +0000] "GET /status/688502923f3cd397d469f924 HTTP/1.1" 303 0 "http://localhost:8080/" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
   192.168.65.3 - - [26/Jul/2025:16:31:55 +0000] "GET /tasks/688502923f3cd397d469f924/words HTTP/1.1" 200 795 "http://localhost:8080/" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"   
   ```

9. **View Results**
   
   Once the task completes, the website will automatically redirect to display the results. It will show a table containing all possible words derived from the entered string.

Enjoy using the WordSearch application! If you encounter any issues, please refer to the logs for troubleshooting.