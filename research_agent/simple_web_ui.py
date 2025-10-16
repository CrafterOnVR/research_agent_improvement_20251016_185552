#!/usr/bin/env python3
"""
Simple Flask Web UI for ARINN Research Agent

A clean, simple web interface without timer functionality.
"""

from flask import Flask, render_template_string, request, jsonify
import os
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

try:
    # Try relative imports first (for package execution)
    from .enhanced_agent import EnhancedResearchAgent
    from .super_enhanced_agent import SuperEnhancedResearchAgent
except ImportError:
    # Fallback to absolute imports (for direct execution)
    from enhanced_agent import EnhancedResearchAgent
    from super_enhanced_agent import SuperEnhancedResearchAgent

app = Flask(__name__)

# Global agent instance
agent = None

def get_agent():
    """Get or create agent instance."""
    global agent
    if agent is None:
        # Create super enhanced agent by default
        agent = SuperEnhancedResearchAgent()
    return agent

@app.route('/')
def index():
    """Main research interface."""
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>ARINN - Super Enhanced Research Agent</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 20px;
                min-height: 100vh;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
            }
            .logo {
                font-size: 3em;
                margin-bottom: 10px;
            }
            .subtitle {
                color: #666;
                font-size: 1.2em;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
                color: #333;
            }
            input[type="text"], textarea, select {
                width: 100%;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 16px;
                transition: border-color 0.3s;
            }
            input[type="text"]:focus, textarea:focus, select:focus {
                outline: none;
                border-color: #667eea;
            }
            textarea {
                min-height: 100px;
                resize: vertical;
            }
            .checkbox-group {
                display: flex;
                align-items: center;
                margin: 15px 0;
            }
            .checkbox-group input {
                width: auto;
                margin-right: 10px;
            }
            .button-group {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                margin: 20px 0;
            }
            button {
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s;
                flex: 1;
                min-width: 150px;
            }
            .btn-primary {
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
            }
            .btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            .btn-secondary {
                background: #f8f9fa;
                color: #333;
                border: 2px solid #ddd;
            }
            .btn-secondary:hover {
                background: #e9ecef;
            }
            .results {
                margin-top: 30px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 8px;
                border-left: 4px solid #667eea;
            }
            .status {
                padding: 10px;
                margin: 10px 0;
                border-radius: 5px;
                font-weight: bold;
            }
            .status.success {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .status.error {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            .loading {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-right: 10px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">🤖 ARINN</div>
                <div class="subtitle">Super Enhanced Research Agent</div>
            </div>

            <form method="POST" action="/research">
                <div class="form-group">
                    <label for="topic">Research Topic:</label>
                    <input type="text" id="topic" name="topic" placeholder="Enter your research topic..." required>
                </div>

                <div class="form-group">
                    <label for="method">Research Method:</label>
                    <select id="method" name="method">
                        <option value="comprehensive">Comprehensive Research</option>
                        <option value="super">Super Intelligent Research</option>
                        <option value="time_based">Time-Based Research (1h + 24h)</option>
                    </select>
                </div>

                <div class="checkbox-group">
                    <input type="checkbox" id="super_intelligence" name="super_intelligence" checked>
                    <label for="super_intelligence">Enable Super Intelligence Features</label>
                </div>

                <div class="checkbox-group">
                    <input type="checkbox" id="ask_definition" name="ask_definition">
                    <label for="ask_definition">Ask Definition Question First</label>
                </div>

                <div class="button-group">
                    <button type="submit" class="btn-primary" id="research-btn">
                        🚀 Start Research
                    </button>
                    <button type="button" class="btn-secondary" onclick="saveResults()">
                        💾 Save Results
                    </button>
                    <button type="button" class="btn-secondary" onclick="loadResults()">
                        📂 Load Results
                    </button>
                </div>
            </form>

            <div id="results-container"></div>
        </div>

        <script>
            const form = document.querySelector('form');
            const researchBtn = document.getElementById('research-btn');
            const resultsContainer = document.getElementById('results-container');

            form.addEventListener('submit', async (e) => {
                e.preventDefault();

                researchBtn.innerHTML = '<span class="loading"></span>Researching...';
                researchBtn.disabled = true;

                const formData = new FormData(form);

                try {
                    const response = await fetch('/research', {
                        method: 'POST',
                        body: formData
                    });

                    const result = await response.json();

                    if (result.success) {
                        displayResults(result);
                    } else {
                        displayError(result.error || 'Research failed');
                    }
                } catch (error) {
                    displayError('Network error: ' + error.message);
                } finally {
                    researchBtn.innerHTML = '🚀 Start Research';
                    researchBtn.disabled = false;
                }
            });

            function displayResults(result) {
                let html = '<div class="results">';
                html += '<h3>Research Results</h3>';

                if (result.topic) {
                    html += `<p><strong>Topic:</strong> ${result.topic}</p>`;
                }

                if (result.intelligence_level) {
                    html += `<p><strong>Intelligence Level:</strong> ${result.intelligence_level}</p>`;
                }

                if (result.intelligence_score) {
                    html += `<p><strong>Intelligence Score:</strong> ${result.intelligence_score.toFixed(1)}/100</p>`;
                }

                if (result.research_phases) {
                    html += '<h4>Research Phases:</h4>';
                    for (const [phase, data] of Object.entries(result.research_phases)) {
                        html += `<h5>${phase.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase())}</h5>`;
                        if (typeof data === 'object' && data !== null) {
                            html += '<ul>';
                            for (const [key, value] of Object.entries(data)) {
                                if (Array.isArray(value) && value.length > 3) {
                                    html += `<li><strong>${key}:</strong> ${value.length} items</li>`;
                                } else {
                                    html += `<li><strong>${key}:</strong> ${JSON.stringify(value).substring(0, 100)}...</li>`;
                                }
                            }
                            html += '</ul>';
                        } else {
                            html += `<p>${String(data).substring(0, 200)}...</p>`;
                        }
                    }
                }

                html += '</div>';
                resultsContainer.innerHTML = html;
            }

            function displayError(error) {
                resultsContainer.innerHTML = `
                    <div class="status error">
                        <strong>Error:</strong> ${error}
                    </div>
                `;
            }

            function saveResults() {
                alert('Save functionality not yet implemented in web UI');
            }

            function loadResults() {
                alert('Load functionality not yet implemented in web UI');
            }
        </script>
    </body>
    </html>
    '''
    return html

@app.route('/research', methods=['POST'])
def research():
    """Handle research requests."""
    try:
        topic = request.form.get('topic', '').strip()
        method = request.form.get('method', 'comprehensive')
        super_intelligence = request.form.get('super_intelligence') == 'on'
        ask_definition = request.form.get('ask_definition') == 'on'

        if not topic:
            return jsonify({'success': False, 'error': 'Topic is required'})

        # Get agent
        if super_intelligence:
            research_agent = SuperEnhancedResearchAgent()
        else:
            research_agent = EnhancedResearchAgent()

        # Configure research
        config = {}
        if ask_definition:
            config['ask_definition_first'] = True

        # Perform research based on method
        if method == 'time_based':
            results = research_agent.time_based_research(topic, config)
        elif method == 'super':
            results = research_agent.super_intelligent_research(topic)
        else:
            results = research_agent.comprehensive_research(topic)

        # Convert results to JSON-serializable format
        json_results = {
            'success': True,
            'topic': results.get('topic'),
            'intelligence_level': results.get('intelligence_level'),
            'intelligence_score': results.get('intelligence_score'),
            'timestamp': results.get('timestamp'),
            'research_phases': {}
        }

        # Convert research phases
        phases = results.get('research_phases', {})
        for phase_name, phase_data in phases.items():
            if hasattr(phase_data, '__dict__'):
                json_results['research_phases'][phase_name] = str(phase_data)
            elif isinstance(phase_data, dict):
                json_results['research_phases'][phase_name] = phase_data
            else:
                json_results['research_phases'][phase_name] = str(phase_data)

        return jsonify(json_results)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("Starting ARINN Simple Web UI...")
    print("Interface: http://localhost:5000")
    print("Press Ctrl+C to stop")
    app.run(debug=True, host='localhost', port=5000)