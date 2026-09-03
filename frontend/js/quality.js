document.addEventListener("DOMContentLoaded", () => {
    loadHistory();
    setupUpload();
});

function setupUpload() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');

    uploadArea.addEventListener('click', (e) => {
        if(e.target.tagName !== 'BUTTON') {
            fileInput.click();
        }
    });
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFile(e.target.files[0]);
        }
    });
}

function resetUpload() {
    document.getElementById('inspection-result').style.display = 'none';
    document.getElementById('upload-area').style.display = 'block';
    document.getElementById('file-input').value = "";
}

async function loadDemoImage(event, filename) {
    event.stopPropagation();
    try {
        const response = await fetch(`${SERVER_URL}/images/${filename}`);
        if(!response.ok) throw new Error("Image not found");
        const blob = await response.blob();
        const file = new File([blob], filename.split('/').pop(), { type: "image/jpeg" });
        handleFile(file);
    } catch(err) {
        alert("Failed to load demo image. Make sure the backend is running and generated images exist.");
    }
}

async function handleFile(file) {
    if (!file.type.startsWith('image/')) {
        alert("Please upload a valid image file (JPG, PNG, WEBP).");
        return;
    }
    if (file.size > 10 * 1024 * 1024) {
        alert("Image exceeds the 10 MB upload limit.");
        return;
    }

    document.getElementById('upload-area').style.display = 'none';
    document.getElementById('inspection-result').style.display = 'none';
    document.getElementById('processing-state').style.display = 'flex';

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE_URL}/quality/inspect`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || "Processing failed");
        }
        
        // Show result
        document.getElementById('processing-state').style.display = 'none';
        document.getElementById('inspection-result').style.display = 'block';
        
        const statusEl = document.getElementById('res-status');
        statusEl.textContent = result.result;
        statusEl.className = `value badge ${result.result}`;
        
        document.getElementById('res-score').textContent = `${result.anomaly_score} / 100`;
        
        const sevEl = document.getElementById('res-severity');
        sevEl.textContent = result.severity;
        sevEl.className = `value badge ${result.severity}`;
        
        document.getElementById('res-issue').textContent = result.potential_issue;
        document.getElementById('res-confidence').textContent = result.detection_strength > 0 ? `${result.detection_strength}%` : "N/A";
        
        // Gauge
        const fillW = Math.min(100, Math.max(0, result.anomaly_score));
        document.getElementById('gauge-fill').style.width = `${fillW}%`;
        document.getElementById('gauge-marker').style.left = `${fillW}%`;
        document.getElementById('gauge-text').textContent = `Current: ${result.anomaly_score}`;
        
        // Images (using relative URLs from FastAPI backend which resolves to the mount)
        const imgOriginal = document.getElementById('img-original');
        const imgProcessed = document.getElementById('img-processed');
        
        imgOriginal.onerror = () => { imgOriginal.alt = "Unable to load inspection image. Please retry the inspection."; };
        imgProcessed.onerror = () => { imgProcessed.alt = "Unable to load inspection image. Please retry the inspection."; };
        
        imgOriginal.src = `${SERVER_URL}${result.original_image_url}`;
        imgProcessed.src = `${SERVER_URL}${result.processed_image_url}`;

        // Details
        const tbody = document.getElementById('details-body');
        const details = result.processing_details;
        tbody.innerHTML = `
            <tr><td><strong>Image Hash (SHA-256)</strong></td><td style="font-family: monospace; font-size: 12px; word-break: break-all;">${result.image_hash}</td></tr>
            <tr><td><strong>Resolution</strong></td><td>${details.image_width} × ${details.image_height}</td></tr>
            <tr><td><strong>Detected Regions</strong></td><td>${details.detected_regions}</td></tr>
            <tr><td><strong>Largest Region</strong></td><td>${details.largest_region_pixels} px</td></tr>
            <tr><td><strong>Mean Anomaly Intensity</strong></td><td>${details.mean_anomaly_intensity}</td></tr>
            <tr><td><strong>Processing Time</strong></td><td>${details.processing_time_ms} ms</td></tr>
            <tr><td><strong>Method</strong></td><td>${details.method}</td></tr>
            <tr><td><strong>Pipeline</strong></td><td>${details.pipeline.join(" → ")}</td></tr>
        `;

        // Reload history
        loadHistory();
        
    } catch (error) {
        alert(error.message || "Failed to process image.");
        document.getElementById('processing-state').style.display = 'none';
        document.getElementById('upload-area').style.display = 'block';
    }
}

async function loadHistory() {
    try {
        const history = await fetchAPI('/quality/history?limit=10');
        const tbody = document.getElementById('history-body');
        tbody.innerHTML = '';
        
        if(history.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:var(--text-secondary)">No inspection records found.</td></tr>';
            return;
        }

        history.forEach(h => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${h.inspection_id}</td>
                <td>${new Date(h.timestamp).toLocaleString()}</td>
                <td><span class="badge ${h.result}">${h.result}</span></td>
                <td>${h.anomaly_score}</td>
                <td><span class="badge ${h.severity}">${h.severity}</span></td>
                <td>${h.potential_issue || '-'}</td>
                <td style="font-family: monospace; font-size: 10px;">${h.image_hash.substring(0, 12)}...</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error("Failed to load history", error);
    }
}
