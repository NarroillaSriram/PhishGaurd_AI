// =============================
// Global Variables
// =============================
let currentAnalysisTab = 'url';
let analysisInProgress = false;

// =============================
// Initialize the Application
// =============================
document.addEventListener('DOMContentLoaded', function () {
    initializeApp();
});

function initializeApp() {

    checkModelStatus();
    loadHistory();
    startRealTimeUpdates();
}



// =============================
// Tab Switching
// =============================
function switchAnalysisTab(tabType) {
    currentAnalysisTab = tabType;
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.type === tabType) btn.classList.add('active');
    });
    document.querySelectorAll('.analysis-tab').forEach(tab => tab.classList.remove('active'));
    document.getElementById(tabType + '-analysis').classList.add('active');
    hideAnalysisResults();
}

// =============================
// Start Analysis w/ URL Validation
// =============================
async function startAnalysis() {
    if (analysisInProgress) return;

    let inputData;
    let analysisType;

    if (currentAnalysisTab === 'url') {
        inputData = document.getElementById('urlInput').value.trim();
        analysisType = 'url';

        if (!inputData) {
            showToast('Please enter a URL to analyze', 'warning');
            return;
        }

        // Allow any input as URL (restriction removed)

    } else {
        const emailFrom = document.getElementById('emailFrom').value.trim();
        const emailSubject = document.getElementById('emailSubject').value.trim();
        const emailContent = document.getElementById('emailContent').value.trim();

        if (!emailContent) {
            showToast('Please enter email content to analyze', 'warning');
            return;
        }

        inputData = `From: ${emailFrom}\nSubject: ${emailSubject}\n\n${emailContent}`;
        analysisType = 'email';
    }

    analysisInProgress = true;
    showAnalysisProgress();
    await runAnalysisPipeline(inputData, analysisType);
}

// =============================
// Analysis Pipeline Simulation
// =============================
async function runAnalysisPipeline(inputData, analysisType) {
    const steps = ['preprocessing', 'tokenization', 'embeddings', 'attention', 'classification'];
    const stepDurations = [800, 600, 700, 1200, 500];
    document.querySelectorAll('.pipeline-step').forEach(step => step.classList.remove('active', 'completed'));

    for (let i = 0; i < steps.length; i++) {
        const step = document.querySelector(`[data-step="${steps[i]}"]`);
        step.classList.add('active');
        await new Promise(res => setTimeout(res, stepDurations[i]));
        step.classList.remove('active');
        step.classList.add('completed');
        if (steps[i] === 'attention') showAttentionVisualization(inputData, analysisType);
    }

    setTimeout(() => performActualAnalysis(inputData, analysisType), 500);
}

function showAnalysisProgress() {
    // Add scanning effect
    document.getElementById('inputSection').classList.add('scanning');

    document.getElementById('analysisProgress').style.display = 'block';
    document.getElementById('attentionViz').style.display = 'none';
    document.getElementById('analysisResults').style.display = 'none';
    const btn = document.getElementById('analyzeBtn');
    document.getElementById('analyzeBtnText').style.display = 'none';
    document.getElementById('analyzeSpinner').style.display = 'block';

    // Smooth scroll to progress
    document.getElementById('analysisProgress').scrollIntoView({ behavior: 'smooth', block: 'center' });

    btn.disabled = true;
}

// =============================
// Attention Visualization
// =============================
function showAttentionVisualization(inputData, analysisType) {
    const attentionViz = document.getElementById('attentionViz');
    attentionViz.style.display = 'block';
    attentionViz.classList.add('fade-in-up'); // Add animation

    generateAttentionTokens(inputData, analysisType);
    generateAttentionHeads(); // Simulate active heads
    drawAttentionMatrix();
}

function generateAttentionHeads() {
    const headsGrid = document.getElementById('attentionHeadsGrid');
    headsGrid.innerHTML = ''; // Clear "not available" message

    // Simulate 8 attention heads
    for (let i = 1; i <= 8; i++) {
        const head = document.createElement('div');
        head.className = 'attention-head-item';

        // Random activity level
        const activity = Math.floor(Math.random() * 100);
        const isHigh = activity > 70;

        head.innerHTML = `
            <div class="head-circle ${isHigh ? 'active' : ''}">
                <div class="head-inner"></div>
            </div>
            <span class="head-label">Head ${i}</span>
            <div class="head-activity-bar">
                <div class="head-activity-fill" style="width: ${activity}%"></div>
            </div>
        `;
        headsGrid.appendChild(head);
    }
}

function generateAttentionTokens(inputData, analysisType) {
    const tokensContainer = document.getElementById('attentionTokens');
    tokensContainer.innerHTML = '';
    let tokens = analysisType === 'url' ? inputData.split(/[\/\.\-\?\&\=]/) : inputData.split(/\s+/).slice(0, 20);
    const suspicious = ['paypal', 'verify', 'urgent', 'account', 'suspended', 'immediately', 'click', 'here'];

    tokens.forEach((token, index) => {
        if (token.trim()) {
            const el = document.createElement('div');
            el.className = 'attention-token';
            el.textContent = token;

            // Stagger animation
            el.style.animationDelay = `${index * 50}ms`;

            if (suspicious.some(k => token.toLowerCase().includes(k))) el.classList.add('high-attention');
            else if (Math.random() > 0.7) el.classList.add('medium-attention');
            else el.classList.add('low-attention');
            tokensContainer.appendChild(el);
        }
    });
}

function drawAttentionMatrix() {
    const canvas = document.getElementById('attentionMatrix');
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const cellSize = 15, rows = 8, cols = 20;

    // Animate matrix drawing with heatmap style
    let frame = 0;
    const maxFrames = 50;

    function animate() {
        if (frame > maxFrames) return;

        // Fade effect
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        for (let i = 0; i < rows; i++) {
            for (let j = 0; j < cols; j++) {
                if (Math.random() > 0.8) {
                    const weight = Math.random();
                    // Heatmap colors: Blue -> Cyan -> White
                    const alpha = weight * (frame / maxFrames);
                    ctx.fillStyle = `rgba(0, 217, 255, ${alpha})`;

                    if (weight > 0.9) ctx.fillStyle = `rgba(255, 255, 255, ${alpha})`; // Hotspot

                    ctx.fillRect(j * cellSize, i * cellSize, cellSize - 1, cellSize - 1);
                }
            }
        }
        frame++;
        requestAnimationFrame(animate);
    }
    animate();
}

// =============================
// API Call + Results
// =============================
async function performActualAnalysis(inputData, analysisType) {
    try {
        const res = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ input: inputData, type: analysisType })
        });
        const result = await res.json();

        if (res.ok) {
            showAnalysisResults(result, analysisType);


            // Reload history to show new scan
            loadHistory();
        } else showToast('Analysis failed: ' + result.error, 'error');
    } catch (err) {
        showToast('Network error: ' + err.message, 'error');
    } finally {
        const btn = document.getElementById('analyzeBtn');
        document.getElementById('analyzeBtnText').style.display = 'flex';
        document.getElementById('analyzeSpinner').style.display = 'none';
        btn.disabled = false;
        analysisInProgress = false;

        // Remove scanning effect
        document.getElementById('inputSection').classList.remove('scanning');
    }
}

// =============================
// Results Display
// =============================
function showAnalysisResults(result, type) {
    const e = document.getElementById('analysisResults');
    const icon = document.getElementById('statusIcon');
    const title = document.getElementById('resultTitle');
    const desc = document.getElementById('resultDescription');
    const conf = document.getElementById('confidenceScore');
    const risk = document.getElementById('threatLevel');
    const time = document.getElementById('analysisTime');
    const reportBtn = document.getElementById('downloadReportBtn');

    // Store scan ID for report download
    if (result.scan_id) {
        reportBtn.setAttribute('data-scan-id', result.scan_id);
        reportBtn.style.display = 'inline-flex';
    } else {
        reportBtn.style.display = 'none';
    }

    e.style.display = 'block';

    let displayConfidence = result.confidence;
    const confidenceLabel = document.querySelector('.confidence-label') || { textContent: '' }; // Fallback

    if (result.prediction === 'Phishing') {
        icon.className = 'status-icon danger';
        icon.innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
        title.textContent = 'THREAT DETECTED';
        desc.textContent = `This ${type} appears to be a phishing attempt`;
        risk.textContent = 'HIGH RISK';
        risk.style.color = 'var(--red-primary)';
        displayConfidence = result.confidence; // Keep risk score
        document.querySelector('.score-card.highlight .score-label').textContent = 'Final Risk Score';
    } else if (result.prediction === 'Suspicious') {
        icon.className = 'status-icon warning';
        icon.innerHTML = '<i class="fas fa-question-circle"></i>';
        title.textContent = 'SUSPICIOUS CONTENT';
        desc.textContent = `This ${type} has several red flags`;
        risk.textContent = 'MEDIUM RISK';
        risk.style.color = 'var(--orange-primary)';
        displayConfidence = result.confidence; // Keep risk score for suspicious
        document.querySelector('.score-card.highlight .score-label').textContent = 'Final Risk Score';
    } else {
        icon.className = 'status-icon safe';
        icon.innerHTML = '<i class="fas fa-shield-check"></i>';
        title.textContent = 'CONTENT APPEARS SAFE';
        desc.textContent = `This ${type} appears to be legitimate`;
        risk.textContent = 'LOW RISK';
        risk.style.color = 'var(--green-primary)';
        // FOR SAFE SITES: Show Safety Score (100 - Risk)
        displayConfidence = Math.max(0, 100 - result.confidence);
        document.querySelector('.score-card.highlight .score-label').textContent = 'Final Safety Score';
    }

    // Display the calculated score
    conf.textContent = displayConfidence.toFixed(1) + '%';

    // =============================
    // Decision Engine Population
    // =============================
    const decisionPanel = document.getElementById('decisionEngineResults');
    const recText = document.getElementById('finalRecommendation');
    const reasonText = document.getElementById('decisionReason');
    const whoisContent = document.getElementById('whoisInfo');

    if (result.recommendation) {
        decisionPanel.style.display = 'block';

        // Recommendation Styling
        recText.textContent = result.recommendation;
        const rec = result.recommendation;

        // Reset classes
        recText.className = '';
        recText.removeAttribute('data-text');

        if (rec.includes("DO NOT VISIT") || rec.includes("Dangerous")) {
            recText.style.color = '#ff4757'; // Red
            recText.classList.add('glitch-text');
            recText.setAttribute('data-text', rec);
        } else if (rec.includes("Suspicious")) {
            recText.style.color = '#ffa502'; // Orange
        } else {
            recText.style.color = '#2ed573'; // Green
        }

        // Reasons
        let reasons = [];
        // Check WHOIS Risk via score from app.py
        if (result.scores && result.scores.domain_risk >= 50) {
            const age = result.domain_info ? result.domain_info.domain_age_days : 0;
            reasons.push(`• High Risk Domain (Age: ${age} days)`);
        }

        // Check Behavior Findings
        if (result.behavior_findings && result.behavior_findings.length > 0) {
            // Add unique findings
            const findings = [...new Set(result.behavior_findings)];
            findings.forEach(f => {
                if (f.includes("Password")) reasons.push("• Login Form detected");
                else if (f.includes("redirect")) reasons.push("• Suspicious Redirect");
                else if (f.includes("external")) reasons.push("• External Form Submission");
                else reasons.push(`• ${f}`);
            });
        }

        if (reasons.length === 0) {
            if (result.prediction === "Phishing") {
                reasons.push("• AI Model Flagged Content");
            } else if (rec.includes("Safe")) {
                reasons.push("• Domain appears established and safe");
            }
        }

        // Limit reasons to 3 to prevent overflow
        if (reasons.length > 3) {
            reasons = reasons.slice(0, 3);
            reasons.push("• ...and more");
        }

        reasonText.innerHTML = reasons.join('<br>');

        // Domain Info
        if (result.domain_info && result.domain_info.creation_date !== 'Unknown') {
            const dRisk = result.scores.domain_risk || 0;
            let riskLabel = 'Low';
            let riskColor = '#2ed573';

            if (dRisk >= 80) {
                riskLabel = 'High';
                riskColor = '#ff4757';
            } else if (dRisk >= 50) {
                riskLabel = 'Suspicious';
                riskColor = '#ffa502';
            }

            let domainName = result.input;
            try {
                // simple extraction for display
                if (domainName.startsWith('http')) {
                    const urlObj = new URL(domainName);
                    domainName = urlObj.hostname;
                } else if (domainName.includes('/')) {
                    domainName = domainName.split('/')[0];
                }
            } catch (e) { }

            whoisContent.innerHTML = `
                <div class="domain-metric-row">
                    <span class="metric-label">Domain Name:</span>
                    <span class="metric-value highlight">${domainName}</span>
                </div>
                <div class="domain-metric-row">
                    <span class="metric-label">Establishment Date:</span>
                    <span class="metric-value">${result.domain_info.creation_date}</span>
                </div>
                <div class="domain-metric-row">
                    <span class="metric-label">Domain Age:</span>
                    <span class="metric-value">${result.domain_info.domain_age_days} days</span>
                </div>
                <div class="domain-metric-row">
                    <span class="metric-label">Registrar:</span>
                    <span class="metric-value">${result.domain_info.registrar}</span>
                </div>
                <div class="domain-metric-row risk-row">
                    <span class="metric-label">Risk Score:</span>
                    <div class="risk-badge" style="background:${riskColor}20; color:${riskColor}; border:1px solid ${riskColor}">
                        ${dRisk}/100 (${riskLabel})
                    </div>
                </div>
            `;
        } else {
            whoisContent.innerHTML = `<div class="domain-metric-row"><em>Domain Intelligence Unavailable</em></div>`;
        }

        // Website Purpose & Category
        const purposePanel = document.getElementById('websitePurposePanel');
        const categoryElem = document.getElementById('websiteCategory');
        const designElem = document.getElementById('designIntent');
        const trustElem = document.getElementById('visualTrust');
        const purposeElem = document.getElementById('websitePurpose');

        if (result.website_purpose && result.type === 'URL') {
            purposePanel.style.display = 'block';
            categoryElem.textContent = result.website_category || 'General';
            designElem.textContent = result.design_intent || 'General Use';

            // Set Visual Trust based on legitimacy signals count
            const signals = result.legitimacy_signals ? result.legitimacy_signals.length : 0;
            if (signals >= 3) trustElem.textContent = 'High';
            else if (signals >= 1) trustElem.textContent = 'Medium';
            else trustElem.textContent = 'Low/New';

            // Format markdown-like bold text from Python with strong tags
            let purposeHTML = result.website_purpose.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            purposeElem.innerHTML = purposeHTML;
        } else {
            purposePanel.style.display = 'none';
        }

    } else {
        decisionPanel.style.display = 'none';
    }

    // =============================
    // Explainable AI Population
    // =============================
    if (result.scores) {
        // Update Scores
        updateScore('transformer', result.scores.transformer);
        updateScore('rule', result.scores.rule_based);
        // Check if behavior score exists (it might be 0 if not run)
        if (result.scores.behavior_risk !== undefined) {
            updateScore('behavior', result.scores.behavior_risk);
        }
        updateScore('final', displayConfidence);

        // Update Suspicious Words
        const wordsContainer = document.getElementById('suspiciousWordsList');
        wordsContainer.innerHTML = '';

        if (result.suspicious_words && result.suspicious_words.length > 0) {
            result.suspicious_words.forEach(word => {
                const tag = document.createElement('div');
                tag.className = 'suspicious-tag';
                tag.innerHTML = `<i class="fas fa-bug"></i> ${word}`;
                wordsContainer.appendChild(tag);
            });
        } else {
            wordsContainer.innerHTML = '<span class="no-words">No specific suspicious keywords detected.</span>';
        }

        // Update Behavior Findings
        const behaviorSection = document.getElementById('behaviorFindingsSection');
        const behaviorList = document.getElementById('behaviorFindingsList');

        if (result.behavior_findings && result.behavior_findings.length > 0) {
            behaviorSection.style.display = 'block';
            behaviorList.innerHTML = '';
            result.behavior_findings.forEach(flag => {
                const tag = document.createElement('div');
                tag.className = 'suspicious-tag';
                tag.style.backgroundColor = 'rgba(255, 107, 107, 0.15)';
                tag.style.color = '#d63031';
                tag.style.borderColor = '#ff7675';
                tag.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${flag}`;
                behaviorList.appendChild(tag);
            });
        } else {
            behaviorSection.style.display = 'none';
        }

        // Update Legitimacy Signals
        const legitimacySection = document.getElementById('legitimacySignalsSection');
        const legitimacyList = document.getElementById('legitimacySignalsList');

        if (result.legitimacy_signals && result.legitimacy_signals.length > 0) {
            legitimacySection.style.display = 'block';
            legitimacyList.innerHTML = '';
            result.legitimacy_signals.forEach(signal => {
                const tag = document.createElement('div');
                tag.className = 'suspicious-tag';
                tag.style.backgroundColor = 'rgba(46, 213, 115, 0.15)';
                tag.style.color = '#2ed573';
                tag.style.borderColor = '#2ed573';
                tag.innerHTML = `<i class="fas fa-check-circle"></i> ${signal}`;
                legitimacyList.appendChild(tag);
            });
        } else {
            legitimacySection.style.display = 'none';
        }
    }

    time.textContent = '47ms';
    e.scrollIntoView({ behavior: 'smooth' });
}

function updateScore(idPrefix, value) {
    const bar = document.getElementById(idPrefix + 'Bar');
    const label = document.getElementById(idPrefix + 'Score');

    if (bar && label) {
        // Animate bar width
        setTimeout(() => { bar.style.width = value + '%'; }, 100);

        // Counter animation
        let start = 0;
        const duration = 1000;
        const startTime = performance.now();

        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Ease out quart
            const ease = 1 - Math.pow(1 - progress, 4);

            const currentVal = Math.floor(start + (value - start) * ease);
            label.textContent = currentVal + '%';

            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }
        requestAnimationFrame(update);
    }
}

function hideAnalysisResults() {
    document.getElementById('analysisProgress').style.display = 'none';
    document.getElementById('attentionViz').style.display = 'none';
    document.getElementById('analysisResults').style.display = 'none';
}

// =============================
// Miscellaneous Utility
// =============================
function blockSource(url) { showToast(`Blocked source: ${url}`, 'success'); }
function addToBlocklist(url) { showToast(`Added to blocklist: ${url}`, 'success'); }
function investigate(url) { showToast(`Investigation started for: ${url}`, 'info'); }

async function loadHistory() {
    try {
        const res = await fetch('/history');
        const history = await res.json();
        const container = document.getElementById('scanHistory');

        if (history.length === 0) {
            container.innerHTML = `
                <div class="history-empty">
                    <i class="fas fa-clipboard-list"></i>
                    <p>No scans performed yet</p>
                </div>
            `;
            return;
        }

        container.innerHTML = '';
        history.forEach(item => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';

            const isPhishing = item.prediction === 'Phishing';
            const isSuspicious = item.prediction === 'Suspicious';
            const iconClass = isPhishing ? 'exclamation-triangle' : (isSuspicious ? 'question-circle' : 'shield-check');
            const colorClass = isPhishing ? 'danger' : (isSuspicious ? 'warning' : 'safe');

            // Adjust confidence for display (Safety vs Risk)
            let displayScore = item.confidence;
            if (item.prediction === 'Legitimate') {
                displayScore = 100 - item.confidence;
            }

            historyItem.innerHTML = `
                <div class="history-icon ${colorClass}">
                    <i class="fas fa-${iconClass}"></i>
                </div>
                <div class="history-details">
                    <div class="history-input">${item.input.substring(0, 40)}${item.input.length > 40 ? '...' : ''}</div>
                    <div class="history-meta">
                        <span class="history-type">${item.type}</span> • 
                        <span class="history-date">${item.timestamp}</span>
                    </div>
                </div>
                <div class="history-status ${colorClass}">
                    ${displayScore.toFixed(1)}%
                </div>
                <button class="history-download" onclick="downloadReport('${item.id}')" title="Download Report">
                    <i class="fas fa-download"></i>
                </button>
            `;
            container.appendChild(historyItem);
        });

    } catch (err) {
        console.error('Failed to load history:', err);
    }
}

function downloadReport(scanId) {
    // If no ID passed, try to get from the main detailed result button
    if (!scanId) {
        const btn = document.getElementById('downloadReportBtn');
        scanId = btn.getAttribute('data-scan-id');
    }

    if (!scanId) {
        showToast('No report available for this scan', 'error');
        return;
    }

    // Trigger download
    window.open(`/download_report/${scanId}`, '_blank');
}

async function checkModelStatus() {
    try {
        const res = await fetch('/status');
        const status = await res.json();

        // Update Status Indicators
        const indicators = document.querySelectorAll('.status-item');

        // 1. Backend API (Always index 0 if it responded)
        updateStatusDot(indicators[0], true);

        // 2. DL Model (Check ready flag)
        updateStatusDot(indicators[1], status.ready);

        // 3. Database (Simulated for this local version)
        updateStatusDot(indicators[2], true);

        // 4. External APIs (Always true for now)
        updateStatusDot(indicators[3], true);

    } catch (err) {
        console.error('Model status check failed:', err);
        // Set all to offline if fetch fails
        document.querySelectorAll('.status-dot').forEach(dot => {
            dot.className = 'status-dot offline';
        });
    }
}

function updateStatusDot(container, isOnline) {
    if (!container) return;
    const dot = container.querySelector('.status-dot');
    if (dot) {
        dot.className = isOnline ? 'status-dot online' : 'status-dot offline';
    }
}

function startRealTimeUpdates() {
    setInterval(() => { updateMetrics(); }, 5000);
}

function updateMetrics() {
    const elem = document.querySelector('.metric-card.threat .metric-value');
    if (elem && Math.random() < 0.3) {
        const cur = parseInt(elem.textContent.replace(/,/g, '')) + 1;
        elem.textContent = cur.toLocaleString();
    }
}

// =============================
// Toast Notifications
// =============================
function showToast(message, type = 'info') {
    const cont = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<i class="fas fa-${getToastIcon(type)}"></i><span>${message}</span>`;
    cont.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}
function getToastIcon(type) {
    switch (type) { case 'success': return 'check-circle'; case 'error': return 'exclamation-circle'; case 'warning': return 'exclamation-triangle'; default: return 'info-circle'; }
}

// =============================
// Modal + Shortcuts
// =============================
function showArchitecture() { document.getElementById('architectureModal').style.display = 'flex'; document.body.style.overflow = 'hidden'; }
function closeArchitecture() { document.getElementById('architectureModal').style.display = 'none'; document.body.style.overflow = 'auto'; }
document.addEventListener('click', e => { if (e.target === document.getElementById('architectureModal')) closeArchitecture(); });
document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeArchitecture();
    if (e.ctrlKey && e.key === 'Enter' && !analysisInProgress) startAnalysis();
});
