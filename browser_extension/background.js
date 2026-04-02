// Background script to monitor tabs and update icon
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && tab.url.startsWith('http')) {

        // Call Flask API
        fetch(`http://127.0.0.1:5000/api/check_url?url=${encodeURIComponent(tab.url)}`)
            .then(response => response.json())
            .then(data => {
                if (data.prediction === 'Phishing') {
                    // Set Badge to Red '!'
                    chrome.action.setBadgeText({ text: "!", tabId: tabId });
                    chrome.action.setBadgeBackgroundColor({ color: "#FF0000", tabId: tabId });

                    // Optional: Inject alert
                    chrome.scripting.executeScript({
                        target: { tabId: tabId },
                        function: () => {
                            alert("⚠️ WARNING: Phishing Detector has identified this site as potentially malicious!");
                        }
                    });

                } else {
                    // Set Badge to Green 'OK' or clear it
                    chrome.action.setBadgeText({ text: "OK", tabId: tabId });
                    chrome.action.setBadgeBackgroundColor({ color: "#00FF00", tabId: tabId });
                }
            })
            .catch(err => console.log("Server not reachable"));
    }
});
