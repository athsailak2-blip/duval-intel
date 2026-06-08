import json
import os

# Create the dashboard HTML for Duval County
# This is a static HTML dashboard that can be hosted on GitHub Pages

dashboard_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Duval County Lead Intelligence Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f7fa;
            color: #2c3e50;
            line-height: 1.6;
        }
        
        .header {
            background: #1a5276;
            color: white;
            padding: 20px 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .header .subtitle {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .header .refresh-info {
            font-size: 12px;
            opacity: 0.7;
            margin-top: 10px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px 40px;
        }
        
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .kpi-card {
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        }
        
        .kpi-card .label {
            font-size: 13px;
            color: #7f8c8d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }
        
        .kpi-card .value {
            font-size: 36px;
            font-weight: 700;
            color: #2c3e50;
        }
        
        .kpi-card .change {
            font-size: 13px;
            margin-top: 8px;
            font-weight: 500;
        }
        
        .kpi-card .change.positive {
            color: #27ae60;
        }
        
        .kpi-card .change.negative {
            color: #e74c3c;
        }
        
        .kpi-card .change.neutral {
            color: #95a5a6;
        }
        
        .section {
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        
        .section h2 {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 20px;
            color: #2c3e50;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .section h2 .badge {
            background: #f39c12;
            color: white;
            font-size: 12px;
            padding: 4px 10px;
            border-radius: 20px;
            font-weight: 500;
        }
        
        .lead-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }
        
        .lead-table th {
            text-align: left;
            padding: 12px 16px;
            font-weight: 600;
            color: #7f8c8d;
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 0.5px;
            border-bottom: 2px solid #ecf0f1;
        }
        
        .lead-table td {
            padding: 16px;
            border-bottom: 1px solid #ecf0f1;
            vertical-align: top;
        }
        
        .lead-table tr:hover {
            background: #f8f9fa;
        }
        
        .score-badge {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 13px;
        }
        
        .score-high {
            background: #d5f5e3;
            color: #27ae60;
        }
        
        .score-medium {
            background: #fef9e7;
            color: #f39c12;
        }
        
        .score-low {
            background: #fadbd8;
            color: #e74c3c;
        }
        
        .deal-path {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 500;
            background: #ebf5fb;
            color: #1a5276;
        }
        
        .signal-stack {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }
        
        .signal-tag {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 500;
            background: #f0f3f4;
            color: #5d6d7e;
        }
        
        .signal-tag.foreclosure {
            background: #fadbd8;
            color: #c0392b;
        }
        
        .signal-tag.tax {
            background: #fef9e7;
            color: #d68910;
        }
        
        .signal-tag.code {
            background: #ebf5fb;
            color: #2874a6;
        }
        
        .signal-tag.probate {
            background: #f5eef8;
            color: #8e44ad;
        }
        
        .signal-tag.estate {
            background: #eafaf1;
            color: #1e8449;
        }
        
        .address-cell {
            font-weight: 500;
            color: #2c3e50;
        }
        
        .owner-cell {
            color: #5d6d7e;
            font-size: 13px;
        }
        
        .date-cell {
            color: #7f8c8d;
            font-size: 13px;
        }
        
        .status-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 6px;
        }
        
        .status-active {
            background: #27ae60;
        }
        
        .status-pending {
            background: #f39c12;
        }
        
        .status-closed {
            background: #95a5a6;
        }
        
        .filters {
            display: flex;
            gap: 12px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .filter-btn {
            padding: 8px 16px;
            border: 1px solid #d5dbdb;
            border-radius: 8px;
            background: white;
            color: #5d6d7e;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .filter-btn:hover, .filter-btn.active {
            background: #1a5276;
            color: white;
            border-color: #1a5276;
        }
        
        .source-health {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 16px;
        }
        
        .source-card {
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 16px;
            border-radius: 8px;
            background: #f8f9fa;
        }
        
        .source-icon {
            width: 40px;
            height: 40px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
        }
        
        .source-icon.online {
            background: #d5f5e3;
        }
        
        .source-icon.warning {
            background: #fef9e7;
        }
        
        .source-icon.offline {
            background: #fadbd8;
        }
        
        .source-info {
            flex: 1;
        }
        
        .source-name {
            font-weight: 600;
            font-size: 14px;
            color: #2c3e50;
        }
        
        .source-status {
            font-size: 12px;
            color: #7f8c8d;
            margin-top: 2px;
        }
        
        .source-last {
            font-size: 11px;
            color: #95a5a6;
        }
        
        .footer {
            text-align: center;
            padding: 40px;
            color: #95a5a6;
            font-size: 13px;
        }
        
        .footer a {
            color: #1a5276;
            text-decoration: none;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 20px;
            }
            
            .header {
                padding: 20px;
            }
            
            .lead-table {
                font-size: 12px;
            }
            
            .lead-table th, .lead-table td {
                padding: 8px;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Duval County Lead Intelligence</h1>
        <div class="subtitle">Jacksonville & Beaches Area - Real Estate Distress Signals</div>
        <div class="refresh-info">Last refreshed: <span id="last-refresh">Loading...</span> | Framework v5.3.1</div>
    </div>
    
    <div class="container">
        <!-- KPI Cards -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="label">Total Active Leads</div>
                <div class="value" id="total-leads">--</div>
                <div class="change positive">+12 from yesterday</div>
            </div>
            <div class="kpi-card">
                <div class="label">High-Stack Leads (3+ Signals)</div>
                <div class="value" id="high-stack-leads">--</div>
                <div class="change positive">+3 new this week</div>
            </div>
            <div class="kpi-card">
                <div class="label">Foreclosure Signals</div>
                <div class="value" id="foreclosure-count">--</div>
                <div class="change neutral">Active pipeline</div>
            </div>
            <div class="kpi-card">
                <div class="label">Tax Delinquent</div>
                <div class="value" id="tax-delinquent-count">--</div>
                <div class="change negative">+5 new delinquencies</div>
            </div>
            <div class="kpi-card">
                <div class="label">Code Violations</div>
                <div class="value" id="code-violation-count">--</div>
                <div class="change neutral">Pending PRR data</div>
            </div>
            <div class="kpi-card">
                <div class="label">Avg Lead Score</div>
                <div class="value" id="avg-score">--</div>
                <div class="change positive">+2.3 this week</div>
            </div>
        </div>
        
        <!-- Lead Table -->
        <div class="section">
            <h2>
                Active Leads
                <span class="badge" id="lead-count-badge">Loading...</span>
            </h2>
            
            <div class="filters">
                <button class="filter-btn active" data-filter="all">All Leads</button>
                <button class="filter-btn" data-filter="high">High Stack (3+)</button>
                <button class="filter-btn" data-filter="foreclosure">Foreclosure</button>
                <button class="filter-btn" data-filter="tax">Tax Delinquent</button>
                <button class="filter-btn" data-filter="code">Code Violation</button>
                <button class="filter-btn" data-filter="probate">Probate/Estate</button>
            </div>
            
            <table class="lead-table">
                <thead>
                    <tr>
                        <th>Score</th>
                        <th>Address</th>
                        <th>Owner</th>
                        <th>Signal Stack</th>
                        <th>Deal Path</th>
                        <th>Last Signal</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody id="lead-table-body">
                    <tr>
                        <td colspan="7" style="text-align: center; padding: 40px; color: #95a5a6;">
                            Loading leads data...
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <!-- Source Health -->
        <div class="section">
            <h2>Source Health</h2>
            <div class="source-health" id="source-health">
                <!-- Source cards will be populated by JavaScript -->
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>Duval County Lead Intelligence System | Framework v5.3.1</p>
        <p>Data sourced from: Duval County Clerk, Property Appraiser, Tax Collector, Court Records, and Municipal Code Compliance</p>
        <p style="margin-top: 10px;"><a href="#" onclick="alert('Refresh initiated'); return false;">Manual Refresh</a> | <a href="https://github.com/xcerebroai/duval-intel" target="_blank">GitHub Repo</a></p>
    </div>
    
    <script>
        // Sample data for demonstration - in production this would be loaded from leads.json
        const sampleLeads = [
            {
                id: "LEAD-001",
                score: 95,
                address: "888 Pre foreclosure Ln, Jacksonville, FL 32210",
                owner: "Michael Brown",
                signals: [
                    { type: "foreclosure", label: "Lis Pendens" },
                    { type: "foreclosure", label: "Foreclosure Sale" },
                    { type: "tax", label: "Tax Delinquent" }
                ],
                dealPath: "Wholesale",
                lastSignal: "2026-05-20",
                status: "active"
            },
            {
                id: "LEAD-002",
                score: 92,
                address: "999 Tax Delinquent Dr, Jacksonville, FL 32211",
                owner: "Sarah Davis",
                signals: [
                    { type: "tax", label: "Tax Delinquent" },
                    { type: "tax", label: "Tax Deed Sale" },
                    { type: "code", label: "Code Violation" }
                ],
                dealPath: "Sub-To",
                lastSignal: "2026-05-10",
                status: "active"
            },
            {
                id: "LEAD-003",
                score: 88,
                address: "111 Code Violation St, Jacksonville, FL 32206",
                owner: "DEF Rentals LLC",
                signals: [
                    { type: "code", label: "Code Violation" },
                    { type: "code", label: "Nuisance Lien" },
                    { type: "foreclosure", label: "Eviction" }
                ],
                dealPath: "Rental Acquisition",
                lastSignal: "2026-05-20",
                status: "active"
            },
            {
                id: "LEAD-004",
                score: 85,
                address: "222 Probate Ct, Jacksonville, FL 32207",
                owner: "Estate of William Taylor",
                signals: [
                    { type: "probate", label: "Probate Case" },
                    { type: "estate", label: "Estate Transfer" },
                    { type: "tax", label: "Tax Delinquent" }
                ],
                dealPath: "Probate",
                lastSignal: "2026-04-05",
                status: "active"
            },
            {
                id: "LEAD-005",
                score: 82,
                address: "333 Sheriff Sale Blvd, Jacksonville Beach, FL 32250",
                owner: "Bank of America NA",
                signals: [
                    { type: "foreclosure", label: "Foreclosure Sale" },
                    { type: "foreclosure", label: "Bank Owned" }
                ],
                dealPath: "REO Flip",
                lastSignal: "2026-05-01",
                status: "active"
            },
            {
                id: "LEAD-006",
                score: 78,
                address: "789 Beach Blvd, Jacksonville Beach, FL 32250",
                owner: "Estate of Mary Johnson",
                signals: [
                    { type: "estate", label: "Probate Transfer" },
                    { type: "tax", label: "Tax Delinquent" }
                ],
                dealPath: "Probate",
                lastSignal: "2026-03-10",
                status: "active"
            },
            {
                id: "LEAD-007",
                score: 75,
                address: "777 Trust Ave, Neptune Beach, FL 32266",
                owner: "The Johnson Family Trust",
                signals: [
                    { type: "estate", label: "Trust Transfer" },
                    { type: "estate", label: "Trustee Sale" }
                ],
                dealPath: "Creative Finance",
                lastSignal: "2026-04-10",
                status: "active"
            },
            {
                id: "LEAD-008",
                score: 72,
                address: "555 Industrial Way, Jacksonville, FL 32254",
                owner: "XYZ Corp",
                signals: [
                    { type: "code", label: "Zoning Violation" },
                    { type: "estate", label: "Out of State Owner" }
                ],
                dealPath: "Commercial",
                lastSignal: "2026-04-25",
                status: "active"
            }
        ];
        
        const sources = [
            { name: "Official Records", status: "online", lastRefresh: "2026-06-08 06:30 AM", icon: "📄" },
            { name: "Court Records (CORE)", status: "online", lastRefresh: "2026-06-08 06:30 AM", icon: "⚖️" },
            { name: "Foreclosure Sales", status: "online", lastRefresh: "2026-06-08 06:15 AM", icon: "🏠" },
            { name: "Tax Deed Sales", status: "online", lastRefresh: "2026-06-08 06:00 AM", icon: "💰" },
            { name: "Property Appraiser", status: "online", lastRefresh: "2026-06-08 05:45 AM", icon: "📊" },
            { name: "Tax Collector", status: "online", lastRefresh: "2026-06-08 05:30 AM", icon: "📝" },
            { name: "GIS Mapping", status: "online", lastRefresh: "2026-06-07 11:00 PM", icon: "🗺️" },
            { name: "Code Enforcement", status: "warning", lastRefresh: "2026-06-01 09:00 AM", icon: "🔍" }
        ];
        
        function renderLeads(leads) {
            const tbody = document.getElementById('lead-table-body');
            tbody.innerHTML = '';
            
            leads.forEach(lead => {
                const scoreClass = lead.score >= 85 ? 'score-high' : lead.score >= 70 ? 'score-medium' : 'score-low';
                const statusClass = lead.status === 'active' ? 'status-active' : lead.status === 'pending' ? 'status-pending' : 'status-closed';
                
                const signalsHtml = lead.signals.map(s => 
                    `<span class="signal-tag ${s.type}">${s.label}</span>`
                ).join('');
                
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><span class="score-badge ${scoreClass}">${lead.score}</span></td>
                    <td class="address-cell">${lead.address}</td>
                    <td class="owner-cell">${lead.owner}</td>
                    <td><div class="signal-stack">${signalsHtml}</div></td>
                    <td><span class="deal-path">${lead.dealPath}</span></td>
                    <td class="date-cell">${lead.lastSignal}</td>
                    <td><span class="status-indicator ${statusClass}"></span>${lead.status}</td>
                `;
                tbody.appendChild(row);
            });
        }
        
        function renderSourceHealth() {
            const container = document.getElementById('source-health');
            container.innerHTML = '';
            
            sources.forEach(source => {
                const statusClass = source.status === 'online' ? 'online' : source.status === 'warning' ? 'warning' : 'offline';
                const statusText = source.status === 'online' ? 'Healthy' : source.status === 'warning' ? 'PRR Required' : 'Offline';
                
                const card = document.createElement('div');
                card.className = 'source-card';
                card.innerHTML = `
                    <div class="source-icon ${statusClass}">${source.icon}</div>
                    <div class="source-info">
                        <div class="source-name">${source.name}</div>
                        <div class="source-status">${statusText}</div>
                        <div class="source-last">Last refresh: ${source.lastRefresh}</div>
                    </div>
                `;
                container.appendChild(card);
            });
        }
        
        function updateKPIs() {
            document.getElementById('total-leads').textContent = sampleLeads.length;
            document.getElementById('high-stack-leads').textContent = sampleLeads.filter(l => l.signals.length >= 3).length;
            document.getElementById('foreclosure-count').textContent = sampleLeads.filter(l => l.signals.some(s => s.type === 'foreclosure')).length;
            document.getElementById('tax-delinquent-count').textContent = sampleLeads.filter(l => l.signals.some(s => s.type === 'tax')).length;
            document.getElementById('code-violation-count').textContent = sampleLeads.filter(l => l.signals.some(s => s.type === 'code')).length;
            document.getElementById('avg-score').textContent = Math.round(sampleLeads.reduce((a, b) => a + b.score, 0) / sampleLeads.length);
            document.getElementById('lead-count-badge').textContent = sampleLeads.length;
            document.getElementById('last-refresh').textContent = new Date().toLocaleString();
        }
        
        // Filter functionality
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                
                const filter = this.dataset.filter;
                let filtered = sampleLeads;
                
                if (filter === 'high') {
                    filtered = sampleLeads.filter(l => l.signals.length >= 3);
                } else if (filter === 'foreclosure') {
                    filtered = sampleLeads.filter(l => l.signals.some(s => s.type === 'foreclosure'));
                } else if (filter === 'tax') {
                    filtered = sampleLeads.filter(l => l.signals.some(s => s.type === 'tax'));
                } else if (filter === 'code') {
                    filtered = sampleLeads.filter(l => l.signals.some(s => s.type === 'code'));
                } else if (filter === 'probate') {
                    filtered = sampleLeads.filter(l => l.signals.some(s => s.type === 'probate' || s.type === 'estate'));
                }
                
                renderLeads(filtered);
            });
        });
        
        // Initialize
        updateKPIs();
        renderLeads(sampleLeads);
        renderSourceHealth();
        
        // In production, this would fetch from leads.json
        // fetch('data/leads.json')
        //     .then(r => r.json())
        //     .then(data => {
        //         renderLeads(data.leads);
        //         updateKPIs(data);
        //     });
    </script>
</body>
</html>'''

# Write dashboard HTML
with open("dashboard/index.html", "w") as f:
    f.write(dashboard_html)

print("Created: dashboard/index.html")

# Create a simple leads.json data file for the dashboard
sample_leads_data = {
    "county": "Duval",
    "state": "FL",
    "last_refresh": "2026-06-08T06:49:34+05:30",
    "framework_version": "v5.3.1",
    "total_leads": 8,
    "high_stack_leads": 3,
    "sources": {
        "official_records": {"status": "healthy", "last_refresh": "2026-06-08T06:30:00", "records_count": 156},
        "court_records": {"status": "healthy", "last_refresh": "2026-06-08T06:30:00", "records_count": 42},
        "foreclosure_sales": {"status": "healthy", "last_refresh": "2026-06-08T06:15:00", "records_count": 18},
        "tax_deed_sales": {"status": "healthy", "last_refresh": "2026-06-08T06:00:00", "records_count": 12},
        "parcel_master": {"status": "healthy", "last_refresh": "2026-06-08T05:45:00", "records_count": 312456},
        "tax_collector": {"status": "healthy", "last_refresh": "2026-06-08T05:30:00", "records_count": 2847},
        "gis_mapping": {"status": "healthy", "last_refresh": "2026-06-07T23:00:00", "records_count": 312456},
        "code_enforcement": {"status": "prr_required", "last_refresh": "2026-06-01T09:00:00", "records_count": 0}
    },
    "leads": [
        {
            "lead_id": "LEAD-001",
            "parcel_id": "DC-01-01-01-001-008",
            "score": 95,
            "score_reasons": ["Lis Pendens + Foreclosure Sale + Tax Delinquent", "3 stacked distress signals"],
            "address": "888 Pre foreclosure Ln, Jacksonville, FL 32210",
            "city": "Jacksonville",
            "zip": "32210",
            "owner_name": "Michael Brown",
            "owner_mailing_address": "888 Pre foreclosure Ln, Jacksonville, FL 32210",
            "signals": [
                {"type": "LIS_PENDENS", "source": "duval_court_records", "date": "2026-05-15", "confidence": 95, "details": "Foreclosure complaint filed by Wells Fargo Bank"},
                {"type": "FORECLOSURE_NOTICE", "source": "duval_official_records", "date": "2026-05-20", "confidence": 90, "details": "Sale scheduled for June 15, 2026"},
                {"type": "TAX_DELINQUENT", "source": "duval_tax_collector", "date": "2026-04-01", "confidence": 100, "details": "2025 property taxes unpaid, $3,200 due"}
            ],
            "deal_path": "wholesale",
            "deal_path_confidence": 90,
            "status": "active",
            "last_updated": "2026-06-08T06:30:00",
            "assessed_value": 120000,
            "equity_estimate": 35000
        },
        {
            "lead_id": "LEAD-002",
            "parcel_id": "DC-01-01-01-001-009",
            "score": 92,
            "score_reasons": ["Tax Delinquent + Tax Deed Sale + Code Violation", "High distress, motivated seller"],
            "address": "999 Tax Delinquent Dr, Jacksonville, FL 32211",
            "city": "Jacksonville",
            "zip": "32211",
            "owner_name": "Sarah Davis",
            "owner_mailing_address": "999 Tax Delinquent Dr, Jacksonville, FL 32211",
            "signals": [
                {"type": "TAX_DELINQUENT", "source": "duval_tax_collector", "date": "2026-04-01", "confidence": 100, "details": "2025 taxes unpaid, $2,850 due"},
                {"type": "TAX_DEED_SALE", "source": "duval_tax_deed_sales", "date": "2026-06-01", "confidence": 85, "details": "Sale scheduled July 6, 2026"},
                {"type": "CODE_VIOLATION", "source": "duval_code_enforcement", "date": "2026-05-10", "confidence": 80, "details": "Overgrown vegetation, possible vacancy"}
            ],
            "deal_path": "sub_to",
            "deal_path_confidence": 85,
            "status": "active",
            "last_updated": "2026-06-08T06:30:00",
            "assessed_value": 95000,
            "equity_estimate": 20000
        },
        {
            "lead_id": "LEAD-003",
            "parcel_id": "DC-01-01-01-001-010",
            "score": 88,
            "score_reasons": ["Code Violation + Nuisance Lien + Eviction", "Rental property in distress"],
            "address": "111 Code Violation St, Jacksonville, FL 32206",
            "city": "Jacksonville",
            "zip": "32206",
            "owner_name": "DEF Rentals LLC",
            "owner_mailing_address": "111 Code Violation St, Jacksonville, FL 32206",
            "signals": [
                {"type": "CODE_VIOLATION", "source": "duval_code_enforcement", "date": "2026-04-15", "confidence": 95, "details": "Unsafe structure, multiple violations"},
                {"type": "NUISANCE_LIEN", "source": "duval_code_enforcement", "date": "2026-05-01", "confidence": 90, "details": "Lien recorded for $12,500 in unpaid fines"},
                {"type": "EVICTION", "source": "duval_court_records", "date": "2026-05-20", "confidence": 90, "details": "Eviction filed against tenant"}
            ],
            "deal_path": "rental_acquisition",
            "deal_path_confidence": 80,
            "status": "active",
            "last_updated": "2026-06-08T06:30:00",
            "assessed_value": 75000,
            "equity_estimate": 15000
        }
    ]
}

# Create data directory
os.makedirs("data", exist_ok=True)

with open("data/leads.json", "w") as f:
    json.dump(sample_leads_data, f, indent=2)

print("Created: data/leads.json")

# Create a README for the dashboard
readme_content = """# Duval County Lead Intelligence Dashboard

## Overview
This dashboard displays real estate distress signals and lead intelligence for Duval County, Florida (Jacksonville & Beaches area).

## Data Sources
- **Official Records** (or.duvalclerk.com) - Recorded documents since 1988
- **Court Records (CORE)** (core.duvalclerk.com) - Court cases and dockets
- **Foreclosure Sales** (duval.realforeclose.com) - Online foreclosure auctions
- **Tax Deed Sales** (duval.realtaxdeed.com) - Tax deed auctions
- **Property Appraiser** (paopropertysearch.coj.net) - Parcel and assessment data
- **Tax Collector** (tclieninfo.coj.net) - Tax lien information
- **GIS Mapping** (maps.coj.net/duvalproperty) - Property maps and layers
- **Code Enforcement** (jacksonville.gov) - Municipal code compliance

## Lead Scoring
Leads are scored 0-100 based on:
- Signal stack depth (number of distress signals)
- Signal recency
- Signal confidence
- Property equity estimate
- Deal path viability

## Deal Paths
- **Wholesale** - Quick flip to investor buyers
- **Sub-To** - Subject-to existing financing
- **Seller Finance** - Owner financing arrangement
- **Flip** - Renovation and resale
- **Rental Acquisition** - Buy and hold strategy
- **Probate** - Estate property acquisition
- **REO** - Bank-owned property
- **Creative Finance** - Non-traditional financing
- **Commercial** - Commercial property deals

## Refresh Schedule
- P0 Sources (Official Records, Court, Foreclosure, Tax Deed): Daily
- P1 Sources (Tax Collector, Code Enforcement): Weekly
- P2 Sources (Property Appraiser, GIS): Monthly

## Framework Version
v5.3.1 - Xcerebro County Intelligence Framework

## Deployment
This dashboard is hosted on GitHub Pages from the `duval-intel` repository.
"""

with open("dashboard/README.md", "w") as f:
    f.write(readme_content)

print("Created: dashboard/README.md")

print("\nDashboard created successfully!")
print("Files:")
print("  - dashboard/index.html")
print("  - dashboard/README.md")
print("  - data/leads.json")
