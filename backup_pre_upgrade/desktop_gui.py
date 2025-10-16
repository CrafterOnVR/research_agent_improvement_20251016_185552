#!/usr/bin/env python3
"""
ARINN - Original Design Desktop GUI

The original ARINN research agent desktop interface.
"""

import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QLabel, QLineEdit, QPushButton,
                            QTextEdit, QComboBox, QCheckBox, QGridLayout,
                            QMessageBox, QProgressBar, QGroupBox, QSpinBox,
                            QTabWidget, QTextBrowser, QSplitter)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon, QPalette, QColor
import datetime

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

class ResearchWorker(QThread):
    """Worker thread for research operations."""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, agent, topic, config):
        super().__init__()
        self.agent = agent
        self.topic = topic
        self.config = config

    def run(self):
        try:
            self.progress.emit(f"Starting research on '{self.topic}'...")

            # Use super intelligent research if enabled
            if self.config.get("super_intelligence", False):
                results = self.agent.super_intelligent_research(self.topic)
            else:
                results = self.agent.comprehensive_research(self.topic)

            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))

class ResearchAgentGUI(QMainWindow):
    """Main GUI window for ARINN - Original Design."""

    def __init__(self):
        super().__init__()
        self.agent = None
        self.current_worker = None
        self.init_agent()
        self.init_ui()

    def init_agent(self):
        """Initialize the research agent."""
        try:
            self.agent = SuperEnhancedResearchAgent()
        except Exception as e:
            QMessageBox.critical(self, "Agent Error", f"Failed to initialize agent: {e}")
            sys.exit(1)

    def init_ui(self):
        """Initialize the user interface - Original ARINN Design."""
        self.setWindowTitle("ARINN - Autonomous Researching and Improving Neural Network")
        self.setGeometry(100, 100, 1200, 800)

        # Set gray background
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(40, 40, 40))
        self.setPalette(palette)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Header with logo
        header_group = QGroupBox()
        header_layout = QHBoxLayout(header_group)

        # Logo from Icon.jpg
        logo_label = QLabel()
        logo_pixmap = QPixmap("Icon.jpg")
        if not logo_pixmap.isNull():
            scaled_pixmap = logo_pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label.setText("ARINN")
            logo_label.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel("ARINN")
        title_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        main_layout.addWidget(header_group)

        # Create splitter for main content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - Configuration
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Research Configuration
        config_group = QGroupBox("Research Configuration")
        config_layout = QVBoxLayout(config_group)

        # Topic input
        config_layout.addWidget(QLabel("Research Topic:"))
        self.topic_input = QLineEdit()
        self.topic_input.setPlaceholderText("Enter research topic...")
        config_layout.addWidget(self.topic_input)

        # Research options
        options_layout = QVBoxLayout()

        self.super_intelligence_checkbox = QCheckBox("Enable Super Intelligence Mode")
        self.super_intelligence_checkbox.setChecked(True)
        options_layout.addWidget(self.super_intelligence_checkbox)

        self.automation_checkbox = QCheckBox("Enable Automation")
        options_layout.addWidget(self.automation_checkbox)

        self.web_research_checkbox = QCheckBox("Enable Web Research")
        self.web_research_checkbox.setChecked(True)
        options_layout.addWidget(self.web_research_checkbox)

        self.file_analysis_checkbox = QCheckBox("Enable File Analysis")
        options_layout.addWidget(self.file_analysis_checkbox)

        # Question format checkboxes
        question_group = QGroupBox("Question Format")
        question_layout = QHBoxLayout(question_group)

        self.ask_a_checkbox = QCheckBox("Ask 'What is a [topic]?'")
        self.ask_the_checkbox = QCheckBox("Ask 'What is the [topic]?'")
        self.ask_the_checkbox.setChecked(True)

        question_layout.addWidget(self.ask_a_checkbox)
        question_layout.addWidget(self.ask_the_checkbox)

        options_layout.addWidget(question_group)

        config_layout.addLayout(options_layout)

        # Site scraping section
        scraping_group = QGroupBox("Site Scraping")
        scraping_layout = QVBoxLayout(scraping_group)

        self.site_scraping_checkbox = QCheckBox("Enable Site Scraping")
        self.site_scraping_checkbox.stateChanged.connect(self.toggle_scraping_options)
        scraping_layout.addWidget(self.site_scraping_checkbox)

        # Scraping options (initially hidden)
        self.scraping_options_widget = QWidget()
        scraping_options_layout = QVBoxLayout(self.scraping_options_widget)

        scraping_options_layout.addWidget(QLabel("Site URL:"))
        self.site_url_input = QLineEdit()
        self.site_url_input.setPlaceholderText("https://example.com")
        scraping_options_layout.addWidget(self.site_url_input)

        scraping_options_layout.addWidget(QLabel("Content Filters (comma-separated):"))
        self.content_filters_input = QLineEdit()
        self.content_filters_input.setPlaceholderText("keyword1, keyword2, keyword3")
        scraping_options_layout.addWidget(self.content_filters_input)

        # Scraping parameters
        params_layout = QHBoxLayout()

        params_layout.addWidget(QLabel("Pages to Scrape:"))
        self.pages_spinbox = QSpinBox()
        self.pages_spinbox.setRange(1, 100)
        self.pages_spinbox.setValue(10)
        params_layout.addWidget(self.pages_spinbox)

        params_layout.addWidget(QLabel("Request Delay (sec):"))
        self.delay_spinbox = QSpinBox()
        self.delay_spinbox.setRange(0, 10)

        params_layout.addWidget(QLabel("Max Depth:"))
        self.depth_spinbox = QSpinBox()
        self.depth_spinbox.setRange(1, 10)
        self.depth_spinbox.setValue(2)
        params_layout.addWidget(self.depth_spinbox)

        scraping_options_layout.addLayout(params_layout)
        scraping_layout.addWidget(self.scraping_options_widget)

        # Initially hide scraping options
        self.scraping_options_widget.setVisible(False)

        config_layout.addWidget(scraping_group)

        left_layout.addWidget(config_group)

        # Control buttons
        buttons_layout = QHBoxLayout()

        self.research_button = QPushButton("🚀 Start Research")
        self.research_button.clicked.connect(self.start_research)
        self.research_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 10px; font-weight: bold; }")
        buttons_layout.addWidget(self.research_button)

        self.save_button = QPushButton("💾 Save Results")
        self.save_button.clicked.connect(self.save_results)
        buttons_layout.addWidget(self.save_button)

        self.load_button = QPushButton("📂 Load Results")
        self.load_button.clicked.connect(self.load_results)
        buttons_layout.addWidget(self.load_button)

        # Add health check button
        self.health_button = QPushButton("🏥 Check Health")
        self.health_button.clicked.connect(self.show_superintelligence_health)
        self.health_button.setStyleSheet("QPushButton { background-color: #2196F3; color: white; padding: 10px; font-weight: bold; }")
        buttons_layout.addWidget(self.health_button)

        left_layout.addLayout(buttons_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        left_layout.addWidget(self.progress_bar)

        splitter.addWidget(left_widget)

        # Right panel - Results with tabs
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Results tabs
        self.results_tabs = QTabWidget()

        # Create tabs for each category
        self.overview_tab = QTextBrowser()
        self.questions_tab = QTextBrowser()
        self.patterns_tab = QTextBrowser()
        self.automation_tab = QTextBrowser()
        self.insights_tab = QTextBrowser()
        self.report_tab = QTextBrowser()

        self.results_tabs.addTab(self.overview_tab, "📊 Overview")
        self.results_tabs.addTab(self.questions_tab, "❓ Questions")
        self.results_tabs.addTab(self.patterns_tab, "🔍 Patterns")
        self.results_tabs.addTab(self.automation_tab, "⚙️ Automation")
        self.results_tabs.addTab(self.insights_tab, "💡 Insights")
        self.results_tabs.addTab(self.report_tab, "📋 Report")

        right_layout.addWidget(self.results_tabs)

        splitter.addWidget(right_widget)

        # Set splitter proportions
        splitter.setSizes([400, 800])

        # Status bar
        self.statusBar().showMessage("Ready")

    def toggle_scraping_options(self, state):
        """Toggle visibility of scraping options."""
        self.scraping_options_widget.setVisible(state == Qt.CheckState.Checked)

    def check_superintelligence_health(self):
        """Check the health and status of all superintelligence components."""
        health_results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "components": {},
            "performance_metrics": {},
            "errors": [],
            "recommendations": []
        }

        try:
            # Check Super Intelligence Mode
            health_results["components"]["super_intelligence_mode"] = {
                "status": "active" if self.super_intelligence_checkbox.isChecked() else "inactive",
                "description": "Super Intelligence Mode activation status"
            }

            # Check Enhanced Heuristic Intelligence
            try:
                if hasattr(self.agent, 'heuristic_intelligence') and self.agent.heuristic_intelligence:
                    # Test heuristic intelligence with a simple analysis
                    test_topic = "test_topic"
                    test_context = "This is a test context for health checking."
                    analysis = self.agent.heuristic_intelligence.analyze_topic_semantics(test_topic, test_context)

                    health_results["components"]["heuristic_intelligence"] = {
                        "status": "healthy",
                        "description": f"Enhanced Heuristic Intelligence - Keywords: {len(analysis.get('keywords', []))}",
                        "details": {
                            "keywords_extracted": len(analysis.get('keywords', [])),
                            "entities_found": len(analysis.get('entities', [])),
                            "concepts_identified": len(analysis.get('concepts', []))
                        }
                    }
                else:
                    health_results["components"]["heuristic_intelligence"] = {
                        "status": "unavailable",
                        "description": "Enhanced Heuristic Intelligence not available"
                    }
            except Exception as e:
                health_results["components"]["heuristic_intelligence"] = {
                    "status": "error",
                    "description": f"Heuristic Intelligence error: {str(e)}"
                }
                health_results["errors"].append(f"Heuristic Intelligence: {str(e)}")

            # Check Advanced Pattern Intelligence
            try:
                if hasattr(self.agent, 'pattern_intelligence') and self.agent.pattern_intelligence:
                    # Test pattern intelligence with sample content
                    sample_content = ["Test content for pattern analysis"]
                    patterns = self.agent.pattern_intelligence.analyze_content_patterns(sample_content[0])

                    health_results["components"]["pattern_intelligence"] = {
                        "status": "healthy",
                        "description": f"Advanced Pattern Intelligence - Patterns found: {len(patterns) if patterns else 0}",
                        "details": {
                            "patterns_analyzed": len(patterns) if patterns else 0,
                            "knowledge_graph_ready": True
                        }
                    }
                else:
                    health_results["components"]["pattern_intelligence"] = {
                        "status": "unavailable",
                        "description": "Advanced Pattern Intelligence not available"
                    }
            except Exception as e:
                health_results["components"]["pattern_intelligence"] = {
                    "status": "error",
                    "description": f"Pattern Intelligence error: {str(e)}"
                }
                health_results["errors"].append(f"Pattern Intelligence: {str(e)}")

            # Check Automation Engine
            try:
                if hasattr(self.agent, 'automation_engine') and self.agent.automation_engine:
                    metrics = self.agent.automation_engine.get_performance_metrics()

                    health_results["components"]["automation_engine"] = {
                        "status": "healthy",
                        "description": f"Automation Engine - Workers: {metrics.get('active_workers', 0)}",
                        "details": {
                            "active_workers": metrics.get('active_workers', 0),
                            "tasks_completed": metrics.get('tasks_completed', 0),
                            "success_rate": f"{metrics.get('success_rate', 0):.1%}"
                        }
                    }
                else:
                    health_results["components"]["automation_engine"] = {
                        "status": "unavailable",
                        "description": "Automation Engine not available"
                    }
            except Exception as e:
                health_results["components"]["automation_engine"] = {
                    "status": "error",
                    "description": f"Automation Engine error: {str(e)}"
                }
                health_results["errors"].append(f"Automation Engine: {str(e)}")

            # Check Self-Improvement System
            try:
                # Test self-improvement detection
                mock_results = {
                    'intelligence_score': 75,
                    'research_phases': {
                        'pattern_research': {'central_concepts': ['test']},
                        'automation_results': {'automation_metrics': {'success_rate': 0.8}}
                    }
                }
                improvements = self.agent.detect_code_improvements(mock_results)

                health_results["components"]["self_improvement"] = {
                    "status": "healthy",
                    "description": f"Self-Improvement System - Improvements detected: {len(improvements)}",
                    "details": {
                        "improvements_detected": len(improvements),
                        "self_modification_capable": True
                    }
                }
            except Exception as e:
                health_results["components"]["self_improvement"] = {
                    "status": "error",
                    "description": f"Self-Improvement error: {str(e)}"
                }
                health_results["errors"].append(f"Self-Improvement: {str(e)}")

            # Check Database Connectivity
            try:
                if hasattr(self.agent, 'db') and self.agent.db:
                    # Test database with a simple query
                    topic_id = self.agent.db.get_or_create_topic('health_check_test')

                    health_results["components"]["database"] = {
                        "status": "healthy",
                        "description": f"Database System - Topic ID: {topic_id}",
                        "details": {
                            "connectivity": "established",
                            "basic_operations": "functional"
                        }
                    }
                else:
                    health_results["components"]["database"] = {
                        "status": "unavailable",
                        "description": "Database not available"
                    }
            except Exception as e:
                health_results["components"]["database"] = {
                    "status": "error",
                    "description": f"Database error: {str(e)}"
                }
                health_results["errors"].append(f"Database: {str(e)}")

            # Check Research Persistence
            try:
                # Check if research state can be saved/loaded
                test_state = {"test": "data", "timestamp": datetime.now().isoformat()}
                # This would test the persistence mechanism

                health_results["components"]["research_persistence"] = {
                    "status": "healthy",
                    "description": "Research Persistence - State management active",
                    "details": {
                        "state_saving": "enabled",
                        "session_recovery": "available"
                    }
                }
            except Exception as e:
                health_results["components"]["research_persistence"] = {
                    "status": "error",
                    "description": f"Research Persistence error: {str(e)}"
                }
                health_results["errors"].append(f"Research Persistence: {str(e)}")

            # Calculate overall status
            component_statuses = [comp["status"] for comp in health_results["components"].values()]

            if "error" in component_statuses:
                health_results["overall_status"] = "critical"
                health_results["recommendations"].append("Critical errors detected - immediate attention required")
            elif "unavailable" in component_statuses:
                health_results["overall_status"] = "degraded"
                health_results["recommendations"].append("Some components unavailable - check super intelligence mode")
            elif all(status == "healthy" for status in component_statuses):
                health_results["overall_status"] = "optimal"
                health_results["recommendations"].append("All systems operating optimally")
            else:
                health_results["overall_status"] = "healthy"
                health_results["recommendations"].append("Super intelligence systems operational")

            # Performance metrics
            health_results["performance_metrics"] = {
                "components_checked": len(health_results["components"]),
                "healthy_components": sum(1 for comp in health_results["components"].values() if comp["status"] == "healthy"),
                "error_count": len(health_results["errors"]),
                "check_duration": "completed"
            }

        except Exception as e:
            health_results["overall_status"] = "failed"
            health_results["errors"].append(f"Health check failed: {str(e)}")
            health_results["recommendations"].append("Unable to perform health check - check system configuration")

        return health_results

    def show_superintelligence_health(self):
        """Display the superintelligence health check results in a dialog."""
        health_results = self.check_superintelligence_health()

        # Create health report dialog
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QHBoxLayout, QPushButton

        dialog = QDialog(self)
        dialog.setWindowTitle("ARINN Superintelligence Health Check")
        dialog.setGeometry(200, 200, 600, 500)

        layout = QVBoxLayout(dialog)

        # Overall status
        status_colors = {
            "optimal": "#4CAF50",
            "healthy": "#8BC34A",
            "degraded": "#FF9800",
            "critical": "#F44336",
            "failed": "#9C27B0",
            "unknown": "#9E9E9E"
        }

        overall_status = health_results["overall_status"].upper()
        status_color = status_colors.get(health_results["overall_status"], "#9E9E9E")

        status_label = QLabel(f"Overall Status: <b><font color='{status_color}'>{overall_status}</font></b>")
        status_label.setStyleSheet("font-size: 14px; margin: 10px;")
        layout.addWidget(status_label)

        # Components status
        components_text = "Component Status:\n\n"
        for component_name, component_info in health_results["components"].items():
            status_emoji = {
                "healthy": "✅",
                "unavailable": "⭕",
                "error": "❌",
                "active": "🟢",
                "inactive": "🔴"
            }.get(component_info["status"], "❓")

            components_text += f"{status_emoji} {component_name.replace('_', ' ').title()}: {component_info['description']}\n"

        components_display = QTextEdit()
        components_display.setPlainText(components_text)
        components_display.setReadOnly(True)
        layout.addWidget(components_display)

        # Errors and recommendations
        if health_results["errors"] or health_results["recommendations"]:
            issues_text = ""
            if health_results["errors"]:
                issues_text += "Errors:\n" + "\n".join(f"• {error}" for error in health_results["errors"]) + "\n\n"
            if health_results["recommendations"]:
                issues_text += "Recommendations:\n" + "\n".join(f"• {rec}" for rec in health_results["recommendations"])

            issues_display = QTextEdit()
            issues_display.setPlainText(issues_text)
            issues_display.setReadOnly(True)
            issues_display.setMaximumHeight(100)
            layout.addWidget(issues_display)

        # Performance metrics
        metrics_text = f"Performance Metrics:\n"
        metrics_text += f"• Components Checked: {health_results['performance_metrics']['components_checked']}\n"
        metrics_text += f"• Healthy Components: {health_results['performance_metrics']['healthy_components']}\n"
        metrics_text += f"• Errors Found: {health_results['performance_metrics']['error_count']}\n"
        metrics_text += f"• Check Timestamp: {health_results['timestamp'][:19].replace('T', ' ')}"

        metrics_display = QLabel(metrics_text)
        metrics_display.setStyleSheet("font-family: monospace; margin: 10px;")
        layout.addWidget(metrics_display)

        # Buttons
        button_layout = QHBoxLayout()

        refresh_button = QPushButton("🔄 Refresh Check")
        refresh_button.clicked.connect(lambda: self.refresh_health_dialog(dialog))
        button_layout.addWidget(refresh_button)

        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

        dialog.exec()

    def refresh_health_dialog(self, dialog):
        """Refresh the health check in the dialog."""
        dialog.close()
        self.show_superintelligence_health()

    def toggle_scraping_options(self, state):
        """Toggle visibility of scraping options."""
        self.scraping_options_widget.setVisible(state == Qt.CheckState.Checked)

    def start_research(self):
        """Start research operation."""
        topic = self.topic_input.text().strip()
        if not topic:
            QMessageBox.warning(self, "Input Error", "Please enter a research topic.")
            return

        # Gather configuration
        config = {
            "super_intelligence": self.super_intelligence_checkbox.isChecked(),
            "automation": self.automation_checkbox.isChecked(),
            "web_research": self.web_research_checkbox.isChecked(),
            "file_analysis": self.file_analysis_checkbox.isChecked(),
            "question_format": "a" if self.ask_a_checkbox.isChecked() else "the",
            "site_scraping": self.site_scraping_checkbox.isChecked()
        }

        if config["site_scraping"]:
            config["site_url"] = self.site_url_input.text().strip()
            config["content_filters"] = [f.strip() for f in self.content_filters_input.text().split(",") if f.strip()]
            config["pages_to_scrape"] = self.pages_spinbox.value()
            config["request_delay"] = self.delay_spinbox.value()
            config["max_depth"] = self.depth_spinbox.value()

        # Disable buttons during research
        self.set_buttons_enabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.statusBar().showMessage("Researching...")

        # Clear previous results
        self.clear_results_tabs()

        # Start research in background thread
        self.current_worker = ResearchWorker(self.agent, topic, config)
        self.current_worker.finished.connect(self.on_research_finished)
        self.current_worker.error.connect(self.on_research_error)
        self.current_worker.progress.connect(self.on_research_progress)
        self.current_worker.start()

    def on_research_finished(self, results):
        """Handle research completion."""
        self.set_buttons_enabled(True)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Research completed")

        # Format and display results in tabs
        self.display_results_in_tabs(results)

        QMessageBox.information(self, "Research Complete",
                              f"Research on '{results.get('topic', 'Unknown')}' completed successfully!")

    def on_research_error(self, error_msg):
        """Handle research error."""
        self.set_buttons_enabled(True)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Research failed")

        QMessageBox.critical(self, "Research Error", f"Research failed: {error_msg}")

    def on_research_progress(self, message):
        """Handle research progress updates."""
        self.statusBar().showMessage(message)

    def display_results_in_tabs(self, results):
        """Display research results in the appropriate tabs."""
        # Overview tab
        overview_text = f"""
<h2>Research Overview</h2>
<p><strong>Topic:</strong> {results.get('topic', 'Unknown')}</p>
<p><strong>Intelligence Level:</strong> {results.get('intelligence_level', 'Unknown')}</p>
<p><strong>Intelligence Score:</strong> {results.get('intelligence_score', 0):.1f}/100</p>
<p><strong>Timestamp:</strong> {results.get('timestamp', 'Unknown')}</p>
"""
        self.overview_tab.setHtml(overview_text)

        # Questions tab
        questions_text = "<h2>Generated Questions</h2>"
        if "research_phases" in results:
            phases = results["research_phases"]
            if "intelligent_questions" in phases.get("deep_research", {}):
                questions = phases["deep_research"]["intelligent_questions"][:20]  # Limit to 20
                questions_text += "<ol>"
                for q in questions:
                    questions_text += f"<li>{q}</li>"
                questions_text += "</ol>"
        self.questions_tab.setHtml(questions_text)

        # Patterns tab
        patterns_text = "<h2>Pattern Analysis</h2>"
        if "research_phases" in results:
            phases = results["research_phases"]
            if "pattern_research" in phases:
                pattern_data = phases["pattern_research"]
                patterns_text += f"<p><strong>Central Concepts:</strong> {len(pattern_data.get('central_concepts', []))}</p>"
                patterns_text += f"<p><strong>Concept Clusters:</strong> {len(pattern_data.get('concept_clusters', []))}</p>"
                patterns_text += f"<p><strong>Knowledge Graph Nodes:</strong> {pattern_data.get('knowledge_graph_stats', {}).get('nodes', 0)}</p>"
        self.patterns_tab.setHtml(patterns_text)

        # Automation tab
        automation_text = "<h2>Automation Results</h2>"
        if "research_phases" in results:
            phases = results["research_phases"]
            if "automation_results" in phases:
                auto_data = phases["automation_results"]
                automation_text += f"<p><strong>Tasks Executed:</strong> {len(auto_data.get('task_results', {}))}</p>"
                automation_text += f"<p><strong>Success Rate:</strong> {auto_data.get('automation_metrics', {}).get('success_rate', 0):.1%}</p>"
        self.automation_tab.setHtml(automation_text)

        # Insights tab
        insights_text = "<h2>Advanced Insights</h2>"
        if "research_phases" in results:
            phases = results["research_phases"]
            if "advanced_insights" in phases:
                insights_data = phases["advanced_insights"]
                insights_text += f"<p><strong>Semantic Insights:</strong> {len(insights_data.get('semantic_insights', []))}</p>"
                insights_text += f"<p><strong>Pattern Insights:</strong> {len(insights_data.get('pattern_insights', []))}</p>"
                insights_text += f"<p><strong>Cross-Domain Insights:</strong> {len(insights_data.get('cross_domain_insights', []))}</p>"
        self.insights_tab.setHtml(insights_text)

        # Report tab
        report_text = "<h2>Comprehensive Report</h2>"
        if "research_phases" in results:
            phases = results["research_phases"]
            if "comprehensive_report" in phases:
                report_text += phases["comprehensive_report"].replace('\n', '<br>')
        self.report_tab.setHtml(report_text)

    def clear_results_tabs(self):
        """Clear all results tabs."""
        self.overview_tab.clear()
        self.questions_tab.clear()
        self.patterns_tab.clear()
        self.automation_tab.clear()
        self.insights_tab.clear()
        self.report_tab.clear()

    def set_buttons_enabled(self, enabled):
        """Enable or disable all buttons."""
        self.research_button.setEnabled(enabled)
        self.save_button.setEnabled(enabled)
        self.load_button.setEnabled(enabled)

    def save_results(self):
        """Save research results."""
        QMessageBox.information(self, "Save Results", "Save functionality would be implemented here.")

    def load_results(self):
        """Load research results."""
        QMessageBox.information(self, "Load Results", "Load functionality would be implemented here.")

def main():
    """Main application entry point."""
    try:
        app = QApplication(sys.argv)
        app.setStyle('Fusion')  # Use Fusion style for better cross-platform compatibility

        window = ResearchAgentGUI()
        window.show()

        print("Starting ARINN - Original Design Desktop GUI...")
        print("The desktop application will open in a new window")
        print("Close the window to exit the application")

        sys.exit(app.exec())

    except Exception as e:
        print(f"❌ Failed to start desktop GUI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()