FROM python:3.13.3-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY richarsi/ richarsi/

EXPOSE 8000

# Start the application using Gunicorn, a Python WSGI HTTP server for UNIX
# Set the number of worker processes for handling requests to 3
# Bind the application to listen on all interfaces (0.0.0.0) at port 8000
# Set the maximum number of seconds to wait for a worker before timeout to 60
# Specify the application module and variable to run (richarsi.permutations.app:app)
CMD ["gunicorn", "-w 3", "-b 0.0.0.0:8000", "-t 60", "richarsi.blackboard.app:app"]