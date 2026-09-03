document.addEventListener('DOMContentLoaded', () => {
    loadProductionData();
});

let charts = {};

async function loadProductionData() {
    const machine = document.getElementById('filter-machine').value;
    const shift = document.getElementById('filter-shift').value;
    
    let queryParams = new URLSearchParams();
    if (machine) queryParams.append('machine_id', machine);
    if (shift) queryParams.append('shift', shift);
    
    document.getElementById('loading-state').style.display = 'flex';
    document.getElementById('production-content').style.display = 'none';

    try {
        const [summary, trends, byMachine, byShift, byFabric] = await Promise.all([
            fetchAPI(`/production?${queryParams.toString()}`),
            fetchAPI(`/production/trends?${queryParams.toString()}`),
            fetchAPI(`/production/by-machine?${queryParams.toString()}`),
            fetchAPI(`/production/by-shift?${queryParams.toString()}`),
            fetchAPI(`/production/by-fabric?${queryParams.toString()}`)
        ]);
        
        // Update KPIs
        document.getElementById('prod-quantity').textContent = summary.production_quantity.toLocaleString();
        document.getElementById('prod-target').textContent = summary.target_quantity.toLocaleString();
        document.getElementById('prod-achievement').textContent = summary.achievement.toFixed(1) + '%';
        document.getElementById('prod-efficiency').textContent = summary.efficiency.toFixed(1) + '%';
        
        // Group data for rendering
        const trendData = trends.slice(-30); // Last 30 points max
        
        // byMachine, byShift, byFabric are already arrays from the API: [{"category": "...", "actual": 123}]
        const machineData = byMachine
            .sort((a,b) => b.actual - a.actual)
            .slice(0, 10);
            
        renderChart('prodTrendChart', 'line', trendData, 'date');
        renderChart('machineChart', 'bar', machineData, 'category');
        renderChart('shiftChart', 'doughnut', byShift, 'category');
        renderChart('fabricChart', 'bar', byFabric, 'category');

        document.getElementById('loading-state').style.display = 'none';
        document.getElementById('production-content').style.display = 'block';

    } catch (error) {
        console.error('Error loading production data:', error);
        document.getElementById('loading-state').innerHTML = `<p style="color:var(--danger)">Failed to load data. Ensure backend is running.</p>`;
    }
}

function applyFilters() {
    loadProductionData();
}

function renderChart(canvasId, type, dataArray, labelKey) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }
    
    const primaryBlue = '#2563EB';
    const blueFill = 'rgba(37, 99, 235, 0.1)';
    const textSecondary = '#667085';
    
    Chart.defaults.color = textSecondary;
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.scale.grid.color = '#E5E7EB';
    
    let dataset = {
        label: 'Production',
        data: dataArray.map(d => d.actual),
        backgroundColor: primaryBlue,
        borderColor: primaryBlue,
        borderWidth: type === 'line' ? 2 : 0,
        borderRadius: type === 'bar' ? 4 : 0
    };

    if (type === 'line') {
        dataset.backgroundColor = blueFill;
        dataset.fill = true;
        dataset.tension = 0.3;
        dataset.pointRadius = 0;
        dataset.pointHitRadius = 10;
    }

    if (type === 'doughnut' || type === 'pie') {
        dataset.backgroundColor = ['#2563EB', '#60A5FA', '#93C5FD', '#BFDBFE'];
        dataset.borderWidth = 0;
    }

    charts[canvasId] = new Chart(ctx, {
        type: type,
        data: {
            labels: dataArray.map(d => d[labelKey]),
            datasets: [dataset]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: type === 'doughnut' || type === 'pie',
                    position: 'bottom',
                    labels: { color: textSecondary }
                }
            },
            scales: type === 'doughnut' || type === 'pie' ? {} : {
                y: { beginAtZero: true, grid: { color: '#E5E7EB' } },
                x: { grid: { display: false } }
            },
            cutout: type === 'doughnut' ? '70%' : undefined,
            indexAxis: canvasId === 'fabricChart' ? 'y' : 'x'
        }
    });
}
