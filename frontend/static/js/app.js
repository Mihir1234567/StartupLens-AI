// StartupLens AI Full-Stack Application Logic
document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

let charts = {
    whatIf: null,
    yearly: null,
    cityShare: null,
    features: null
};

async function initApp() {
    setupTabs();
    setupSliders();
    await loadMetadata();
    setupPredictionForm();
    setupWhatIfTrigger();
    
    // Automatically trigger initial prediction & load background tabs
    runPrediction();
    loadInvestorAnalytics();
    loadSectorOpportunities();
    loadEcosystemAnalytics();
    loadModelDiagnostics();
}

// Tab Switching
function setupTabs() {
    const tabs = document.querySelectorAll('.nav-tab');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetId = tab.getAttribute('data-tab');
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));

            tab.classList.add('active');
            const targetContent = document.getElementById(targetId);
            if (targetContent) {
                targetContent.classList.add('active');
            }

            // Trigger specific renders when switching
            if (targetId === 'whatif-tab' && !charts.whatIf) {
                runWhatIfSimulation();
            }
        });
    });
}

// Sliders and Steppers synchronization
function setupSliders() {
    const yearSlider = document.getElementById('funding_year');
    const yearVal = document.getElementById('funding_year_val');
    if (yearSlider && yearVal) {
        yearSlider.addEventListener('input', (e) => {
            yearVal.innerText = e.target.value;
        });
    }

    const syndicateInput = document.getElementById('investor_count');
    const syndicateVal = document.getElementById('investor_count_val');
    if (syndicateInput && syndicateVal) {
        syndicateInput.addEventListener('input', (e) => {
            syndicateVal.innerText = e.target.value;
        });
    }
}

// Load metadata and populate select fields
async function loadMetadata() {
    try {
        const res = await fetch('/api/metadata');
        if (!res.ok) throw new Error('Failed to fetch metadata');
        const data = await res.json();

        // Update header stat badges
        const totalDealsEl = document.getElementById('stat_total_deals');
        if (totalDealsEl) totalDealsEl.innerText = data.total_deals.toLocaleString() + ' Deals Analyzed';

        const totalCapEl = document.getElementById('stat_total_capital');
        if (totalCapEl) totalCapEl.innerText = data.total_capital_formatted_usd;

        // Populate Industry options
        populateSelect('industry_select', data.industries, 'FinTech & Payments');
        populateSelect('whatif_industry_select', data.industries, 'Technology & Enterprise SaaS');

        // Populate City options
        populateSelect('city_select', data.cities, 'Bangalore');

        // Populate Investment Types
        populateSelect('stage_select', data.investment_types, 'Early Stage (Series A/B)');
        populateSelect('whatif_stage_select', data.investment_types, 'Early Stage (Series A/B)');
    } catch (err) {
        console.error('Error loading metadata:', err);
    }
}

function populateSelect(elementId, items, defaultValue) {
    const el = document.getElementById(elementId);
    if (!el) return;
    el.innerHTML = '';
    items.forEach(item => {
        const opt = document.createElement('option');
        opt.value = item;
        opt.innerText = item;
        if (item === defaultValue) opt.selected = true;
        el.appendChild(opt);
    });
}

// Setup Prediction Form
function setupPredictionForm() {
    const form = document.getElementById('prediction_form');
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            runPrediction();
        });
    }

    // Presets
    const presets = document.querySelectorAll('.preset-btn');
    presets.forEach(btn => {
        btn.addEventListener('click', () => {
            const industry = btn.getAttribute('data-industry');
            const city = btn.getAttribute('data-city');
            const stage = btn.getAttribute('data-stage');
            const year = btn.getAttribute('data-year');
            const syndicate = btn.getAttribute('data-syndicate');

            if (industry) document.getElementById('industry_select').value = industry;
            if (city) document.getElementById('city_select').value = city;
            if (stage) document.getElementById('stage_select').value = stage;
            if (year) {
                document.getElementById('funding_year').value = year;
                document.getElementById('funding_year_val').innerText = year;
            }
            if (syndicate) {
                document.getElementById('investor_count').value = syndicate;
                document.getElementById('investor_count_val').innerText = syndicate;
            }

            runPrediction();
        });
    });
}

// Run Valuation Prediction
async function runPrediction() {
    const btn = document.getElementById('predict_submit_btn');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span>⚡ Computing Valuation Dynamics...</span>';
    }

    const payload = {
        industry: document.getElementById('industry_select').value,
        city: document.getElementById('city_select').value,
        investment_type: document.getElementById('stage_select').value,
        funding_year: parseInt(document.getElementById('funding_year').value),
        investor_count: parseInt(document.getElementById('investor_count').value)
    };

    try {
        const res = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error('Prediction request failed');
        const data = await res.json();

        // Render Hero Box
        document.getElementById('res_val_usd').innerText = data.formatted_usd;
        document.getElementById('res_val_inr').innerText = '≈ ' + data.formatted_inr;
        document.getElementById('res_tier_badge').innerText = data.valuation_tier;
        document.getElementById('res_percentile').innerText = `Top ${100 - data.comparable_percentile}% of historical Indian funding rounds`;

        // Render Confidence Interval
        document.getElementById('res_lower_bound').innerText = '$' + (data.lower_bound_usd / 1e6).toFixed(2) + 'M';
        document.getElementById('res_upper_bound').innerText = '$' + (data.upper_bound_usd / 1e6).toFixed(2) + 'M';
        document.getElementById('res_range_meter_fill').style.width = '75%';

        // Render AI Advisory Insights
        const insightsList = document.getElementById('res_insights_list');
        insightsList.innerHTML = '';
        data.advisory_insights.forEach(insight => {
            const li = document.createElement('li');
            li.innerText = insight;
            insightsList.appendChild(li);
        });

    } catch (err) {
        console.error('Prediction error:', err);
        alert('Could not complete prediction. Please verify the backend connection.');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<span>🚀 Run Valuation Inference</span>';
        }
    }
}

// Setup What-If Trigger
function setupWhatIfTrigger() {
    const btn = document.getElementById('run_whatif_btn');
    if (btn) {
        btn.addEventListener('click', runWhatIfSimulation);
    }
}

// Run What-If Simulation
async function runWhatIfSimulation() {
    const industry = document.getElementById('whatif_industry_select').value;
    const stage = document.getElementById('whatif_stage_select').value;
    const year = parseInt(document.getElementById('whatif_year').value || 2026);
    const syndicate = parseInt(document.getElementById('whatif_syndicate').value || 2);

    const payload = {
        industry: industry,
        investment_type: stage,
        funding_year: year,
        investor_count: syndicate,
        candidate_cities: ['Bangalore', 'Mumbai', 'Delhi NCR', 'Pune', 'Hyderabad', 'Chennai', 'Ahmedabad', 'Jaipur', 'Kolkata']
    };

    try {
        const res = await fetch('/api/what-if', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error('What-If simulation failed');
        const data = await res.json();

        // Render Table
        const tbody = document.getElementById('whatif_table_body');
        tbody.innerHTML = '';

        const cities = [];
        const amounts = [];

        data.results.forEach((item, index) => {
            cities.push(item.city);
            amounts.push(item.estimated_amount_usd / 1e6);

            const tr = document.createElement('tr');
            if (item.is_highest) tr.classList.add('highlight-row');

            const varianceBadge = item.variance_pct >= 0 
                ? `<span style="color: #34d399; font-weight: 600;">+${item.variance_pct}%</span>`
                : `<span style="color: #f43f5e; font-weight: 600;">${item.variance_pct}%</span>`;

            tr.innerHTML = `
                <td><strong>#${index + 1}</strong></td>
                <td>${item.city} ${item.is_highest ? '🏆 <small>(Top Hub)</small>' : ''}</td>
                <td>${item.formatted_usd}</td>
                <td>${item.formatted_inr}</td>
                <td>${varianceBadge}</td>
            `;
            tbody.appendChild(tr);
        });

        // Render Chart
        renderWhatIfChart(cities, amounts);

    } catch (err) {
        console.error('What-If error:', err);
    }
}

function renderWhatIfChart(labels, values) {
    const ctx = document.getElementById('whatIfChart');
    if (!ctx) return;

    if (charts.whatIf) {
        charts.whatIf.destroy();
    }

    charts.whatIf = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Projected Funding (Million USD)',
                data: values,
                backgroundColor: labels.map((_, i) => i === 0 ? 'rgba(6, 182, 212, 0.85)' : 'rgba(59, 130, 246, 0.5)'),
                borderColor: labels.map((_, i) => i === 0 ? '#06b6d4' : '#3b82f6'),
                borderWidth: 1.5,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => `$${ctx.parsed.y.toFixed(2)}M USD`
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#9ca3af', font: { size: 11 } }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: {
                        color: '#9ca3af',
                        callback: (v) => `$${v}M`
                    }
                }
            }
        }
    });
}

// Load Investor Analytics
async function loadInvestorAnalytics() {
    try {
        const res = await fetch('/api/investors?top_n=12');
        if (!res.ok) throw new Error('Failed to fetch investors');
        const data = await res.json();

        const tbody = document.getElementById('investors_table_body');
        if (!tbody) return;
        tbody.innerHTML = '';

        const maxDeals = data[0] ? data[0].deal_count : 1;

        data.forEach((inv, idx) => {
            const tr = document.createElement('tr');
            const pct = Math.round((inv.deal_count / maxDeals) * 100);
            tr.innerHTML = `
                <td><span class="badge ${idx < 3 ? 'badge-live' : 'badge-author'}">#${idx + 1}</span></td>
                <td><strong>${inv.name}</strong></td>
                <td>${inv.deal_count} Rounds</td>
                <td style="width: 35%;">
                    <div class="progress-bar-wrap">
                        <div class="progress-bar-fill" style="width: ${pct}%; background: linear-gradient(90deg, #3b82f6, #06b6d4);"></div>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error('Error loading investors:', err);
    }
}

// Load Sector Opportunities
async function loadSectorOpportunities() {
    try {
        const res = await fetch('/api/sectors');
        if (!res.ok) throw new Error('Failed to fetch sectors');
        const data = await res.json();

        const tbody = document.getElementById('sectors_table_body');
        if (!tbody) return;
        tbody.innerHTML = '';

        data.forEach((sec, idx) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>#${idx + 1}</strong></td>
                <td><strong>${sec.industry}</strong></td>
                <td>
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-weight: 700; color: #67e8f9;">${sec.opportunity_score}</span>
                        <div class="progress-bar-wrap" style="width: 80px;">
                            <div class="progress-bar-fill" style="width: ${sec.opportunity_score}%; background: #10b981;"></div>
                        </div>
                    </div>
                </td>
                <td>${sec.formatted_total_usd}</td>
                <td>${sec.funding_rounds}</td>
                <td>${sec.formatted_median_usd}</td>
                <td>${sec.active_cities_count} Hubs</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error('Error loading sectors:', err);
    }
}

// Load Ecosystem Macro Analytics
async function loadEcosystemAnalytics() {
    try {
        const res = await fetch('/api/ecosystem-stats');
        if (!res.ok) throw new Error('Failed to fetch ecosystem stats');
        const data = await res.json();

        // 1. Yearly Trend Chart
        const yearlyCtx = document.getElementById('yearlyChart');
        if (yearlyCtx) {
            const labels = data.yearly_trends.map(d => d.year);
            const deals = data.yearly_trends.map(d => d.deal_count);
            const funding = data.yearly_trends.map(d => d.total_funding_m);

            charts.yearly = new Chart(yearlyCtx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Deal Count',
                            data: deals,
                            borderColor: '#3b82f6',
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            fill: true,
                            tension: 0.35,
                            yAxisID: 'y'
                        },
                        {
                            label: 'Total Capital ($M)',
                            data: funding,
                            borderColor: '#06b6d4',
                            backgroundColor: 'transparent',
                            borderDash: [5, 5],
                            tension: 0.35,
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#9ca3af' } },
                        y: { position: 'left', grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#9ca3af' } },
                        y1: { position: 'right', grid: { drawOnChartArea: false }, ticks: { color: '#67e8f9' } }
                    }
                }
            });
        }

        // 2. City Share Donut Chart
        const cityCtx = document.getElementById('cityShareChart');
        if (cityCtx) {
            const topCities = data.city_distribution.slice(0, 6);
            charts.cityShare = new Chart(cityCtx, {
                type: 'doughnut',
                data: {
                    labels: topCities.map(c => c.city),
                    datasets: [{
                        data: topCities.map(c => c.total_funding_m),
                        backgroundColor: [
                            '#3b82f6',
                            '#06b6d4',
                            '#10b981',
                            '#8b5cf6',
                            '#f59e0b',
                            '#6b7280'
                        ],
                        borderWidth: 2,
                        borderColor: '#111827'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom', labels: { color: '#d1d5db', font: { size: 11 } } }
                    }
                }
            });
        }
    } catch (err) {
        console.error('Error loading ecosystem stats:', err);
    }
}

// Load Model Diagnostics & Benchmarks
async function loadModelDiagnostics() {
    try {
        const res = await fetch('/api/model-info');
        if (!res.ok) throw new Error('Failed to fetch model info');
        const data = await res.json();

        // Populate Benchmarks Table
        const tbody = document.getElementById('benchmarks_table_body');
        if (tbody) {
            tbody.innerHTML = '';
            data.benchmarks.forEach(bm => {
                const tr = document.createElement('tr');
                if (bm.is_best) tr.classList.add('highlight-row');
                tr.innerHTML = `
                    <td><strong>${bm.algorithm}</strong> ${bm.is_best ? '<span class="badge badge-live">Selected Production Model</span>' : ''}</td>
                    <td>${bm.test_r2.toFixed(4)}</td>
                    <td>${bm.test_rmse.toFixed(4)}</td>
                    <td>${bm.test_mae.toFixed(4)}</td>
                    <td>${bm.cv_r2.toFixed(4)}</td>
                    <td><small style="color: #9ca3af;">${bm.description}</small></td>
                `;
                tbody.appendChild(tr);
            });
        }

        // Feature Importances Chart
        const featCtx = document.getElementById('featuresChart');
        if (featCtx) {
            const topFeats = data.feature_importances.slice(0, 8);
            charts.features = new Chart(featCtx, {
                type: 'bar',
                indexAxis: 'y',
                data: {
                    labels: topFeats.map(f => f.feature_label),
                    datasets: [{
                        label: 'Feature Attribution (%)',
                        data: topFeats.map(f => f.importance_percentage),
                        backgroundColor: 'rgba(99, 102, 241, 0.75)',
                        borderColor: '#6366f1',
                        borderWidth: 1,
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: { callbacks: { label: (c) => `${c.parsed.x}% relative importance` } }
                    },
                    scales: {
                        x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#9ca3af', callback: v => v + '%' } },
                        y: { grid: { display: false }, ticks: { color: '#e5e7eb', font: { size: 11 } } }
                    }
                }
            });
        }
    } catch (err) {
        console.error('Error loading model diagnostics:', err);
    }
}
