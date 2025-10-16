"""
Research Agent Desktop GUI

A PyQt6-based desktop application for the Super Enhanced Research Agent.
Provides a native Windows GUI with core research capabilities.
"""

import sys
import os
import time
import threading
import json
import logging
from datetime import datetime, timedelta

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

try:
    from super_enhanced_agent import SuperEnhancedResearchAgent
except ImportError:
    import super_enhanced_agent
    SuperEnhancedResearchAgent = super_enhanced_agent.SuperEnhancedResearchAgent

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QProgressBar,
    QTabWidget, QGroupBox, QCheckBox, QSpinBox, QDoubleSpinBox, QComboBox,
    QSplitter, QMessageBox, QStatusBar, QMenuBar, QMenu,
    QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap, QAction

class ResearchWorker(QThread):
    """Worker thread for running research operations"""
    progress_updated = pyqtSignal(str)
    research_completed = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, topic, config, research_method="super_intelligent"):
        super().__init__()
        self.topic = topic
        self.config = config
        self.research_method = research_method

    def run(self):
        try:
            # Different progress phases based on research method
            if self.research_method == "time_based":
                phases = [
                    "Phase 1/3: Initial learning phase (1 hour) - Understanding the topic",
                    "Phase 1/3: Gathering basic topic information",
                    "Phase 1/3: Generating fundamental questions",
                    "Phase 1/3: Identifying knowledge gaps",
                    "Phase 2/3: Deep research phase (24 hours) - Comprehensive analysis",
                    "Phase 2/3: Generating intelligent questions from initial knowledge",
                    "Phase 2/3: Performing pattern-based research",
                    "Phase 2/3: Executing automated tasks",
                    "Phase 2/3: Generating advanced insights",
                    "Phase 3/3: Creating comprehensive report",
                    "Phase 3/3: Finalizing time-based results"
                ]
            else:
                phases = [
                    "Initializing super intelligence",
                    "Analyzing topic semantics",
                    "Generating intelligent questions",
                    "Performing pattern research",
                    "Executing automated tasks",
                    "Generating advanced insights",
                    "Creating comprehensive report",
                    "Finalizing results"
                ]

            for phase in phases:
                self.progress_updated.emit(phase)
                time.sleep(1)  # Simulate work

            # Initialize agent and run research
            super_intelligence_enabled = self.super_intelligence_checkbox.isChecked()
            agent = SuperEnhancedResearchAgent(
                data_dir="./data",
                use_llm=True,
                max_results=10,
                enable_super_intelligence=super_intelligence_enabled
            )

            # Choose research method
            if self.research_method == "time_based":
                results = agent.time_based_research(self.topic, self.config)
            else:
                results = agent.super_intelligent_research(self.topic, self.config)

            # If site scraping is enabled, run it after main research
            if self.config.get("enable_site_scraping") and self.config.get("site_scraping"):
                scraping_config = self.config["site_scraping"]
                self.progress_updated.emit(f"Starting site scraping for {scraping_config['url']}...")
                try:
                    scraping_results = agent.scrape_specific_site(
                        site_url=scraping_config["url"],
                        max_depth=scraping_config.get("max_depth", 2),
                        delay_between_requests=scraping_config.get("delay_between_requests", 1.0),
                        content_filters=scraping_config.get("content_filters", []),
                        max_pages=scraping_config.get("max_pages", 50)
                    )
                    results["site_scraping"] = scraping_results
                    self.progress_updated.emit("Site scraping completed")
                except Exception as e:
                    self.progress_updated.emit(f"Site scraping failed: {str(e)}")
                    results["site_scraping"] = {"error": str(e)}

            self.research_completed.emit(results)

        except Exception as e:
            self.error_occurred.emit(str(e))

class TimedResearchWorker(QThread):
    """Worker thread for running actual timed research operations"""
    progress_updated = pyqtSignal(str)
    phase_completed = pyqtSignal(str, dict)  # phase_name, partial_results
    research_completed = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    time_remaining_updated = pyqtSignal(str, int)  # phase_name, seconds_remaining

    def __init__(self, topic, config, resume_state=None):
        super().__init__()
        self.topic = topic
        self.config = config
        self.is_paused = False
        self.is_stopped = False
        self.pause_event = threading.Event()
        self.pause_event.set()  # Start unpaused

        # Resume state if provided
        self.resume_state = resume_state
        self.current_phase = resume_state.get('current_phase', 'initial_learning') if resume_state else 'initial_learning'
        self.phase_start_time = resume_state.get('phase_start_time') if resume_state else None
        self.time_remaining_at_pause = resume_state.get('time_remaining_at_pause', 0) if resume_state else 0
        self.partial_results = resume_state.get('partial_results', {}) if resume_state else {}
        self.config = resume_state.get('config', config) if resume_state else config

    def pause(self):
        """Pause the research"""
        self.is_paused = True
        self.pause_event.clear()

        # Save current state for persistence
        self._save_research_state(self.current_phase, self.partial_results)

    def resume(self):
        """Resume the research"""
        self.is_paused = False
        self.pause_event.set()

    def stop(self):
        """Stop the research"""
        self.is_stopped = True
        self.pause_event.set()  # Allow thread to exit

    def run(self):
        try:
            # Handle resume state
            if self.resume_state:
                self.progress_updated.emit(f"Resuming {self.current_phase.replace('_', ' ').title()}")
                # Continue from where we left off
                if self.current_phase == 'waiting_phase_1':
                    self._resume_waiting_phase_1()
                elif self.current_phase == 'waiting_phase_2':
                    self._resume_waiting_phase_2()
                elif self.current_phase == 'deep_research':
                    self._complete_research()
                elif self.current_phase == 'initial_learning':
                    # Research was paused after initial learning but before waiting
                    # Continue with Phase 1 waiting
                    self._resume_waiting_phase_1()
                else:
                    # Unknown phase, start fresh
                    self.progress_updated.emit("Unknown resume state, starting fresh research")
                    self.resume_state = None
                return

            # Fresh start - Phase 1: Initial Learning
            self.progress_updated.emit("Phase 1/3: Initial learning phase - Understanding the topic")
            phase_1_results = self._perform_initial_learning()
            self.phase_completed.emit("initial_learning", phase_1_results)
            self.partial_results['initial_learning'] = phase_1_results

            # Save state before waiting
            self._save_research_state('waiting_phase_1', phase_1_results)

            # Wait for 1 hour (3600 seconds) with pause/resume support
            self._wait_with_pause(3600, "Phase 1: Initial Learning")

            if self.is_stopped:
                return

            # Phase 2: Deep Research
            self.progress_updated.emit("Phase 2/3: Deep research phase - Comprehensive analysis")
            phase_2_results = self._perform_deep_research(phase_1_results)
            self.phase_completed.emit("deep_research", phase_2_results)
            self.partial_results['deep_research'] = phase_2_results

            # Save state before waiting
            self._save_research_state('waiting_phase_2', {**self.partial_results, 'deep_research': phase_2_results})

            # Wait for 24 hours (86400 seconds) with pause/resume support
            self._wait_with_pause(86400, "Phase 2: Deep Research")

            if self.is_stopped:
                return

            # Phase 3: Report Generation
            self.progress_updated.emit("Phase 3/3: Generating comprehensive report")
            final_results = self._generate_final_report(phase_1_results, phase_2_results)
            self.research_completed.emit(final_results)

            # Clean up saved state on completion
            self._clear_research_state()

        except Exception as e:
            self.error_occurred.emit(str(e))

    def _wait_with_pause(self, total_seconds, phase_name):
        """Wait for the specified time with pause/resume support"""
        if self.resume_state and self.time_remaining_at_pause > 0:
            # Resuming from pause - use remaining time
            end_time = time.time() + self.time_remaining_at_pause
            # Don't reset time_remaining_at_pause here - keep it for multiple pauses
        else:
            # Fresh start
            end_time = time.time() + total_seconds

        while time.time() < end_time and not self.is_stopped:
            self.pause_event.wait()  # Wait if paused

            if self.is_stopped:
                break

            current_time = time.time()
            remaining = max(0, int(end_time - current_time))

            # Update remaining time for pause/resume (always keep current remaining time)
            self.time_remaining_at_pause = remaining

            # Emit time remaining every second
            self.time_remaining_updated.emit(phase_name, remaining)

            time.sleep(1)

    def _perform_initial_learning(self):
        """Perform actual initial learning phase"""
        try:
            # Initialize agent
            agent = SuperEnhancedResearchAgent(
                data_dir="./data",
                use_llm=True,
                max_results=10,
                enable_super_intelligence=True
            )

            # Perform initial learning
            initial_knowledge = agent._perform_initial_learning(self.topic, self.config)

            # Save partial results
            self._save_partial_results("initial_learning", initial_knowledge)

            return initial_knowledge

        except Exception as e:
            logging.error(f"Initial learning failed: {e}")
            return {"error": str(e)}

    def _perform_deep_research(self, initial_knowledge):
        """Perform actual deep research phase"""
        try:
            # Initialize agent
            super_intelligence_enabled = self.super_intelligence_checkbox.isChecked()
            agent = SuperEnhancedResearchAgent(
                data_dir="./data",
                use_llm=True,
                max_results=10,
                enable_super_intelligence=super_intelligence_enabled
            )

            # Perform deep research
            deep_results = agent._perform_deep_research(self.topic, initial_knowledge)

            # Save partial results
            self._save_partial_results("deep_research", deep_results)

            return deep_results

        except Exception as e:
            logging.error(f"Deep research failed: {e}")
            return {"error": str(e)}

    def _generate_final_report(self, phase_1_results, phase_2_results):
        """Generate final comprehensive report"""
        try:
            # Initialize agent
            super_intelligence_enabled = self.super_intelligence_checkbox.isChecked()
            agent = SuperEnhancedResearchAgent(
                data_dir="./data",
                use_llm=True,
                max_results=10,
                enable_super_intelligence=super_intelligence_enabled
            )

            # Combine results
            research_results = {
                "topic": self.topic,
                "timestamp": datetime.now().isoformat(),
                "intelligence_level": "time_based_super_enhanced",
                "research_phases": {
                    "initial_learning": phase_1_results,
                    "deep_research": phase_2_results
                },
                "timing": {
                    "phase_1_duration_hours": 1,
                    "phase_2_duration_hours": 24,
                    "total_duration_hours": 25
                }
            }

            # Generate report
            report = agent._generate_time_based_report(self.topic, research_results)
            research_results["research_phases"]["comprehensive_report"] = report

            # Calculate final score
            research_results["success"] = True
            research_results["intelligence_score"] = agent._calculate_time_based_intelligence_score(research_results)

            # Save final results
            self._save_partial_results("final_results", research_results)

            return research_results

        except Exception as e:
            logging.error(f"Final report generation failed: {e}")
            return {"error": str(e)}

    def _save_partial_results(self, phase_name, results):
        """Save partial results to disk for recovery"""
        try:
            research_dir = os.path.join("./data", "timed_research")
            os.makedirs(research_dir, exist_ok=True)

            filename = f"{self.topic}_{phase_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(research_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logging.warning(f"Failed to save partial results for {phase_name}: {e}")

    def _save_research_state(self, current_phase, partial_results):
        """Save the current research state for persistence across restarts"""
        try:
            state_dir = os.path.join("./data", "research_state")
            os.makedirs(state_dir, exist_ok=True)

            state = {
                'topic': self.topic,
                'config': self.config,
                'current_phase': current_phase,
                'phase_start_time': self.phase_start_time,
                'time_remaining_at_pause': self.time_remaining_at_pause,
                'partial_results': partial_results,
                'saved_at': datetime.now().isoformat()
            }

            filepath = os.path.join(state_dir, f"{self.topic}_research_state.json")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logging.warning(f"Failed to save research state: {e}")

    def _clear_research_state(self):
        """Clear saved research state after completion"""
        try:
            state_dir = os.path.join("./data", "research_state")
            filepath = os.path.join(state_dir, f"{self.topic}_research_state.json")
            if os.path.exists(filepath):
                os.remove(filepath)
        except OSError as e:
            logging.warning(f"Failed to clear research state: {e}")

    def _resume_waiting_phase_1(self):
        """Resume waiting for Phase 1 completion"""
        try:
            # Calculate remaining time from when we paused
            if self.time_remaining_at_pause > 0:
                self._wait_with_pause(self.time_remaining_at_pause, "Phase 1: Initial Learning")

            if not self.is_stopped:
                # Continue with Phase 2
                phase_1_results = self.partial_results.get('initial_learning', {})
                self.progress_updated.emit("Phase 2/3: Deep research phase - Comprehensive analysis")
                phase_2_results = self._perform_deep_research(phase_1_results)
                self.phase_completed.emit("deep_research", phase_2_results)
                self.partial_results['deep_research'] = phase_2_results

                # Save state before Phase 2 waiting
                self._save_research_state('waiting_phase_2', {**self.partial_results, 'deep_research': phase_2_results})

                # Wait for Phase 2
                self._wait_with_pause(86400, "Phase 2: Deep Research")

                if not self.is_stopped:
                    # Generate final report
                    self.progress_updated.emit("Phase 3/3: Generating comprehensive report")
                    final_results = self._generate_final_report(phase_1_results, phase_2_results)
                    self.research_completed.emit(final_results)
                    self._clear_research_state()

        except Exception as e:
            self.error_occurred.emit(f"Resume error: {str(e)}")

    def _resume_waiting_phase_2(self):
        """Resume waiting for Phase 2 completion"""
        try:
            # Calculate remaining time from when we paused
            if self.time_remaining_at_pause > 0:
                self._wait_with_pause(self.time_remaining_at_pause, "Phase 2: Deep Research")

            if not self.is_stopped:
                # Generate final report
                phase_1_results = self.partial_results.get('initial_learning', {})
                phase_2_results = self.partial_results.get('deep_research', {})

                self.progress_updated.emit("Phase 3/3: Generating comprehensive report")
                final_results = self._generate_final_report(phase_1_results, phase_2_results)
                self.research_completed.emit(final_results)
                self._clear_research_state()

        except Exception as e:
            self.error_occurred.emit(f"Resume error: {str(e)}")

    def _complete_research(self):
        """Complete research from deep research phase"""
        try:
            phase_1_results = self.partial_results.get('initial_learning', {})
            phase_2_results = self.partial_results.get('deep_research', {})

            # Wait for Phase 2 if needed
            self._wait_with_pause(86400, "Phase 2: Deep Research")

            if not self.is_stopped:
                # Generate final report
                self.progress_updated.emit("Phase 3/3: Generating comprehensive report")
                final_results = self._generate_final_report(phase_1_results, phase_2_results)
                self.research_completed.emit(final_results)
                self._clear_research_state()

        except Exception as e:
            self.error_occurred.emit(f"Resume error: {str(e)}")

class SiteScrapingWorker(QThread):
    """Worker thread for independent site scraping operations"""
    progress_updated = pyqtSignal(str)
    scraping_completed = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, scraping_config):
        super().__init__()
        self.scraping_config = scraping_config

    def run(self):
        try:
            self.progress_updated.emit("Initializing site scraping...")

            # Initialize agent
            super_intelligence_enabled = self.super_intelligence_checkbox.isChecked()
            agent = SuperEnhancedResearchAgent(
                data_dir="./data",
                use_llm=True,
                max_results=10,
                enable_super_intelligence=super_intelligence_enabled
            )

            self.progress_updated.emit("Starting site scraping...")

            # Perform site scraping
            scraping_results = agent.scrape_specific_site(
                site_url=self.scraping_config["url"],
                max_depth=self.scraping_config["max_depth"],
                delay_between_requests=self.scraping_config["delay_between_requests"],
                content_filters=self.scraping_config["content_filters"],
                max_pages=self.scraping_config["max_pages"]
            )

            self.progress_updated.emit("Site scraping completed")
            self.scraping_completed.emit(scraping_results)

        except Exception as e:
            self.error_occurred.emit(str(e))

class ResearchAgentGUI(QMainWindow):
    """Main GUI window for the Research Agent"""

    def __init__(self):
        super().__init__()
        self.agent = None
        self.current_results = None
        self.worker = None
        self.current_topic = ""
        self.paused_research_state = None

        self.init_ui()
        self.setup_menu()
        self.load_logo()
        self.check_for_paused_research()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Super Enhanced Research Agent")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Header with logo
        header_layout = QHBoxLayout()
        self.logo_label = QLabel()
        # Logo size will be set in load_logo()
        header_layout.addWidget(self.logo_label)

        title_label = QLabel("Super Enhanced Research Agent")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        subtitle_label = QLabel("*Maximum Intelligence Without API Keys*")
        subtitle_font = QFont()
        subtitle_font.setItalic(True)
        subtitle_label.setFont(subtitle_font)
        header_layout.addWidget(subtitle_label)

        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Create splitter for main content
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Top section - Research input and controls
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)

        # Research input group
        input_group = QGroupBox("Research Configuration")
        input_layout = QVBoxLayout(input_group)

        # Topic input
        topic_layout = QHBoxLayout()
        topic_layout.addWidget(QLabel("Research Topic:"))
        self.topic_input = QLineEdit()
        # Super intelligence control checkbox
        self.super_intelligence_checkbox = QCheckBox("Enable Super Intelligence Features")
        self.super_intelligence_checkbox.setChecked(True)  # Default to enabled
        self.super_intelligence_checkbox.setToolTip(
            "Enable autonomous goal generation, self-improvement, and advanced AI features.\n"
            "When disabled, ARINN runs in safe research-only mode."
        )

        # Autonomous goal timer display
        self.goal_timer_label = QLabel("Next autonomous goal: --:--")
        self.goal_timer_label.setStyleSheet("color: #666; font-size: 10px;")
        self.goal_timer_label.setVisible(True)  # Show when super intelligence enabled

        # Connect checkbox to timer visibility
        self.super_intelligence_checkbox.stateChanged.connect(self._update_goal_timer_visibility)
        self.topic_input.setPlaceholderText("Enter your research topic (e.g., artificial intelligence, machine learning)")
        topic_layout.addWidget(self.topic_input)
        topic_layout.addWidget(self.super_intelligence_checkbox)
        topic_layout.addWidget(self.goal_timer_label)
        input_layout.addLayout(topic_layout)

        # Research method selection
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Research Method:"))
        self.method_combo = QComboBox()
        self.method_combo.addItems([
            "Super Intelligent Research (Fast)",
            "Time-Based Research (25 Hours)"
        ])
        self.method_combo.setCurrentText("Super Intelligent Research (Fast)")
        self.method_combo.currentTextChanged.connect(self.on_method_changed)
        method_layout.addWidget(self.method_combo)
        method_layout.addStretch()
        input_layout.addLayout(method_layout)

        # Configuration options
        config_layout = QHBoxLayout()

        # Left column
        left_config = QVBoxLayout()
        self.web_checkbox = QCheckBox("Enable Web Research")
        self.web_checkbox.setChecked(True)
        left_config.addWidget(self.web_checkbox)

        self.github_checkbox = QCheckBox("Enable GitHub Research")
        left_config.addWidget(self.github_checkbox)

        self.files_checkbox = QCheckBox("Enable File Analysis")
        left_config.addWidget(self.files_checkbox)

        # Right column
        right_config = QVBoxLayout()
        self.automation_checkbox = QCheckBox("Enable Automation")
        self.automation_checkbox.setChecked(True)
        right_config.addWidget(self.automation_checkbox)

        self.site_scraping_checkbox = QCheckBox("Enable Site Scraping")
        right_config.addWidget(self.site_scraping_checkbox)

        # Site scraping configuration (shown when checkbox is enabled)
        self.site_scraping_group = QGroupBox("Site Scraping Settings")
        self.site_scraping_group.setVisible(False)  # Hidden by default
        scraping_layout = QVBoxLayout(self.site_scraping_group)

        # URL input
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("Site URL:"))
        self.scrape_url_input = QLineEdit()
        self.scrape_url_input.setPlaceholderText("https://docs.python.org/3")
        url_layout.addWidget(self.scrape_url_input)
        scraping_layout.addLayout(url_layout)

        # Parameters
        params_layout = QHBoxLayout()

        # Max depth
        depth_layout = QVBoxLayout()
        depth_layout.addWidget(QLabel("Max Depth:"))
        self.scrape_depth_spin = QSpinBox()
        self.scrape_depth_spin.setRange(1, 5)
        self.scrape_depth_spin.setValue(2)
        depth_layout.addWidget(self.scrape_depth_spin)
        params_layout.addLayout(depth_layout)

        # Delay
        delay_layout = QVBoxLayout()
        delay_layout.addWidget(QLabel("Request Delay:"))
        self.scrape_delay_spin = QDoubleSpinBox()
        self.scrape_delay_spin.setRange(0.5, 5.0)
        self.scrape_delay_spin.setValue(1.0)
        self.scrape_delay_spin.setSingleStep(0.5)
        delay_layout.addWidget(self.scrape_delay_spin)
        params_layout.addLayout(delay_layout)

        # Max pages
        pages_layout = QVBoxLayout()
        pages_layout.addWidget(QLabel("Max Pages:"))
        self.scrape_pages_spin = QSpinBox()
        self.scrape_pages_spin.setRange(10, 100)
        self.scrape_pages_spin.setValue(50)
        pages_layout.addWidget(self.scrape_pages_spin)
        params_layout.addLayout(pages_layout)

        scraping_layout.addLayout(params_layout)

        # Content filters with help
        filters_layout = QHBoxLayout()
        filters_label = QLabel("Content Filters:")
        filters_label.setToolTip("Comma-separated keywords to focus scraping on.\n"
                                "Example: tutorial,function,class,api\n"
                                "Only pages containing these words will be prioritized.\n"
                                "Leave empty to scrape all content.")
        filters_layout.addWidget(filters_label)
        self.scrape_filters_input = QLineEdit()
        self.scrape_filters_input.setPlaceholderText("tutorial,function,class,api")
        self.scrape_filters_input.setToolTip("Keywords like: tutorial, api, function, class, guide, reference")
        filters_layout.addWidget(self.scrape_filters_input)
        scraping_layout.addLayout(filters_layout)

        right_config.addWidget(self.site_scraping_group)

        # Connect checkbox to show/hide settings
        self.site_scraping_checkbox.stateChanged.connect(self.on_site_scraping_checkbox_changed)
        # Connect URL input to enable/disable scrape button
        self.scrape_url_input.textChanged.connect(self.on_scrape_url_changed)

        # Time-based research options (only shown when time-based is selected)
        definition_group = QGroupBox("Definition Question Format")
        definition_group.setVisible(False)  # Hidden by default
        definition_layout = QVBoxLayout(definition_group)

        self.question_a_checkbox = QCheckBox("Start question with 'What is a [topic]?'")
        self.question_a_checkbox.setChecked(True)  # Default selection
        definition_layout.addWidget(self.question_a_checkbox)

        self.question_the_checkbox = QCheckBox("Start question with 'What is the [topic]?'")
        definition_layout.addWidget(self.question_the_checkbox)

        # Ensure only one can be checked at a time
        self.question_a_checkbox.stateChanged.connect(lambda: self.on_question_checkbox_changed('a'))
        self.question_the_checkbox.stateChanged.connect(lambda: self.on_question_checkbox_changed('the'))

        right_config.addWidget(definition_group)
        self.definition_group = definition_group  # Store reference

        max_results_layout = QHBoxLayout()
        max_results_layout.addWidget(QLabel("Max Results:"))
        self.max_results_spin = QSpinBox()
        self.max_results_spin.setRange(5, 20)
        self.max_results_spin.setValue(10)
        max_results_layout.addWidget(self.max_results_spin)
        right_config.addLayout(max_results_layout)

        depth_layout = QHBoxLayout()
        depth_layout.addWidget(QLabel("Research Depth:"))
        self.depth_combo = QComboBox()
        self.depth_combo.addItems(["standard", "deep", "comprehensive"])
        self.depth_combo.setCurrentText("deep")
        depth_layout.addWidget(self.depth_combo)
        right_config.addLayout(depth_layout)

        config_layout.addLayout(left_config)
        config_layout.addLayout(right_config)
        input_layout.addLayout(config_layout)

        top_layout.addWidget(input_group)

        # Control buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("🚀 Start Super Intelligent Research")
        self.start_button.clicked.connect(self.start_research)
        self.start_button.setStyleSheet("QPushButton { font-weight: bold; padding: 10px; }")
        button_layout.addWidget(self.start_button)

        # Site scraping button (independent of research)
        self.scrape_button = QPushButton("🕷️ Scrape Site Only")
        self.scrape_button.clicked.connect(self.scrape_site_only)
        self.scrape_button.setEnabled(False)  # Disabled until site scraping is configured
        self.scrape_button.setStyleSheet("QPushButton { font-weight: bold; padding: 10px; }")
        button_layout.addWidget(self.scrape_button)

        self.pause_button = QPushButton("⏸️ Pause Research")
        self.pause_button.clicked.connect(self.pause_research)
        self.pause_button.setEnabled(False)
        button_layout.addWidget(self.pause_button)

        self.resume_button = QPushButton("▶️ Resume Research")
        self.resume_button.clicked.connect(self.resume_research)
        self.resume_button.setEnabled(False)
        self.resume_button.setVisible(False)
        button_layout.addWidget(self.resume_button)

        self.stop_button = QPushButton("⏹️ Stop Research")
        self.stop_button.clicked.connect(self.stop_research)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        button_layout.addStretch()
        top_layout.addLayout(button_layout)

        # Progress section
        progress_group = QGroupBox("Research Progress")
        progress_layout = QVBoxLayout(progress_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        progress_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready to start research...")
        progress_layout.addWidget(self.status_label)

        self.timer_label = QLabel("")
        self.timer_label.setVisible(False)
        progress_layout.addWidget(self.timer_label)

        top_layout.addWidget(progress_group)

        splitter.addWidget(top_widget)

        # Bottom section - Results tabs
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)

        self.results_tabs = QTabWidget()

        # Overview tab
        overview_tab = QWidget()
        overview_layout = QVBoxLayout(overview_tab)

        self.overview_text = QTextEdit()
        self.overview_text.setReadOnly(True)
        overview_layout.addWidget(self.overview_text)

        self.results_tabs.addTab(overview_tab, "📊 Overview")

        # Questions tab
        questions_tab = QWidget()
        questions_layout = QVBoxLayout(questions_tab)

        self.questions_text = QTextEdit()
        self.questions_text.setReadOnly(True)
        questions_layout.addWidget(self.questions_text)

        self.results_tabs.addTab(questions_tab, "❓ Questions")

        # Patterns tab
        patterns_tab = QWidget()
        patterns_layout = QVBoxLayout(patterns_tab)

        self.patterns_text = QTextEdit()
        self.patterns_text.setReadOnly(True)
        patterns_layout.addWidget(self.patterns_text)

        self.results_tabs.addTab(patterns_tab, "🔍 Patterns")

        # Automation tab
        automation_tab = QWidget()
        automation_layout = QVBoxLayout(automation_tab)

        self.automation_text = QTextEdit()
        self.automation_text.setReadOnly(True)
        automation_layout.addWidget(self.automation_text)

        self.results_tabs.addTab(automation_tab, "⚙️ Automation")

        # Insights tab
        insights_tab = QWidget()
        insights_layout = QVBoxLayout(insights_tab)

        self.insights_text = QTextEdit()
        self.insights_text.setReadOnly(True)
        insights_layout.addWidget(self.insights_text)

        self.results_tabs.addTab(insights_tab, "💡 Insights")

        # Report tab
        report_tab = QWidget()
        report_layout = QVBoxLayout(report_tab)

        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        report_layout.addWidget(self.report_text)

        self.results_tabs.addTab(report_tab, "📄 Report")

        bottom_layout.addWidget(self.results_tabs)

        splitter.addWidget(bottom_widget)
        splitter.setSizes([400, 400])

        main_layout.addWidget(splitter)

        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")

    def setup_menu(self):
        """Setup the menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')

        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menubar.addMenu('Help')

        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def on_method_changed(self):
        """Handle research method selection change"""
        method = self.method_combo.currentText()
        if "Time-Based" in method:
            self.start_button.setText("⏰ Start Time-Based Research (25 Hours)")
            self.status_label.setText("Time-based research: 1 hour initial learning + 24 hours deep research")
            self.definition_group.setVisible(True)
        else:
            self.start_button.setText("🚀 Start Super Intelligent Research")
            self.status_label.setText("Ready to start research...")
            self.definition_group.setVisible(False)

    def on_question_checkbox_changed(self, checkbox_type):
        """Handle question checkbox changes to ensure only one is selected"""
        if checkbox_type == 'a' and self.question_a_checkbox.isChecked():
            self.question_the_checkbox.setChecked(False)
        elif checkbox_type == 'the' and self.question_the_checkbox.isChecked():
            self.question_a_checkbox.setChecked(False)
        # If both are unchecked, default to 'a'
        elif not self.question_a_checkbox.isChecked() and not self.question_the_checkbox.isChecked():
            self.question_a_checkbox.setChecked(True)

    def on_site_scraping_checkbox_changed(self):
        """Handle site scraping checkbox changes to show/hide settings"""
        is_enabled = self.site_scraping_checkbox.isChecked()
        self.site_scraping_group.setVisible(is_enabled)
        self.update_scrape_button_state()

    def on_scrape_url_changed(self):
        """Handle URL input changes to enable/disable scrape button"""
        self.update_scrape_button_state()

    def update_scrape_button_state(self):
        """Update the enabled state of the scrape button"""
        has_url = bool(self.scrape_url_input.text().strip())
        is_enabled = self.site_scraping_checkbox.isChecked() and has_url
        self.scrape_button.setEnabled(is_enabled)

    def check_for_paused_research(self):
        """Check if there's paused research to resume"""
        try:
            state_dir = os.path.join("./data", "research_state")
            if not os.path.exists(state_dir):
                return

            # Look for any saved research state files
            for filename in os.listdir(state_dir):
                if filename.endswith("_research_state.json"):
                    filepath = os.path.join(state_dir, filename)

                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            state = json.load(f)
                    except (json.JSONDecodeError, IOError) as e:
                        logging.warning(f"Failed to load research state from {filepath}: {e}")
                        continue

                    self.paused_research_state = state

                    # Ask user if they want to resume
                    topic = state.get('topic', 'Unknown')
                    current_phase = state.get('current_phase', 'unknown')
                    saved_at = state.get('saved_at', 'Unknown time')

                    reply = QMessageBox.question(
                        self,
                        "Resume Paused Research",
                        f"Found paused research for topic '{topic}'\n\n"
                        f"Current phase: {current_phase.replace('_', ' ').title()}\n"
                        f"Saved at: {saved_at}\n\n"
                        "Do you want to resume this research?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.Yes
                    )

                    if reply == QMessageBox.StandardButton.Yes:
                        self.resume_paused_research(state)
                    else:
                        # Clear the paused state
                        try:
                            os.remove(filepath)
                        except OSError as e:
                            logging.warning(f"Failed to remove paused research state file {filepath}: {e}")
                        self.paused_research_state = None

                    break  # Only handle one paused research at a time

        except Exception as e:
            logging.warning(f"Error checking for paused research: {e}")

    def resume_paused_research(self, state):
        """Resume paused research from saved state"""
        try:
            topic = state['topic']
            config = state['config']

            # Update UI to match the paused research configuration
            self.topic_input.setText(topic)

            # Set research method based on config
            if config.get('ask_definition_first'):
                self.method_combo.setCurrentText("Time-Based Research (25 Hours)")
                # Set definition checkboxes based on config
                question_format = config.get('question_format', 'a')
                if question_format == 'a':
                    self.question_a_checkbox.setChecked(True)
                    self.question_the_checkbox.setChecked(False)
                else:
                    self.question_a_checkbox.setChecked(False)
                    self.question_the_checkbox.setChecked(True)
            else:
                self.method_combo.setCurrentText("Super Intelligent Research (Fast)")

            # Update UI to show we're resuming
            self.status_label.setText(f"Resuming research for '{topic}'...")
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.pause_button.setEnabled(True)
            self.timer_label.setVisible(True)

            # Start the timed research worker with resume state
            self.worker = TimedResearchWorker(topic, config, state)
            self.worker.progress_updated.connect(self.update_progress)
            self.worker.phase_completed.connect(self.phase_completed)
            self.worker.time_remaining_updated.connect(self.update_time_remaining)
            self.worker.research_completed.connect(self.research_finished)
            self.worker.error_occurred.connect(self.research_error)
            self.worker.start()

        except Exception as e:
            QMessageBox.critical(self, "Resume Error", f"Failed to resume research: {str(e)}")

    def load_logo(self):
        """Load and display the logo"""
        logo_path = "Icon.jpg"
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # Scale to 120x120 for better quality, using smooth transformation
            scaled_pixmap = pixmap.scaled(
                120, 120,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.logo_label.setPixmap(scaled_pixmap)
            # Update label size to match
            self.logo_label.setFixedSize(120, 120)
        else:
            self.logo_label.setText("🔬")
            self.logo_label.setFixedSize(80, 80)

    def start_research(self):
        """Start the research process"""
        topic = self.topic_input.text().strip()
        if not topic:
            QMessageBox.warning(self, "Input Required", "Please enter a research topic.")
            return

        # Check if there's paused research for a different topic
        if self.paused_research_state:
            paused_topic = self.paused_research_state.get('topic')
            if paused_topic and paused_topic != topic:
                reply = QMessageBox.question(
                    self,
                    "Paused Research Exists",
                    f"There's paused research for topic '{paused_topic}'.\n\n"
                    "Do you want to resume that research instead of starting new research on '{topic}'?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.resume_paused_research(self.paused_research_state)
                    return

        # Store current topic for image rating context
        self.current_topic = topic

        # Determine research method
        method_text = self.method_combo.currentText()
        if "Time-Based" in method_text:
            research_method = "time_based"
            method_description = "Time-Based Research (25 hours)"
        else:
            research_method = "super_intelligent"
            method_description = "Super Intelligent Research"

        # Confirm time-based research
        if research_method == "time_based":
            reply = QMessageBox.question(
                self,
                "Time-Based Research",
                "Time-based research takes 25 hours total:\n"
                "• Phase 1: 1 hour initial learning\n"
                "• Phase 2: 24 hours deep research\n\n"
                "This is a simulation - actual research would take the full time.\n\n"
                "Do you want to proceed?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        # Prepare configuration
        config = {
            "enable_web_research": self.web_checkbox.isChecked(),
            "enable_github_research": self.github_checkbox.isChecked(),
            "enable_file_analysis": self.files_checkbox.isChecked(),
            "enable_workflow_execution": self.automation_checkbox.isChecked(),
            "enable_site_scraping": self.site_scraping_checkbox.isChecked(),
            "max_results": self.max_results_spin.value(),
            "research_depth": self.depth_combo.currentText()
        }

        # Add site scraping configuration if enabled
        if self.site_scraping_checkbox.isChecked():
            scrape_url = self.scrape_url_input.text().strip()
            if not scrape_url:
                QMessageBox.warning(self, "Configuration Required", "Please enter a site URL to scrape.")
                return

            if not scrape_url.startswith(('http://', 'https://')):
                QMessageBox.warning(self, "Invalid URL", "Site URL must start with http:// or https://")
                return

            config["site_scraping"] = {
                "url": scrape_url,
                "max_depth": self.scrape_depth_spin.value(),
                "delay_between_requests": self.scrape_delay_spin.value(),
                "max_pages": self.scrape_pages_spin.value(),
                "content_filters": [f.strip() for f in self.scrape_filters_input.text().split(',') if f.strip()]
            }

        # Add time-based specific config
        if research_method == "time_based":
            question_format = "a" if self.question_a_checkbox.isChecked() else "the"
            config["ask_definition_first"] = True
            config["question_format"] = question_format

        # Update UI
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText(f"Starting {method_description}...")
        self.status_bar.showMessage(f"{method_description} in progress...")

        # Clear previous results
        self.overview_text.clear()
        self.questions_text.clear()
        self.patterns_text.clear()
        self.automation_text.clear()
        self.insights_text.clear()
        self.report_text.clear()

        # Start appropriate research worker
        if research_method == "time_based":
            self.worker = TimedResearchWorker(topic, config)
            self.worker.progress_updated.connect(self.update_progress)
            self.worker.phase_completed.connect(self.phase_completed)
            self.worker.time_remaining_updated.connect(self.update_time_remaining)
            self.worker.research_completed.connect(self.research_finished)
            self.worker.error_occurred.connect(self.research_error)

            # Enable pause/resume buttons for timed research
            self.pause_button.setEnabled(True)
            self.resume_button.setEnabled(False)
            self.resume_button.setVisible(False)
            self.timer_label.setVisible(True)
        else:
            self.worker = ResearchWorker(topic, config, research_method)
            self.worker.progress_updated.connect(self.update_progress)
            self.worker.research_completed.connect(self.research_finished)
            self.worker.error_occurred.connect(self.research_error)

        self.worker.start()

    def pause_research(self):
        """Pause the research process"""
        if hasattr(self.worker, 'pause'):
            self.worker.pause()
            self.pause_button.setEnabled(False)
            self.resume_button.setEnabled(True)
            self.resume_button.setVisible(True)
            self.status_label.setText("Research paused")
            self.status_bar.showMessage("Research paused")

    def resume_research(self):
        """Resume the research process"""
        if hasattr(self.worker, 'resume'):
            self.worker.resume()
            self.pause_button.setEnabled(True)
            self.resume_button.setEnabled(False)
            self.resume_button.setVisible(False)
            self.status_label.setText("Research resumed")
            self.status_bar.showMessage("Research resumed")

    def stop_research(self):
        """Stop the research process"""
        if self.worker and self.worker.isRunning():
            if hasattr(self.worker, 'stop'):
                self.worker.stop()
            else:
                self.worker.terminate()
            self.worker.wait()

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.pause_button.setEnabled(False)
        self.resume_button.setEnabled(False)
        self.resume_button.setVisible(False)
        self.progress_bar.setValue(0)
        self.timer_label.setVisible(False)
        self.status_label.setText("Research stopped")
        self.status_bar.showMessage("Research stopped by user")

    def scrape_site_only(self):
        """Scrape a site independently of research topics"""
        # Validate inputs
        url = self.scrape_url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "URL Required", "Please enter a site URL to scrape.")
            return

        if not url.startswith(('http://', 'https://')):
            QMessageBox.warning(self, "Invalid URL", "Site URL must start with http:// or https://")
            return

        # Prepare scraping configuration
        scraping_config = {
            "url": url,
            "max_depth": self.scrape_depth_spin.value(),
            "delay_between_requests": self.scrape_delay_spin.value(),
            "max_pages": self.scrape_pages_spin.value(),
            "content_filters": [f.strip() for f in self.scrape_filters_input.text().split(',') if f.strip()]
        }

        # Update UI
        self.scrape_button.setEnabled(False)
        self.start_button.setEnabled(False)  # Disable research while scraping
        self.progress_bar.setValue(0)
        self.status_label.setText(f"Starting site scraping for {url}...")
        self.status_bar.showMessage("Site scraping in progress...")

        # Clear previous results
        self.overview_text.clear()
        self.questions_text.clear()
        self.patterns_text.clear()
        self.automation_text.clear()
        self.insights_text.clear()
        self.report_text.clear()

        # Start scraping worker
        self.worker = SiteScrapingWorker(scraping_config)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.scraping_completed.connect(self.site_scraping_finished)
        self.worker.error_occurred.connect(self.site_scraping_error)
        self.worker.start()

    def phase_completed(self, phase_name, partial_results):
        """Handle phase completion"""
        if phase_name == "initial_learning":
            self.status_label.setText("✅ Phase 1 completed: Initial learning finished")
            self.progress_bar.setValue(33)
        elif phase_name == "deep_research":
            self.status_label.setText("✅ Phase 2 completed: Deep research finished")
            self.progress_bar.setValue(66)

    def update_time_remaining(self, phase_name, seconds_remaining):
        """Update the time remaining display"""
        hours = seconds_remaining // 3600
        minutes = (seconds_remaining % 3600) // 60
        seconds = seconds_remaining % 60

        time_str = f"{phase_name}: {hours:02d}:{minutes:02d}:{seconds:02d} remaining"
        self.timer_label.setText(time_str)

    def update_progress(self, phase):
        """Update progress display"""
        self.status_label.setText(f"🔄 {phase}...")
        # Simulate progress increase
        current_value = self.progress_bar.value()
        self.progress_bar.setValue(min(current_value + 12, 90))

    def research_finished(self, results):
        """Handle research completion"""
        self.current_results = results
        self.progress_bar.setValue(100)
        self.timer_label.setVisible(False)
        self.status_label.setText("✅ Research completed successfully!")
        self.status_bar.showMessage("Research completed")

        # Clear any paused research state since it's now complete
        self.paused_research_state = None

        # Update UI
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.pause_button.setEnabled(False)
        self.resume_button.setEnabled(False)
        self.resume_button.setVisible(False)

        # Display results
        self.display_results(results)

    def research_error(self, error_msg):
        """Handle research error"""
        self.progress_bar.setValue(0)
        self.status_label.setText("❌ Research failed")
        self.status_bar.showMessage("Research failed")

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        QMessageBox.critical(self, "Research Error", f"An error occurred during research:\n\n{error_msg}")

    def site_scraping_finished(self, results):
        """Handle site scraping completion"""
        self.progress_bar.setValue(100)
        self.status_label.setText("✅ Site scraping completed successfully!")
        self.status_bar.showMessage("Site scraping completed")

        # Update UI
        self.scrape_button.setEnabled(True)
        self.start_button.setEnabled(True)

        # Display results
        self.display_site_scraping_results(results)

    def site_scraping_error(self, error_msg):
        """Handle site scraping error"""
        self.progress_bar.setValue(0)
        self.status_label.setText("❌ Site scraping failed")
        self.status_bar.showMessage("Site scraping failed")

        self.scrape_button.setEnabled(True)
        self.start_button.setEnabled(True)

        QMessageBox.critical(self, "Site Scraping Error", f"An error occurred during site scraping:\n\n{error_msg}")

    def display_site_scraping_results(self, results):
        """Display site scraping results in the UI"""
        if not results:
            return

        # Overview with scraping statistics
        stats = results.get('scraping_stats', {})
        summary = results.get('summary', {})

        overview = f"""Site Scraping Results
Site URL: {results.get('site_url', 'N/A')}
Completion Status: {results.get('completion_status', 'N/A')}

Scraping Statistics:
• Pages Scraped: {stats.get('pages_scraped', 0)}
• Pages Failed: {stats.get('pages_failed', 0)}
• Links Discovered: {stats.get('total_links_found', 0)}
• Content Size: {summary.get('total_content_size_mb', 0):.2f} MB
• Duration: {stats.get('elapsed_time_seconds', 0):.1f} seconds
• Success Rate: {summary.get('success_rate', 0):.1f}%

Content Analysis:
• Average Page Size: {summary.get('average_page_size', 0):.0f} bytes
• Total Words: {summary.get('content_stats', {}).get('total_words', 0):,}
• Average Words/Page: {summary.get('content_stats', {}).get('average_words_per_page', 0):.0f}
"""
        self.overview_text.setPlainText(overview)

        # Show scraped content in patterns tab
        if results.get('scraped_content'):
            content_list = results['scraped_content']
            content_text = f"Scraped {len(content_list)} pages:\n\n"

            for i, content in enumerate(content_list[:10], 1):  # Show first 10
                content_text += f"{i}. {content.get('title', 'No title')}\n"
                content_text += f"   URL: {content.get('url', 'N/A')}\n"
                content_text += f"   Words: {content.get('word_count', 0)}\n"
                content_text += f"   Relevance: {content.get('content_relevance', 0):.2f}\n\n"

            if len(content_list) > 10:
                content_text += f"... and {len(content_list) - 10} more pages"

            self.patterns_text.setPlainText(content_text)

        # Show any errors in insights tab
        if results.get('errors'):
            errors_text = "Scraping Errors:\n\n" + "\n".join(f"• {error}" for error in results['errors'][:10])
            self.insights_text.setPlainText(errors_text)

    def display_results(self, results):
        """Display research results in the UI"""
        if not results:
            return

        # Overview
        timing_info = ""
        definition_info = ""
        if results.get('intelligence_level') == 'time_based_super_enhanced':
            timing = results.get('timing', {})
            timing_info = f"""
Research Timing: {timing.get('total_duration_hours', 25)} hours total
Phase 1: {timing.get('phase_1_duration_hours', 1)} hour initial learning
Phase 2: {timing.get('phase_2_duration_hours', 24)} hours deep research"""

            # Check for definition answer
            initial_learning = results.get('research_phases', {}).get('initial_learning', {})
            if initial_learning.get('definition_answer'):
                question_asked = initial_learning.get('definition_question', 'What is the [topic]?')
                definition_info = f"""
Definition Question: {question_asked}
Definition Obtained: {initial_learning['definition_answer']}"""

        overview = f"""Research Topic: {results.get('topic', 'N/A')}
Intelligence Level: {results.get('intelligence_level', 'N/A').replace('_', ' ').title()}
Intelligence Score: {results.get('intelligence_score', 0):.1f}
Research Phases: {len(results.get('research_phases', {}))}
Timestamp: {results.get('timestamp', 'N/A')}
Success: {'Yes' if results.get('success') else 'No'}{timing_info}{definition_info}
"""
        self.overview_text.setPlainText(overview)

        # Questions - handle both research methods
        phases = results.get('research_phases', {})

        # For time-based research, questions are in deep_research phase
        questions_list = None
        if results.get('intelligence_level') == 'time_based_super_enhanced':
            deep_research = phases.get('deep_research', {})
            if isinstance(deep_research, dict):
                questions_list = deep_research.get('intelligent_questions')
        else:
            questions_list = phases.get('intelligent_questions')

        if questions_list and isinstance(questions_list, list):
            questions_text = "\n".join(f"{i+1}. {q}" for i, q in enumerate(questions_list[:15]))
            self.questions_text.setPlainText(questions_text)

        # Patterns - handle both research methods
        pattern_data = None
        if results.get('intelligence_level') == 'time_based_super_enhanced':
            deep_research = phases.get('deep_research', {})
            if isinstance(deep_research, dict):
                pattern_data = deep_research.get('pattern_research')
        else:
            pattern_data = phases.get('pattern_research')

        if pattern_data and isinstance(pattern_data, dict):
            patterns = f"""Central Concepts: {len(pattern_data.get('central_concepts', []))}
Concept Clusters: {len(pattern_data.get('concept_clusters', []))}
Knowledge Graph Nodes: {pattern_data.get('knowledge_graph_stats', {}).get('nodes', 0)}
Knowledge Graph Edges: {pattern_data.get('knowledge_graph_stats', {}).get('edges', 0)}
"""
            self.patterns_text.setPlainText(patterns)

        # Automation - handle both research methods
        auto_data = None
        if results.get('intelligence_level') == 'time_based_super_enhanced':
            deep_research = phases.get('deep_research', {})
            if isinstance(deep_research, dict):
                auto_data = deep_research.get('automation_results')
        else:
            auto_data = phases.get('automation_results')

        if auto_data and isinstance(auto_data, dict):
            automation = f"""Tasks Executed: {len(auto_data.get('task_results', {}))}
Success Rate: {auto_data.get('automation_metrics', {}).get('success_rate', 0):.1%}
Average Duration: {auto_data.get('automation_metrics', {}).get('average_duration', 0):.2f} seconds
"""
            self.automation_text.setPlainText(automation)

        # Insights - handle both research methods
        insights_data = None
        if results.get('intelligence_level') == 'time_based_super_enhanced':
            deep_research = phases.get('deep_research', {})
            if isinstance(deep_research, dict):
                insights_data = deep_research.get('advanced_insights')
        else:
            insights_data = phases.get('advanced_insights')

        if insights_data and isinstance(insights_data, dict):
            insights = f"""Semantic Insights: {len(insights_data.get('semantic_insights', []))}
Pattern Insights: {len(insights_data.get('pattern_insights', []))}
Automation Insights: {len(insights_data.get('automation_insights', []))}
Cross-Domain Insights: {len(insights_data.get('cross_domain_insights', []))}
Recommendations: {len(insights_data.get('recommendations', []))}

Top Recommendations:
"""
            if 'recommendations' in insights_data:
                insights += "\n".join(f"• {rec}" for rec in insights_data['recommendations'][:5])

            self.insights_text.setPlainText(insights)

        # Report
        if 'comprehensive_report' in phases:
            report = phases['comprehensive_report']
            if isinstance(report, str):
                self.report_text.setPlainText(report)


    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Super Enhanced Research Agent",
            "Super Enhanced Research Agent\n\n"
            "Maximum Intelligence Without API Keys\n\n"
            "A comprehensive research automation system with:\n"
            "• Advanced heuristic intelligence\n"
            "• Pattern recognition and analysis\n"
            "• Automated task execution\n"
            "• Self-improvement capabilities\n"
            "• Time-based research workflows\n"
            "• Intelligent question generation\n\n"
            "Version: 1.0.0"
        )

def main():
    """Main application entry point"""
    try:
        app = QApplication(sys.argv)

        # Check if we have a display (for headless environments)
        if not app.platformName():
            print("❌ Error: No display environment detected.")
            print("💡 To run the desktop GUI, you need:")
            print("   1. A Windows desktop environment")
            print("   2. Run from desktop (not terminal)")
            print("   3. Or use: python run_desktop_gui.py")
            print("   4. Or use the web UI: python run_ui.py")
            sys.exit(1)

        # Set application properties
        app.setApplicationName("Super Enhanced Research Agent")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("Research Agent Team")

        # Create and show main window
        window = ResearchAgentGUI()
        window.show()

        # Start event loop
        sys.exit(app.exec())

    except Exception as e:
        print(f"❌ Failed to start desktop GUI: {e}")
        print("💡 Try running from desktop environment or use web UI:")
        print("   python run_ui.py  # Web-based interface")
        sys.exit(1)

if __name__ == "__main__":
    main()