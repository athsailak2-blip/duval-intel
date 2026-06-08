#!/usr/bin/env python3
"""Update dashboard with enhanced filtering - score range slider and deal path dropdown."""

# Read current dashboard
with open("/workspace/dashboard/index.html", "r") as f:
    dashboard = f.read()

# Find the filters section and replace it with enhanced filters
old_filters = '''            <div class="filters">
                <button class="filter-btn active" data-filter="all">All Leads</button>
                <button class="filter-btn" data-filter="high">High Stack (3+)</button>
                <button class="filter-btn" data-filter="foreclosure">Foreclosure</button>
                <button class="filter-btn" data-filter="tax">Tax Delinquent</button>
                <button class="filter-btn" data-filter="code">Code Violation</button>
                <button class="filter-btn" data-filter="probate">Probate/Estate</button>
            </div>'''

new_filters = '''            <div class="filters-row">
                <div class="filter-group">
                    <label>Signal Type</label>
                    <div class="filters" id="signal-filters">
                        <button class="filter-btn active" data-filter="all">All Leads</button>
                        <button class="filter-btn" data-filter="high">High Stack (3+)</button>
                        <button class="filter-btn" data-filter="foreclosure">Foreclosure</button>
                        <button class="filter-btn" data-filter="tax">Tax Delinquent</button>
                        <button class="filter-btn" data-filter="code">Code Violation</button>
                        <button class="filter-btn" data-filter="probate">Probate/Estate</button>
                    </div>
                </div>
                
                <div class="filter-group">
                    <label>Deal Path</label>
                    <select class="filter-select" id="deal-path-filter">
                        <option value="all">All Deal Paths</option>
                        <option value="wholesale">Wholesale</option>
                        <option value="sub_to">Subject To</option>
                        <option value="rental_acquisition">Rental Acquisition</option>
                        <option value="probate">Probate</option>
                        <option value="creative_finance">Creative Finance</option>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label>Score Range: <span id="score-range-value">0 - 100</span></label>
                    <div class="score-range-slider">
                        <input type="range" id="score-min" min="0" max="100" value="0" class="range-slider">
                        <input type="range" id="score-max" min="0" max="100" value="100" class="range-slider">
                    </div>
                </div>
            </div>'''

dashboard = dashboard.replace(old_filters, new_filters)

# Add CSS for new filter elements
old_css = '''        .filters {
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
        }'''

new_css = '''        .filters-row {
            display: flex;
            gap: 24px;
            margin-bottom: 20px;
            flex-wrap: wrap;
            align-items: flex-end;
        }
        
        .filter-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .filter-group label {
            font-size: 12px;
            font-weight: 600;
            color: #7f8c8d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .filters {
            display: flex;
            gap: 8px;
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
        
        .filter-select {
            padding: 8px 16px;
            border: 1px solid #d5dbdb;
            border-radius: 8px;
            background: white;
            color: #5d6d7e;
            font-size: 13px;
            cursor: pointer;
            min-width: 180px;
        }
        
        .filter-select:focus {
            outline: none;
            border-color: #1a5276;
        }
        
        .score-range-slider {
            display: flex;
            align-items: center;
            gap: 8px;
            width: 200px;
        }
        
        .range-slider {
            -webkit-appearance: none;
            appearance: none;
            height: 6px;
            border-radius: 3px;
            background: #d5dbdb;
            outline: none;
            flex: 1;
        }
        
        .range-slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #1a5276;
            cursor: pointer;
        }
        
        .range-slider::-moz-range-thumb {
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #1a5276;
            cursor: pointer;
            border: none;
        }'''

dashboard = dashboard.replace(old_css, new_css)

# Update the JavaScript filter functionality
old_js = '''        // Filter functionality
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
        });'''

new_js = '''        // Current filter state
        let currentFilters = {
            signal: 'all',
            dealPath: 'all',
            scoreMin: 0,
            scoreMax: 100
        };
        
        function applyFilters() {
            let filtered = sampleLeads;
            
            // Signal type filter
            if (currentFilters.signal === 'high') {
                filtered = filtered.filter(l => l.signals.length >= 3);
            } else if (currentFilters.signal === 'foreclosure') {
                filtered = filtered.filter(l => l.signals.some(s => s.type === 'foreclosure'));
            } else if (currentFilters.signal === 'tax') {
                filtered = filtered.filter(l => l.signals.some(s => s.type === 'tax'));
            } else if (currentFilters.signal === 'code') {
                filtered = filtered.filter(l => l.signals.some(s => s.type === 'code'));
            } else if (currentFilters.signal === 'probate') {
                filtered = filtered.filter(l => l.signals.some(s => s.type === 'probate' || s.type === 'estate'));
            }
            
            // Deal path filter
            if (currentFilters.dealPath !== 'all') {
                filtered = filtered.filter(l => l.dealPath === currentFilters.dealPath || l.deal_path === currentFilters.dealPath);
            }
            
            // Score range filter
            filtered = filtered.filter(l => {
                const score = l.score || 0;
                return score >= currentFilters.scoreMin && score <= currentFilters.scoreMax;
            });
            
            renderLeads(filtered);
        }
        
        // Signal filter buttons
        document.querySelectorAll('#signal-filters .filter-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('#signal-filters .filter-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                currentFilters.signal = this.dataset.filter;
                applyFilters();
            });
        });
        
        // Deal path filter
        document.getElementById('deal-path-filter').addEventListener('change', function() {
            currentFilters.dealPath = this.value;
            applyFilters();
        });
        
        // Score range sliders
        const scoreMinSlider = document.getElementById('score-min');
        const scoreMaxSlider = document.getElementById('score-max');
        const scoreRangeValue = document.getElementById('score-range-value');
        
        function updateScoreRange() {
            let min = parseInt(scoreMinSlider.value);
            let max = parseInt(scoreMaxSlider.value);
            
            if (min > max) {
                [min, max] = [max, min];
            }
            
            currentFilters.scoreMin = min;
            currentFilters.scoreMax = max;
            scoreRangeValue.textContent = `${min} - ${max}`;
            applyFilters();
        }
        
        scoreMinSlider.addEventListener('input', updateScoreRange);
        scoreMaxSlider.addEventListener('input', updateScoreRange);'''

dashboard = dashboard.replace(old_js, new_js)

# Write updated dashboard
with open("/workspace/dashboard/index.html", "w") as f:
    f.write(dashboard)

print("Dashboard updated with enhanced filtering:")
print("- Signal type filter buttons (existing)")
print("- Deal path dropdown filter")
print("- Score range slider (0-100)")
print("- Combined filter logic that applies all filters together")
