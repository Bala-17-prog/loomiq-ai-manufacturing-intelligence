document.addEventListener("DOMContentLoaded", async () => {
    try {
        const data = await fetchAPI('/dashboard');
        
        // Hide loader, show dashboard
        document.getElementById('loading-state').style.display = 'none';
        document.getElementById('dashboard-content').style.display = 'block'; // Or flex/block depending on your main wrapper
        
        // Update KPIs
        document.getElementById('kpi-production').textContent = data.kpis.production.toLocaleString();
        document.getElementById('kpi-efficiency').textContent = data.kpis.efficiency.toFixed(1) + '%';
        document.getElementById('kpi-defects').textContent = data.kpis.defect_rate.toFixed(1) + '%';
        
        const activeMachinesParts = data.kpis.active_machines.split('/');
        document.getElementById('kpi-machines').textContent = data.kpis.active_machines;
        if (activeMachinesParts.length === 2) {
            const offlineCount = parseInt(activeMachinesParts[1].trim()) - parseInt(activeMachinesParts[0].trim());
            document.getElementById('kpi-offline').textContent = `${offlineCount} offline`;
        }

        // Update Machine Status Panel
        if (data.health_distribution) {
            const total = (data.health_distribution["Healthy"] || 0) + (data.health_distribution["Warning"] || 0) + (data.health_distribution["Critical"] || 0);
            document.getElementById('status-total-machines').textContent = `${activeMachinesParts[1] ? activeMachinesParts[1].trim() : total}`;
            document.getElementById('status-healthy').textContent = data.health_distribution["Healthy"] || 0;
            document.getElementById('status-warning').textContent = data.health_distribution["Warning"] || 0;
            document.getElementById('status-critical').textContent = data.health_distribution["Critical"] || 0;
        }
        
        // Render Charts
        const trendDates = data.production_trend.map(d => d.date);
        const trendActuals = data.production_trend.map(d => d.actual);
        const trendTargets = data.production_trend.map(d => d.target);

        initCharts({ 
            trend: { dates: trendDates, production: trendActuals, targets: trendTargets } 
        });
        
        // Render Alerts
        renderAlerts(data.recent_alerts);

    } catch (error) {
        document.getElementById('loading-state').innerHTML = `<p style="color:var(--danger)">Failed to load dashboard data. Ensure backend is running at localhost:8000.</p>`;
    }
});

function initCharts(chartData) {
    // Colors for the new light enterprise theme
    const primaryBlue = '#2563EB';
    const blueFill = 'rgba(37, 99, 235, 0.1)';
    const targetGray = '#98A2B3';
    const textSecondary = '#667085';
    const gridColor = '#E5E7EB';

    // Set defaults
    Chart.defaults.color = textSecondary;
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.scale.grid.color = gridColor;

    // Production Trend
    const ctxProd = document.getElementById('productionChart');
    if (ctxProd) {
        new Chart(ctxProd, {
            type: 'line',
            data: {
                labels: chartData.trend.dates,
                datasets: [
                    {
                        label: 'Target',
                        data: chartData.trend.targets,
                        borderColor: targetGray,
                        borderWidth: 2,
                        borderDash: [5, 5],
                        backgroundColor: 'transparent',
                        tension: 0,
                        pointRadius: 0,
                        pointHitRadius: 10,
                        order: 2
                    },
                    {
                        label: 'Actual Production',
                        data: chartData.trend.production,
                        borderColor: primaryBlue,
                        backgroundColor: blueFill,
                        borderWidth: 2,
                        tension: 0.3,
                        fill: true,
                        pointRadius: 0,
                        pointHitRadius: 10,
                        order: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { 
                        display: true,
                        position: 'bottom',
                        labels: { boxWidth: 12, usePointStyle: true, pointStyle: 'line' }
                    },
                    tooltip: { mode: 'index', intersect: false }
                },
                scales: {
                    y: { beginAtZero: true },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // Shift Efficiency
    const ctxShift = document.getElementById('shiftChart');
    if (ctxShift) {
        new Chart(ctxShift, {
            type: 'bar',
            data: {
                labels: ['Morning', 'Afternoon', 'Night'],
                datasets: [{
                    label: 'Efficiency',
                    data: [92, 88, 85],
                    backgroundColor: primaryBlue,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function(context) { return context.parsed.y + '%'; }
                        }
                    }
                },
                scales: {
                    y: { beginAtZero: true, max: 100 },
                    x: { grid: { display: false } }
                }
            }
        });
    }
}

function renderAlerts(alerts) {
    const list = document.getElementById('alerts-list');
    list.innerHTML = '';
    
    // SVG Icons matching enterprise look
    const icons = {
        critical: `<svg class="alert-icon" width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>`,
        warning: `<svg class="alert-icon" width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`,
        info: `<svg class="alert-icon" width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`
    };
    
    alerts.forEach(alert => {
        const item = document.createElement('div');
        item.className = `alert-item ${alert.level}`;
        
        let iconHtml = icons.info;
        if(alert.level === 'warning') iconHtml = icons.warning;
        if(alert.level === 'critical') iconHtml = icons.critical;
        
        item.innerHTML = `
            ${iconHtml}
            <div>
                <strong style="color: var(--text-primary); font-size: 14px;">${alert.machine}</strong>
                <div style="font-size: 13px; color: var(--text-secondary); margin-top: 4px; line-height: 1.4;">${alert.message}</div>
            </div>
        `;
        list.appendChild(item);
    });
}
