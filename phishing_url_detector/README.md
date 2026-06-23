# PhishGuard AI - Phishing URL and Email Detector

PhishGuard AI is a multi-modal security system designed to detect and prevent phishing attacks. It leverages advanced Machine Learning techniques alongside heuristic rules, domain intelligence analysis (WHOIS), and a real-time web crawler utilizing behavioral analysis to score and classify URLs and e-mails as either Legitimate or Phishing.

## Features

- **Multi-Modal Detection**: Processes both suspicious URLs and suspicious email contents to analyze potential threats.
- **Machine Learning Models**: Employs deep learning (Multi-Head Self-Attention layers) via TensorFlow/Keras to analyze text and structures.
- **Hybrid Scoring**: Combines results from:
  - **AI Transformer Models**: Trained on a large dataset of emails and URLs.
  - **WHOIS Domain Checks**: Evaluates domain age, registration details, and expiration.
  - **Crawler Analysis**: Analyzes HTML content, checks for malicious scripts, and reviews website forms in real-time.
- **Reporting System**: Generate and download detailed PDF security reports summarizing findings, risk assessments, and final safety scores.
- **History Tracker**: Maintains a record of the last 50 scans executed by the user.

## Prerequisites

Before running the application, make sure you have the following installed:

- Python 3.8+
- Node.js (Optional, if frontend tools are expanded later)

It's highly recommended to use a Python virtual environment to install your dependencies to avoid conflicts.

## Installation

1. **Navigate to the Project Directory** (if not already there):

    ```bash
    cd "phishing_url_detector"
    ```

2. **Create a Virtual Environment (Optional but Recommended)**:

    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate
    ```

3. **Install the Requirements**:

    Install all required Python packages using `pip`:

    ```bash
    pip install -r requirements.txt
    ```

    Note: This will install core components like `Flask`, `tensorflow`, `scikit-learn`, `selenium`, `beautifulsoup4`, `python-whois`, etc.

## Setup & Training (Optional if models exist)

The models (`email_model.h5`, `phishing_model.h5`, and their vectorizers) are stored in the `/models/` folder. If they are missing or if you want to rebuild them on your machine:

1. Look in the `Phishing URL dataset` directory to ensure dataset CSVs are present.
2. Run the `train_model.py` script:

    ```bash
    python train_model.py
    ```

This script trains both the email classifier and the URL classifier, creates TF-IDF vectorizers, and saves the models and performance metrics into the `models/` directory.

## Execution Steps

Once the environment is set up and the required models exist, follow these steps to execute the web portal:

1. **Run the Flask Application**:

    ```bash
    python app.py
    ```

2. **Access the Web Interface**:

    Open your web browser and navigate to:

    ```
    http://localhost:5000
    ```

3. **Use the Application**:

    - **Input Data**: Enter a suspicious URL (e.g., `http://example.com/login`) or paste an email's text content.
    - **Analyze**: Click the scan button. The tool will automatically detect if it is a URL or Email and start evaluating through machine learning models, WHOIS metrics, and a web crawler.
    - **View Results**: A breakdown of the risk score, behavioral findings, legitimacy flags, and overall verdict will be returned.
    - **Download Report**: You can download a PDF of the results by selecting "Download Report" after the scan is finalized.

## Architecture

- **`app.py`**: The main Flask backend application routing endpoints, generating PDF reports, and triggering predictions.
- **`model_utils.py`**: Contains functions like `predict_url`, `predict_email`, `predict_smart` to interface with the trained AI models.
- **`crawler.py`**: Houses the logic that drives Selenium/BeautifulSoup to visit URLs dynamically and scrape signs of malice or credibility.
- **`domain_info.py`**: Interacts with the `python-whois` library to collect risk profiles regarding the domain registrar and registration dates.
- **`train_model.py`**: The module that loads local datasets (`Phishing URLs.csv`, `Legitimate URLs.csv`), preprocesses strings through TF-IDF, trains Sequential Neural Networks, and serialized components to disk using Joblib.

## Troubleshooting

- **Models Not Loading**: Ensure `python train_model.py` completes fully. Also verify your TensorFlow version matches the version used to compile the `.h5` files. Run `pip install tensorflow==2.15.0`.
- **Crawler/WebDriver Failures**: The `selenium` module requires `webdriver-manager` to fetch matching Chrome tools. Make sure you have Google Chrome installed on your operating system.
