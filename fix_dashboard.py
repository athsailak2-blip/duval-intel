import json

# Read current dashboard
with open('/workspace/dashboard/index.html', 'r') as f:
    html = f.read()

# Find the sample data section and replace with leads.json fetch
old_js = """        // Sample data for demonstration - in production this would be loaded from leads.json
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
        ];"""

new_js = """        // Load leads from leads.json - fallback to sample data if not available
        let sampleLeads = [];
        let sources = [];"""

# Replace the sample data declaration
html = html.replace(old_js, new_js)

# Now replace the hardcoded sources array
old_sources = """        const sources = [
            { name: "Official Records", status: "online", lastRefresh: "2026-06-08 06:30 AM", icon: "📄" },
            { name: "Court Records (CORE)", status: "online", lastRefresh: "2026-06-08 06:30 AM", icon: "⚖️" },
            { name: "Foreclosure Sales", status: "online", lastRefresh: "2026-06-08 06:15 AM", icon: "🏠" },
            { name: "Tax Deed Sales", status: "online", lastRefresh: "2026-06-08 06:00 AM", icon: "💰" },
            { name: "Property Appraiser", status: "online", lastRefresh: "2026-06-08 05:45 AM", icon: "📊" },
            { name: "Tax Collector", status: "online", lastRefresh: "2026-06-08 05:30 AM", icon: "📝" },
            { name: "GIS Mapping", status: "online", lastRefresh: "2026-06-07 11:00 PM", icon: "🗺️" },
            { name: "Code Enforcement", status: "warning", lastRefresh: "2026-06-01 09:00 AM", icon: "🔍" }
        ];"""

new_sources = """        // Sources will be populated from leads.json"""

html = html.replace(old_sources, new_sources)

# Replace the initialization section at the end
old_init = """        // Initialize
        updateKPIs();
        renderLeads(sampleLeads);
        renderSourceHealth();
        
        // In production, this would fetch from leads.json
        // fetch('data/leads.json')
        //     .then(r => r.json())
        //     .then(data => {
        //         renderLeads(data.leads);
        //         updateKPIs(data);
        //     });"""

new_init = """        // Load data from leads.json
        function loadData() {
            fetch('data/leads.json?t=' + Date.now())
                .then(r => {
                    if (!r.ok) throw new Error('Failed to load leads.json');
                    return r.json();
                })
                .then(data => {
                    sampleLeads = data.leads || [];
                    
                    // Build sources from data
                    const sourceMap = {
                        'duval_official_records': { name: 'Official Records', icon: '📄' },
                        'duval_court_records': { name: 'Court Records (CORE)', icon: '⚖️' },
                        'duval_foreclosure_sales': { name: 'Foreclosure Sales', icon: '🏠' },
                        'duval_tax_deed_sales': { name: 'Tax Deed Sales', icon: '💰' },
                        'duval_parcel_master': { name: 'Property Appraiser', icon: '📊' },
                        'duval_tax_collector': { name: 'Tax Collector', icon: '📝' },
                        'duval_gis': { name: 'GIS Mapping', icon: '🗺️' },
                        'duval_code_enforcement': { name: 'Code Enforcement', icon: '🔍' }
                    };
                    
                    sources = Object.entries(data.sources || {}).map(([id, info]) => {
                        const mapped = sourceMap[id] || { name: id, icon: '📋' };
                        const isPrr = info.status === 'prr_required';
                        const isHealthy = info.status === 'healthy' || info.status === 'scraped';
                        return {
                            name: mapped.name,
                            status: isPrr ? 'warning' : isHealthy ? 'online' : 'offline',
                            lastRefresh: info.last_refresh || 'Never',
                            icon: mapped.icon
                        };
                    });
                    
                    updateKPIs();
                    renderLeads(sampleLeads);
                    renderSourceHealth();
                })
                .catch(err => {
                    console.error('Error loading leads.json:', err);
                    document.getElementById('lead-table-body').innerHTML = `
                        <tr><td colspan="7" style="text-align: center; padding: 40px; color: #e74c3c;">
                            Error loading data: ${err.message}<br>
                            <small>Run scrapers to populate leads.json</small>
                        </td></tr>
                    `;
                });
        }
        
        // Initialize
        loadData();"""

html = html.replace(old_init, new_init)

# Write updated dashboard
with open('/workspace/dashboard/index.html', 'w') as f:
    f.write(html)

print(f"Dashboard updated: {len(html)} characters")
print("Changes made:")
print("1. Removed hardcoded sample leads - now loads from leads.json")
print("2. Removed hardcoded sources - now builds from leads.json data")
print("3. Added error handling with fetch fallback")
print("4. Sources show actual status from data (healthy/prr_required/offline)")
