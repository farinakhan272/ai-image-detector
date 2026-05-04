document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-btn');
    const analyzeBtn = document.getElementById('analyze-btn');
    const previewImg = document.getElementById('image-preview');
    const placeholder = document.querySelector('.placeholder');
    const progressBar = document.getElementById('progress-bar');
    const statusText = document.getElementById('status-text');
    const aiResult = document.getElementById('ai-result');
    const duplicateResult = document.getElementById('duplicate-result');
    const aiCard = document.getElementById('ai-card');
    const duplicateCard = document.getElementById('duplicate-card');
    const confidenceScore = document.getElementById('confidence-score');
    const errorLog = document.getElementById('error-log');
    const loader = document.getElementById('loader');

    let selectedFile = null;

    // --- File Handling ---

    browseBtn.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        if (e.dataTransfer.files.length > 0) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    function handleFile(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please select an image file.');
            return;
        }

        selectedFile = file;
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImg.src = e.target.result;
            previewImg.classList.remove('hidden');
            placeholder.classList.add('hidden');
            analyzeBtn.disabled = false;
            resetResults();
        };
        reader.readAsDataURL(file);
    }

    function resetResults() {
        progressBar.style.width = '0%';
        statusText.innerText = 'Ready to scan';
        aiResult.innerText = 'Pending';
        duplicateResult.innerText = 'Pending';
        aiCard.className = 'card';
        duplicateCard.className = 'card';
        confidenceScore.innerText = '--%';
        confidenceScore.style.color = 'var(--text-sub)';
        errorLog.classList.add('hidden');
        errorLog.innerText = '';
    }

    // --- Analysis ---

    analyzeBtn.addEventListener('click', async () => {
        if (!selectedFile) return;

        // UI State
        analyzeBtn.disabled = true;
        browseBtn.disabled = true;
        loader.classList.remove('hidden');
        
        statusText.innerText = 'Uploading and analyzing...';
        updateProgress(30);

        const formData = new FormData();
        formData.append('image', selectedFile);

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            console.log('analyze response', response.status, response.bodyUsed);
            const text = await response.clone().text();
            let data = null;

            try {
                data = text ? JSON.parse(text) : null;
            } catch (parseError) {
                displayError('Unexpected response from server', text || parseError.message);
                throw new Error('Unexpected response from server');
            }

            if (!response.ok) {
                const errorMessage = data?.error || 'Analysis failed';
                const errorTrace = data?.trace || data?.message || text;
                displayError(errorMessage, errorTrace);
                throw new Error(errorMessage);
            }

            updateProgress(70);
            
            setTimeout(() => {
                updateProgress(100);
                displayResults(data);
                loader.classList.add('hidden');
                analyzeBtn.disabled = false;
                browseBtn.disabled = false;
            }, 800);

        } catch (error) {
            console.error('Analysis request failed', error);
            if (!errorLog.innerText) {
                displayError(error.message || 'Analysis failed');
            }
            loader.classList.add('hidden');
            analyzeBtn.disabled = false;
            browseBtn.disabled = false;
        }
    });

    function updateProgress(percent) {
        progressBar.style.width = percent + '%';
    }

    function displayError(message, trace) {
        statusText.innerText = 'Error: ' + message;
        errorLog.classList.remove('hidden');
        errorLog.innerText = trace ? `${message}\n\n${trace}` : message;
        analyzeBtn.disabled = false;
        browseBtn.disabled = false;
    }

    function displayResults(data) {
        statusText.innerText = 'Analysis Complete';

        // AI Result
        if (data.is_ai) {
            aiResult.innerText = `AI Generated (${Math.round(data.ai_score)}%)`;
            aiCard.classList.add('danger');
        } else {
            aiResult.innerText = `Human Created (${Math.round(100 - data.ai_score)}%)`;
            aiCard.classList.add('success');
        }

        // Duplicate Result
        if (data.is_duplicate) {
            const bestMatch = data.duplicates[0];
            duplicateResult.innerText = `Match Found (${Math.round(bestMatch.similarity)}%)`;
            duplicateCard.classList.add('danger');
        } else {
            duplicateResult.innerText = 'Original Content';
            duplicateCard.classList.add('success');
        }

        // Detailed Layers
        document.getElementById('details-panel').classList.remove('hidden');
        document.getElementById('bar-frequency').style.width = data.ai_details.frequency + '%';
        document.getElementById('bar-noise').style.width = data.ai_details.noise + '%';
        document.getElementById('bar-color').style.width = data.ai_details.color + '%';
        document.getElementById('bar-metadata').style.width = data.ai_details.metadata + '%';

        // Dynamic Confidence
        // High confidence if scores are consistent (all low or all high)
        const scores = [data.ai_details.frequency, data.ai_details.noise, data.ai_details.color, data.ai_details.metadata];
        const avg = scores.reduce((a, b) => a + b) / scores.length;
        const variance = scores.reduce((a, b) => a + Math.pow(b - avg, 2), 0) / scores.length;
        
        let confidence = Math.max(70, 100 - (Math.sqrt(variance) * 2));
        if (data.is_duplicate) confidence = Math.max(confidence, data.duplicates[0].similarity);
        
        confidenceScore.innerText = Math.round(confidence) + '%';
        confidenceScore.style.color = (confidence > 80 && !data.is_ai && !data.is_duplicate) ? 'var(--success)' : 'var(--danger)';
    }
});
