let telemetryChart;

document.addEventListener("DOMContentLoaded", async () => {
    try {
        const machines = await fetchAPI('/machines');
        
        const tbody = document.getElementById('machines-body');
        
        // We will fetch full details in parallel just for the demo to show risk in table, 
        // normally you'd paginate or have risk in the list endpoint.
        // For 20 machines, parallel fetch is fine for a demo.
        const detailPromises = machines.map(m => fetchAPI(`/machines/${m.machine_id}`));
        const detailedMachines = await Promise.all(detailPromises);
        
        detailedMachines.sort((a,b) => {
            const riskMap = {"HIGH": 3, "MEDIUM": 2, "LOW": 1};
            return riskMap[b.health.risk] - riskMap[a.health.risk];
        });

        detailedMachines.forEach(m => {
            const tr = document.createElement('tr');
            tr.onclick = () => openMachineModal(m.machine_id);
            tr.innerHTML = `
                <td><strong>${m.machine_id}</strong></td>
                <td>${m.machine_name}</td>
                <td>${m.department}</td>
                <td><span class="badge ${m.status}">${m.status}</span></td>
                <td><span class="badge ${m.health.risk}">${m.health.risk}</span></td>
            `;
            tbody.appendChild(tr);
        });

        document.getElementById('loading-state').style.display = 'none';
        document.getElementById('machines-content').style.display = 'block';
    } catch (error) {
        document.getElementById('loading-state').innerHTML = `<p style="color:var(--danger)">Failed to load data.</p>`;
    }
});

async function openMachineModal(machineId) {
    document.getElementById('machine-modal').style.display = 'flex';
    document.getElementById('modal-title').textContent = "Loading...";
    
    try {
        const [details, metrics] = await Promise.all([
            fetchAPI(`/machines/${machineId}`),
            fetchAPI(`/machines/${machineId}/metrics?limit=30`)
        ]);
        
        document.getElementById('modal-title').textContent = `${details.machine_name} (${details.machine_id})`;
        document.getElementById('modal-subtitle').textContent = `Department: ${details.department} | Installed: ${details.installation_date}`;
        
        document.getElementById('modal-health-score').textContent = details.health.score;
        const riskEl = document.getElementById('modal-risk-level');
        riskEl.textContent = details.health.risk;
        riskEl.className = `value badge ${details.health.risk}`;
        
        const indList = document.getElementById('modal-indicators');
        indList.innerHTML = '';
        details.health.indicators.forEach(ind => {
            const li = document.createElement('li');
            li.textContent = ind;
            if(details.health.risk === 'LOW') li.style.color = 'var(--success)';
            indList.appendChild(li);
        });

        renderTelemetry(metrics);
        
    } catch (error) {
        console.error(error);
        document.getElementById('modal-title').textContent = "Error loading machine data.";
    }
}

function renderTelemetry(metrics) {
    const ctx = document.getElementById('telemetryChart').getContext('2d');
    if (telemetryChart) {
        telemetryChart.destroy();
    }
    
    // Reverse to show chronological left-to-right
    metrics.reverse();
    const labels = metrics.map(m => new Date(m.timestamp).toLocaleDateString());
    const temp = metrics.map(m => m.temperature);
    const vib = metrics.map(m => m.vibration);
    
    telemetryChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Temperature (°C)',
                    data: temp,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    yAxisID: 'y'
                },
                {
                    label: 'Vibration (mm/s)',
                    data: vib,
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            scales: {
                x: { ticks: { color: '#94a3b8' } },
                y: { type: 'linear', display: true, position: 'left', ticks: { color: '#ef4444' } },
                y1: { type: 'linear', display: true, position: 'right', ticks: { color: '#f59e0b' }, grid: { drawOnChartArea: false } },
            },
            plugins: { legend: { labels: { color: '#f8fafc' } } }
        }
    });
}

function closeModal() {
    document.getElementById('machine-modal').style.display = 'none';
}
