document.addEventListener("DOMContentLoaded", () => {
    updateSimulation(); // Run initial baseline
});

function resetSimulation() {
    document.getElementById('speed').value = 1.0;
    document.getElementById('downtime').value = 0;
    document.getElementById('defect').value = 0;
    updateSimulation();
}

async function updateSimulation() {
    const speed = parseFloat(document.getElementById('speed').value);
    const downtime = parseFloat(document.getElementById('downtime').value);
    const defect = parseFloat(document.getElementById('defect').value);
    
    // Update labels
    document.getElementById('speed-val').textContent = speed.toFixed(2) + 'x';
    document.getElementById('downtime-val').textContent = (downtime > 0 ? '+' : '') + (downtime * 100).toFixed(0) + '%';
    document.getElementById('defect-val').textContent = (defect > 0 ? '+' : '') + (defect * 100).toFixed(1) + '%';
    
    try {
        const response = await fetch(`${API_BASE_URL}/simulator/simulate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                speed_multiplier: speed,
                downtime_reduction: downtime,
                defect_rate_change: defect
            })
        });
        
        const data = await response.json();
        if (data.error) return;
        
        // Update Impact Card
        const impactCard = document.getElementById('impact-card');
        const revImpact = document.getElementById('revenue-impact');
        const pctImpact = document.getElementById('percentage-impact');
        
        const revChange = data.impact.revenue_change;
        
        if (revChange < 0) {
            impactCard.className = 'impact-card negative';
            revImpact.textContent = `-$${Math.abs(revChange).toLocaleString()}`;
        } else {
            impactCard.className = 'impact-card';
            revImpact.textContent = `+$${revChange.toLocaleString()}`;
        }
        
        pctImpact.textContent = `${data.impact.percentage_change > 0 ? '+' : ''}${data.impact.percentage_change}% change vs baseline`;
        
        // Update Table
        document.getElementById('base-prod').textContent = data.baseline.production.toLocaleString();
        document.getElementById('sim-prod').textContent = data.simulated.production.toLocaleString();
        document.getElementById('delta-prod').innerHTML = formatDelta(data.simulated.production - data.baseline.production);
        
        document.getElementById('base-def').textContent = data.baseline.defects.toLocaleString();
        document.getElementById('sim-def').textContent = data.simulated.defects.toLocaleString();
        document.getElementById('delta-def').innerHTML = formatDelta(data.simulated.defects - data.baseline.defects);
        
        document.getElementById('base-good').textContent = data.baseline.good_units.toLocaleString();
        document.getElementById('sim-good').textContent = data.simulated.good_units.toLocaleString();
        document.getElementById('delta-good').innerHTML = formatDelta(data.simulated.good_units - data.baseline.good_units);
        
    } catch (error) {
        console.error("Simulation failed:", error);
    }
}

function formatDelta(val) {
    if (val > 0) return `<span style="color:var(--success)">+${val.toLocaleString()}</span>`;
    if (val < 0) return `<span style="color:var(--danger)">${val.toLocaleString()}</span>`;
    return `<span style="color:var(--text-secondary)">0</span>`;
}
