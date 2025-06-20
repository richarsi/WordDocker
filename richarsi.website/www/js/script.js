const submitBtn = document.getElementById('submit-btn');
let pendingRequest = false;
let pollInterval = null;

const protocol = window.location.protocol; // e.g., 'http:' or 'https:'
const host = window.location.hostname;     // e.g., 'localhost' or any domain
const port = window.location.port;         // e.g., '8000', if specified

const base_url = `${protocol}//${host}${port ? ':' + port : ''}`;
const tasks_url = `${protocol}//${host}${port ? ':' + port : ''}/tasks`;

submitBtn.addEventListener('click', async () => {
    const input = document.getElementById('word-input').value.trim();
    
    if (!/^[A-Za-z]+$/.test(input)) {
        showError("Input must contain only alphabetic characters.");
        return;
    }

    if (pendingRequest) {
        alert("Another request is still being processed. Please wait.");
        return;
    }

    clearError();
    clearResults();
    const payload = { letters: input.toLowerCase() };

    try {
        const response = await fetch(tasks_url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (response.status === 202) {
            pendingRequest = true;
            const location = response.headers.get('Location');
            pollStatus(`${base_url}${location}`);
        } else {
            handleErrorResponse(response);
        }
    } catch (error) {
        showError("Failed to connect to the server.");
    }
});

function pollStatus(statusUrl) {
    const pollInterval = setInterval(async () => {
        console.log(`Polling status at: ${statusUrl}`);

        try {
            const response = await fetch(statusUrl);

            // Check if the response is successful
            if (response.ok) {
                const data = await response.json();
                
                // First check if the status property exists
                if ('status' in data && data.status === "COMPLETED") {
                    clearInterval(pollInterval);
                    console.log("Operation completed. Stopping polling.");
                    
                    // Display the results from the redirect payload
                    displayResults(data);
                    // Allow another request to be submitted 
                    pendingRequest = false;
                } 
                // Then check if the lastUpdated property exists
                else if ('lastUpdated' in data) {
                    // Handle status payload with lastUpdated time
                    document.getElementById('last-updated').innerText = `Last Updated: ${data.lastUpdated}`;
                    console.log("Status updated:", data.lastUpdated);
                }
                // If neither status nor lastUpdated are present
                else {
                    throw new Error("Unexpected response structure.");
                }
            } else {
                throw new Error(`Unexpected response status: ${response.status}`);
            }
        } catch (error) {
            console.error("Error during polling:", error);
            showError("Polling failed due to a connection error.");
            clearInterval(pollInterval);
        }
    }, 5000);
}

function displayResults(data) {
    const wordCount = data.words.length;
    const elapsedTime = (new Date(data.completed) - new Date(data.started)) / 1000;

    const tableBody = document.getElementById('results-body');
    const row = `<tr>
                    <td>${wordCount}</td>
                    <td>${elapsedTime.toFixed(2)}</td>
                    <td>${data.words.join(', ')}</td>
                 </tr>`;
    tableBody.innerHTML = row;
    document.getElementById('results-table').style.display = '';
}

function handleErrorResponse(response) {
    response.text().then(text => {
        showError(`Error ${response.status}: ${text}`);
    });
}

function showError(message) {
    document.getElementById('error-message').innerText = message;
}

function clearError() {
    document.getElementById('error-message').innerText = '';
}

function clearResults() {
    document.getElementById('results-body').innerHTML = '';
    document.getElementById('results-table').style.display = 'none';
    document.getElementById('last-updated').innerText = '';
}
