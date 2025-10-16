#!/usr/bin/env python3
"""
Super Enhanced Research Agent Desktop GUI

A clean PyQt6 desktop interface for ARINN research agent.
"""

import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QLabel, QLineEdit, QPushButton,
                            QTextEdit, QComboBox, QCheckBox, QGridLayout,
                            QMessageBox, QProgressBar, QGroupBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon

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

    def __init__(self, agent, topic, method, super_intelligence):
        super().__init__()
        self.agent = agent
        self.topic = topic
        self.method = method
        self.super_intelligence = super_intelligence

    def run(self):
        try:
            self.progress.emit(f"Starting {self.method} research on '{self.topic}'...")

            if self.method == "comprehensive":
                results = self.agent.comprehensive_research(self.topic)
            elif self.method == "super":
                results = self.agent.super_intelligent_research(self.topic)
            elif self.method == "time_based":
                results = self.agent.time_based_research(self.topic)
            else:
                raise ValueError(f"Unknown research method: {self.method}")

            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))

class ResearchAgentGUI(QMainWindow):
    """Main GUI window for the research agent."""

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
        """Initialize the user interface."""
        self.setWindowTitle("🤖 ARINN - Super Enhanced Research Agent")
        self.setGeometry(100, 100, 1000, 700)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Header with logo
        header_group = QGroupBox()
        header_layout = QHBoxLayout(header_group)

        logo_label = QLabel("🤖")
        logo_label.setFont(QFont("Arial", 48))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel("ARINN")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle_label = QLabel("Super Enhanced Research Agent")
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)

        main_layout.addWidget(header_group)

        # Research input section
        input_group = QGroupBox("Research Configuration")
        input_layout = QGridLayout(input_group)

        # Topic input
        input_layout.addWidget(QLabel("Research Topic:"), 0, 0)
        self.topic_input = QLineEdit()
        self.topic_input.setPlaceholderText("Enter your research topic...")
        input_layout.addWidget(self.topic_input, 0, 1)

        # Research method
        input_layout.addWidget(QLabel("Research Method:"), 1, 0)
        self.method_combo = QComboBox()
        self.method_combo.addItems([
            "Comprehensive Research",
            "Super Intelligent Research",
            "Time-Based Research (1h + 24h)"
        ])
        input_layout.addWidget(self.method_combo, 1, 1)

        # Super intelligence checkbox
        self.super_intelligence_checkbox = QCheckBox("Enable Super Intelligence Features")
        self.super_intelligence_checkbox.setChecked(True)
        input_layout.addWidget(self.super_intelligence_checkbox, 2, 0, 1, 2)

        main_layout.addWidget(input_group)

        # Buttons
        button_layout = QHBoxLayout()

        self.research_button = QPushButton("🚀 Start Research")
        self.research_button.clicked.connect(self.start_research)
        button_layout.addWidget(self.research_button)

        self.save_button = QPushButton("💾 Save Results")
        self.save_button.clicked.connect(self.save_results)
        button_layout.addWidget(self.save_button)

        self.load_button = QPushButton("📂 Load Results")
        self.load_button.clicked.connect(self.load_results)
        button_layout.addWidget(self.load_button)

        self.resume_button = QPushButton("🔄 Resume Research")
        self.resume_button.clicked.connect(self.resume_research)
        button_layout.addWidget(self.resume_button)

        self.image_button = QPushButton("🖼️ Analyze Images")
        self.image_button.clicked.connect(self.analyze_images)
        button_layout.addWidget(self.image_button)

        self.scrape_button = QPushButton("🎯 Web Scrape")
        self.scrape_button.clicked.connect(self.web_scrape)
        button_layout.addWidget(self.scrape_button)

        main_layout.addLayout(button_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Results area
        results_group = QGroupBox("Research Results")
        results_layout = QVBoxLayout(results_group)

        self.results_text = QTextEdit()
        self.results_text.setPlaceholderText("Research results will appear here...")
        results_layout.addWidget(self.results_text)

        main_layout.addWidget(results_group)

        # Status bar
        self.statusBar().showMessage("Ready")

        # Apply styling
        self.apply_styling()

    def apply_styling(self):
        """Apply custom styling to the GUI."""
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
            }

            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 5px;
                margin-top: 1ex;
                background: rgba(255, 255, 255, 0.9);
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }

            QPushButton {
                padding: 8px 16px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                min-width: 100px;
            }

            QPushButton:hover {
                transform: translateY(-1px);
            }

            QLineEdit, QComboBox, QTextEdit {
                padding: 5px;
                border: 2px solid #ddd;
                border-radius: 3px;
            }

            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
                border-color: #667eea;
            }
        """)

    def start_research(self):
        """Start research operation."""
        topic = self.topic_input.text().strip()
        if not topic:
            QMessageBox.warning(self, "Input Error", "Please enter a research topic.")
            return

        method_map = {
            "Comprehensive Research": "comprehensive",
            "Super Intelligent Research": "super",
            "Time-Based Research (1h + 24h)": "time_based"
        }

        method = method_map.get(self.method_combo.currentText(), "comprehensive")
        super_intelligence = self.super_intelligence_checkbox.isChecked()

        # Disable buttons during research
        self.set_buttons_enabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.statusBar().showMessage("Researching...")
        self.results_text.clear()

        # Start research in background thread
        self.current_worker = ResearchWorker(self.agent, topic, method, super_intelligence)
        self.current_worker.finished.connect(self.on_research_finished)
        self.current_worker.error.connect(self.on_research_error)
        self.current_worker.progress.connect(self.on_research_progress)
        self.current_worker.start()

    def on_research_finished(self, results):
        """Handle research completion."""
        self.set_buttons_enabled(True)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Research completed")

        # Format and display results
        result_text = self.format_results(results)
        self.results_text.setPlainText(result_text)

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

    def format_results(self, results):
        """Format research results for display."""
        lines = []

        lines.append(f"Topic: {results.get('topic', 'Unknown')}")
        lines.append(f"Intelligence Level: {results.get('intelligence_level', 'Unknown')}")
        lines.append(f"Intelligence Score: {results.get('intelligence_score', 0):.1f}/100")
        lines.append(f"Timestamp: {results.get('timestamp', 'Unknown')}")
        lines.append("")

        # Add research phases
        phases = results.get('research_phases', {})
        if phases:
            lines.append("Research Phases:")
            for phase_name, phase_data in phases.items():
                lines.append(f"  {phase_name.replace('_', ' ').title()}:")
                if isinstance(phase_data, dict):
                    for key, value in phase_data.items():
                        if isinstance(value, (list, dict)):
                            lines.append(f"    {key}: {len(value)} items")
                        else:
                            lines.append(f"    {key}: {str(value)[:100]}...")
                else:
                    lines.append(f"    {str(phase_data)[:200]}...")
                lines.append("")

        return "\n".join(lines)

    def set_buttons_enabled(self, enabled):
        """Enable or disable all buttons."""
        self.research_button.setEnabled(enabled)
        self.save_button.setEnabled(enabled)
        self.load_button.setEnabled(enabled)
        self.resume_button.setEnabled(enabled)
        self.image_button.setEnabled(enabled)
        self.scrape_button.setEnabled(enabled)

    def save_results(self):
        """Save research results."""
        QMessageBox.information(self, "Save Results", "Save functionality not yet implemented in GUI.")

    def load_results(self):
        """Load research results."""
        QMessageBox.information(self, "Load Results", "Load functionality not yet implemented in GUI.")

    def resume_research(self):
        """Resume paused research."""
        QMessageBox.information(self, "Resume Research", "Resume functionality not yet implemented in GUI.")

    def analyze_images(self):
        """Analyze uploaded images."""
        QMessageBox.information(self, "Image Analysis", "Image analysis functionality not yet implemented in GUI.")

    def web_scrape(self):
        """Perform web scraping."""
        QMessageBox.information(self, "Web Scraping", "Web scraping functionality not yet implemented in GUI.")

def main():
    """Main application entry point."""
    try:
        app = QApplication(sys.argv)
        app.setStyle('Fusion')  # Use Fusion style for better cross-platform compatibility

        window = ResearchAgentGUI()
        window.show()

        print("Starting Super Enhanced Research Agent Desktop GUI...")
        print("The desktop application will open in a new window")
        print("Close the window to exit the application")

        sys.exit(app.exec())

    except Exception as e:
        print(f"❌ Failed to start desktop GUI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()