#!/usr/bin/env python3
"""
Clean Desktop GUI for ARINN Research Agent

A simplified, stable version of the desktop GUI with timer button functionality.
"""

import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTextEdit, QPushButton, QLabel,
                             QComboBox, QCheckBox, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

try:
    # Try relative imports first (for package execution)
    from .enhanced_agent import EnhancedResearchAgent
    from .super_enhanced_agent import SuperEnhancedResearchAgent
except ImportError:
    # Fallback to absolute imports (for direct execution)
    from enhanced_agent import EnhancedResearchAgent
    from super_enhanced_agent import SuperEnhancedResearchAgent


class ResearchAgentGUI(QMainWindow):
    """Clean desktop GUI for the research agent."""

    def __init__(self):
        super().__init__()
        self.agent = None
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("ARINN - Super Enhanced Research Agent")
        self.setGeometry(100, 100, 900, 700)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Title
        title_label = QLabel("🤖 ARINN - Super Enhanced Research Agent")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Input section
        input_frame = QFrame()
        input_frame.setFrameStyle(QFrame.Shape.Box)
        input_layout = QVBoxLayout(input_frame)

        # Topic input
        topic_layout = QHBoxLayout()
        topic_label = QLabel("Research Topic:")
        self.topic_input = QTextEdit()
        self.topic_input.setMaximumHeight(60)
        self.topic_input.setPlaceholderText("Enter your research topic here...")
        topic_layout.addWidget(topic_label)
        topic_layout.addWidget(self.topic_input)
        input_layout.addLayout(topic_layout)

        # Super intelligence control
        self.super_intelligence_checkbox = QCheckBox("Enable Super Intelligence Features")
        self.super_intelligence_checkbox.setChecked(True)
        self.super_intelligence_checkbox.setToolTip(
            "Enable autonomous goal generation, self-improvement, and advanced AI features.\n"
            "When disabled, ARINN runs in safe research-only mode."
        )
        input_layout.addWidget(self.super_intelligence_checkbox)

        # Timer launch button
        self.timer_button = QPushButton("Launch Goal Timer")
        self.timer_button.setToolTip("Launch a separate window showing the autonomous goal countdown timer")
        self.timer_button.clicked.connect(self._launch_timer_window)
        self.timer_button.setEnabled(True)  # Always enabled for now
        input_layout.addWidget(self.timer_button)

        # Connect checkbox to timer button state
        self.super_intelligence_checkbox.stateChanged.connect(self._update_timer_button_state)
        # Initialize button state
        self._update_timer_button_state()

        main_layout.addWidget(input_frame)

        # Research method selection
        method_layout = QHBoxLayout()
        method_label = QLabel("Research Method:")
        self.method_combo = QComboBox()
        self.method_combo.addItems([
            "Comprehensive Research",
            "Super Intelligent Research",
            "Time-Based Research (1h + 24h)"
        ])
        method_layout.addWidget(method_label)
        method_layout.addWidget(self.method_combo)
        method_layout.addStretch()
        main_layout.addLayout(method_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("🚀 Start Research")
        self.start_button.clicked.connect(self.start_research)
        self.start_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 10px; }")

        self.save_button = QPushButton("💾 Save Results")
        self.save_button.clicked.connect(self.save_results)

        self.load_button = QPushButton("📂 Load Results")
        self.load_button.clicked.connect(self.load_results)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.load_button)
        main_layout.addLayout(button_layout)

        # Results area
        results_label = QLabel("Research Results:")
        main_layout.addWidget(results_label)

        self.results_text = QTextEdit()
        self.results_text.setPlaceholderText("Research results will appear here...")
        main_layout.addWidget(self.results_text)

        # Status bar
        self.statusBar().showMessage("Ready - ARINN Research Agent Loaded")

    def _update_timer_button_state(self):
        """Update timer button enabled state based on super intelligence checkbox."""
        is_enabled = self.super_intelligence_checkbox.isChecked()
        self.timer_button.setEnabled(is_enabled)

        if is_enabled:
            self.timer_button.setText("Launch Goal Timer")
        else:
            self.timer_button.setText("Timer Disabled (Enable Super Intelligence)")

    def _launch_timer_window(self):
        """Launch the autonomous goal timer in a separate CMD window."""
        try:
            import subprocess
            import sys
            import os

            # Path to the timer script
            timer_script = os.path.join(os.path.dirname(__file__), "autonomous_timer.py")

            if not os.path.exists(timer_script):
                QMessageBox.warning(
                    self,
                    "Timer Not Found",
                    f"Timer script not found: {timer_script}"
                )
                return

            # Launch timer in separate CMD window
            subprocess.Popen([
                sys.executable, timer_script
            ], creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)

            QMessageBox.information(
                self,
                "Timer Launched",
                "Autonomous goal timer launched in separate window.\n\n"
                "Close the timer window to stop monitoring."
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Launch Failed",
                f"Failed to launch timer: {str(e)}"
            )

    def start_research(self):
        """Start the research process."""
        topic = self.topic_input.toPlainText().strip()
        if not topic:
            QMessageBox.warning(self, "Input Required", "Please enter a research topic.")
            return

        # Create appropriate agent
        use_super = self.super_intelligence_checkbox.isChecked()
        method = self.method_combo.currentText()

        try:
            if use_super:
                if "Time-Based" in method:
                    self.agent = SuperEnhancedResearchAgent()
                    config = {"ask_definition_first": True, "enable_image_analysis": False}
                    results = self.agent.time_based_research(topic, config)
                else:
                    self.agent = SuperEnhancedResearchAgent()
                    results = self.agent.super_intelligent_research(topic)
            else:
                self.agent = EnhancedResearchAgent()
                results = self.agent.comprehensive_research(topic)

            # Display results
            self.display_results(results)

        except Exception as e:
            QMessageBox.critical(self, "Research Failed", f"Research failed: {str(e)}")

    def display_results(self, results):
        """Display research results in the text area."""
        try:
            if isinstance(results, dict):
                # Format the results nicely
                output = f"Research Topic: {results.get('topic', 'Unknown')}\n"
                output += f"Intelligence Level: {results.get('intelligence_level', 'Standard')}\n"
                output += f"Timestamp: {results.get('timestamp', 'Unknown')}\n\n"

                if "research_phases" in results:
                    phases = results["research_phases"]
                    for phase_name, phase_data in phases.items():
                        output += f"--- {phase_name.replace('_', ' ').title()} ---\n"
                        if isinstance(phase_data, dict):
                            for key, value in phase_data.items():
                                if isinstance(value, list) and len(value) > 5:
                                    output += f"{key}: {len(value)} items\n"
                                else:
                                    output += f"{key}: {str(value)[:200]}...\n"
                        else:
                            output += str(phase_data)[:500] + "\n"
                        output += "\n"

                if "intelligence_score" in results:
                    output += f"Intelligence Score: {results['intelligence_score']:.1f}/100\n"

                self.results_text.setText(output)
            else:
                self.results_text.setText(str(results))

        except Exception as e:
            self.results_text.setText(f"Error displaying results: {str(e)}\n\nRaw results:\n{str(results)}")

    def save_results(self):
        """Save research results to file."""
        if not self.agent or not hasattr(self.agent, 'results'):
            QMessageBox.warning(self, "No Results", "No research results to save.")
            return

        # Implementation for saving results
        QMessageBox.information(self, "Save Results", "Save functionality not yet implemented.")

    def load_results(self):
        """Load research results from file."""
        QMessageBox.information(self, "Load Results", "Load functionality not yet implemented.")


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle("Fusion")

    # Dark theme palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    app.setPalette(palette)

    try:
        window = ResearchAgentGUI()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        error_msg = f"Failed to start desktop GUI: {e}"
        print(f"❌ {error_msg}")
        print("💡 Try running from desktop environment or use web UI:")
        print("   python run_ui.py  # Web-based interface")
        sys.exit(1)


if __name__ == "__main__":
    main()