document.addEventListener('DOMContentLoaded', function () {
    checkCurrentTab();

    document.getElementById('checkBtn').addEventListener('click', function () {
        checkCurrentTab();
    });
});

function checkCurrentTab() {
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = '<p class="loading">Analyzing...</p>';

    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        const currentUrl = tabs[0].url;

        // Call Flask API
        fetch(`http://127.0.0.1:5000/api/check_url?url=${encodeURIComponent(currentUrl)}`)
            .then(response => response.json())
            .then(data => {
                if (data.prediction === 'Phishing') {
                    resultDiv.innerHTML = `
            <div id="status" class="phishing">
              WARNING: PHISHING DETECTED
              <span id="score">${data.confidence}% Risk</span>
            </div>
            <p>This site detects as malicious.</p>
          `;
                } else {
                    resultDiv.innerHTML = `
            <div id="status" class="safe">
              WEBSITE IS SAFE
              <span id="score">${data.confidence}% Risk</span>
            </div>
            <p>No phishing indicators found.</p>
          `;
                }
            })
            .catch(error => {
                resultDiv.innerHTML = `<p style="color:red">Error connecting to server. Is Flask app running?</p>`;
                console.error('Error:', error);
            });
    });
}
