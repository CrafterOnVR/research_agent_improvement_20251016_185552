import asyncio
import json
import logging
import random
import time
from datetime import datetime
from typing import Any, Dict, List, Optional


class GoalManager:
    """Manages the autonomous goals of the research agent."""

    def __init__(self, agent):
        self.agent = agent
        self.goal_history: List[Dict[str, Any]] = []
        self.active_goal: Optional[Dict[str, Any]] = None
        self.last_goal_time = time.time()
        self.goal_interval_minutes = 30
        self.autonomous_mode = True
        self.creativity_score = 10
        self.state_file = self.agent.state_file
        self._load_state()
        self.goal_categories = {
            "learning": {
                "weight": 0.20,
                "goals": [
                    "Learn about emerging technologies",
                    "Study a new programming language feature",
                    "Explore scientific breakthroughs",
                    "Analyze current trends in AI",
                    "Research historical events",
                    "Learn about different cultures",
                    "Study philosophical concepts",
                    "Explore mathematical theories"
                ]
            },
            "improvement": {
                "weight": 0.15,
                "goals": [
                    "Optimize code performance",
                    "Improve error handling",
                    "Enhance user interface",
                    "Add new features",
                    "Refactor complex functions",
                    "Improve documentation",
                    "Enhance security measures",
                    "Optimize memory usage"
                ]
            },
            "exploration": {
                "weight": 0.15,
                "goals": [
                    "Discover new websites to scrape",
                    "Explore new data sources",
                    "Find interesting research papers",
                    "Discover new tools and libraries",
                    "Explore new APIs",
                    "Find new datasets",
                    "Discover new communities",
                    "Explore new domains"
                ]
            },
            "maintenance": {
                "weight": 0.10,
                "goals": [
                    "Clean up old data",
                    "Optimize database queries",
                    "Update dependencies",
                    "Review and fix bugs",
                    "Update documentation",
                    "Clean up code comments",
                    "Organize project files",
                    "Review security settings"
                ]
            },
            "creativity": {
                "weight": 0.05,
                "goals": [
                    "Generate creative ideas",
                    "Design new features",
                    "Create helpful utilities",
                    "Develop new algorithms",
                    "Design better user experiences",
                    "Create educational content",
                    "Develop new research methods",
                    "Design innovative solutions"
                ]
            },
            "analysis": {
                "weight": 0.25,
                "goals": [
                    "Analyze collected data",
                    "Review research findings",
                    "Analyze performance metrics",
                    "Review user feedback",
                    "Analyze trends and patterns",
                    "Review system logs",
                    "Analyze knowledge gaps",
                    "Review improvement opportunities",
                    "Identify potential enhancements",
                    "Assess system optimization needs"
                ]
            },
            "thinking": {
                "weight": 0.10,
                "goals": [
                    "Evaluate reasoning abilities",
                    "Improve logical deduction",
                    "Enhance problem-solving skills",
                    "Practice critical thinking"
                ]
            },
            "autonomy": {
                "weight": 0.10,
                "goals": [
                    "Enhance Parallel Task Execution"
                ]
            }
        }

    def _load_state(self):
        """Load the agent's state from a file."""
        if self.agent.os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    self.creativity_score = state.get('creativity_score', 10)
            except (json.JSONDecodeError, IOError):
                self.creativity_score = 10

    def _initialize_autonomous_system(self):
        """Initialize the autonomous goal generation and pursuit system."""
        try:
            # Start autonomous goal timer
            self._start_autonomous_timer()

            logging.info("Autonomous goal system initialized")

        except Exception as e:
            logging.error(f"Failed to initialize autonomous system: {e}")
            self.autonomous_mode = False
        """Load the agent's state from a file."""
        if self.agent.os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    self.creativity_score = state.get('creativity_score', 10)
            except (json.JSONDecodeError, IOError):
                self.creativity_score = 10

    def _save_state(self):
        """Save the agent's state to a file."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump({'creativity_score': self.creativity_score}, f)
        except IOError as e:
            logging.error(f"Failed to save agent state: {e}")

    def _start_autonomous_timer(self):
        """Start the autonomous goal generation timer."""
        import threading
        import asyncio

        def autonomous_timer():
            """Timer function that runs every 30 minutes."""
            loop = self.agent.automation_engine.loop
            while self.autonomous_mode:
                try:
                    # Check if we should generate a new goal
                    current_time = time.time()
                    time_since_last_goal = current_time - self.last_goal_time

                    # Only generate goals if not actively researching
                    if (time_since_last_goal >= (self.goal_interval_minutes * 60) and
                        not self.agent._is_currently_researching()):

                        asyncio.run_coroutine_threadsafe(self._generate_and_execute_goal(), loop)
                        self.last_goal_time = current_time

                    # Sleep for 1 minute before checking again
                    time.sleep(60)

                except Exception as e:
                    logging.error(f"Autonomous timer error: {e}")
                    time.sleep(60)  # Wait before retrying

        # Start timer in background thread
        timer_thread = threading.Thread(target=autonomous_timer, daemon=True)
        timer_thread.start()
        logging.info(f"Autonomous goal timer started (interval: {self.goal_interval_minutes} minutes)")

    async def _generate_and_execute_goal(self):
        """Generate a random useful goal and execute it."""
        try:
            print(f"[ARINN-LOG] {datetime.now().isoformat()} - AUTONOMOUS: Starting goal generation cycle")

            # Check if research is currently active
            if self.agent._is_research_active():
                # QUEUE the goal for later execution instead of skipping
                if not hasattr(self, 'queued_goals'):
                    self.queued_goals = []

                # Only queue if we don't already have a queued goal and it's time for a new goal
                current_time = time.time()
                time_since_last_goal = current_time - self.last_goal_time
                if time_since_last_goal >= self.goal_interval_minutes * 60 and not self.queued_goals:
                    self.queued_goals.append({
                        'timestamp': current_time,
                        'reason': 'research_active'
                    })
                    print(f"[ARINN-LOG] {datetime.now().isoformat()} - AUTONOMOUS: Research active, goal queued for later execution")
                return

            # Check if we have queued goals to execute first
            if hasattr(self, 'queued_goals') and self.queued_goals:
                queued_item = self.queued_goals.pop(0)
                print(f"[ARINN-LOG] {datetime.now().isoformat()} - AUTONOMOUS: Executing queued goal")

                # Generate and execute the queued goal
                goal = self._generate_random_goal()
                if not goal:
                    print(f"[ARINN-LOG] {datetime.now().isoformat()} - AUTONOMOUS: No queued goal generated")
                    return

                self.active_goal = goal
                print(f"[ARINN-LOG] {datetime.now().isoformat()} - AUTONOMOUS: Generated queued goal - Category: {goal['category']}, Description: {goal['description']}")

                # Execute the queued goal
                print(f"[ARINN-LOG] {datetime.now().isoformat()} - AUTONOMOUS: Executing queued goal: {goal['description']}")
                result = await self.agent.goal_executor._execute_goal(goal)

                # Record the result
                goal_result = {
                    "goal": goal,
                    "result": result,
                    "timestamp": datetime.now().isoformat(),
                    "success": result.get("success", False),
                    "queued": True
                }

                self.goal_history.append(goal_result)
                self.active_goal = None
                self.last_goal_time = time.time()
                return

            # The chance of generating a novel goal is based on the creativity score
            import random
            chance_of_novel_goal = self.creativity_score / 100.0
            print(f"[ARINN-LOG] Creativity score: {self.creativity_score}/100. Chance of generating a novel goal: {chance_of_novel_goal:.0%}")

            if random.random() < chance_of_novel_goal:
                print(f"[ARINN-LOG] {datetime.now().isoformat()} - AUTONOMOUS: Attempting to generate a novel goal...")
                goal = self._generate_novel_goal()
                if goal:
                    print(f"[ARINN-LOG] {datetime.now().isoformat()} - AUTONOMOUS: Generated a novel goal!")
                else:
                    print(f"[ARINN-LOG] {datetime.now().isoformat()} - AUTONOMOUS: Novel goal generation failed, falling back to random goal.")
                    goal = self._generate_random_goal()
            else:
                goal = self._generate_random_goal()
            
            if not goal:
                print(f"[ARINN-LOG] {datetime.now().isoformat()} - AUTONOMOUS: No goal generated")
                return

            self.active_goal = goal
            print(f"[ARINN-LOG] {datetime.now().isoformat()} - AUTONOMOUS: Generated goal - Category: {goal['category']}, Description: {goal['description']}")

            # Execute the goal
            print(f"[ARINN-LOG] {datetime.now().isoformat()} - AUTONOMOUS: Executing goal: {goal['description']}")
            result = await self.agent.goal_executor._execute_goal(goal)

            # Record the result
            goal_result = {
                "goal": goal,
                "result": result,
                "timestamp": datetime.now().isoformat(),
                "success": result.get("success", False)
            }

            self.goal_history.append(goal_result)
            self.active_goal = None

            # Keep only last 50 goals in history
            if len(self.goal_history) > 50:
                self.goal_history = self.goal_history[-50:]

            success_status = "SUCCESS" if result.get("success", False) else "FAILED"
            print(f"[ARINN-LOG] {datetime.now().isoformat()} - AUTONOMOUS: Goal execution {success_status}: {goal['description']}")

        except Exception as e:
            print(f"[ARINN-LOG] {datetime.now().isoformat()} - AUTONOMOUS ERROR: Goal generation/execution failed: {e}")
            self.active_goal = None

    def _generate_novel_goal(self) -> Optional[Dict[str, Any]]:
        """Generate a novel goal by combining existing goals."""
        try:
            import random
            
            # Select two different random categories
            cat1_name, cat2_name = random.sample(list(self.goal_categories.keys()), 2)
            
            # Select a random goal from each category
            goal1_desc = random.choice(self.goal_categories[cat1_name]["goals"])
            goal2_desc = random.choice(self.goal_categories[cat2_name]["goals"])
            
            # Combine the goals to create a novel goal
            novel_description = f"{goal1_desc} and {goal2_desc}"
            novel_category = f"{cat1_name}-{cat2_name}"
            novel_priority = (self._calculate_goal_priority(cat1_name) + self._calculate_goal_priority(cat2_name)) / 2
            
            return {
                "id": f"novel_{int(time.time())}",
                "category": novel_category,
                "description": novel_description,
                "generated_at": datetime.now().isoformat(),
                "priority": novel_priority,
                "is_novel": True,
            }
        except Exception as e:
            logging.error(f"Novel goal generation failed: {e}")
            return None

    def _generate_random_goal(self) -> Optional[Dict[str, Any]]:
        """Generate a random useful goal based on weighted categories."""
        try:
            import random

            # Calculate total weight
            total_weight = sum(category["weight"] for category in self.goal_categories.values())

            # Select category based on weights
            rand_val = random.uniform(0, total_weight)
            cumulative_weight = 0

            selected_category = None
            for category_name, category_data in self.goal_categories.items():
                cumulative_weight += category_data["weight"]
                if rand_val <= cumulative_weight:
                    selected_category = category_name
                    break

            if not selected_category:
                return None

            # Select random goal from category
            category_goals = self.goal_categories[selected_category]["goals"]
            selected_goal_text = random.choice(category_goals)

            return {
                "id": f"{selected_category}_{int(time.time())}",
                "category": selected_category,
                "description": selected_goal_text,
                "generated_at": datetime.now().isoformat(),
                "priority": self._calculate_goal_priority(selected_category)
            }

        except Exception as e:
            logging.error(f"Goal generation failed: {e}")
            return None

    def _calculate_goal_priority(self, category: str, *args, **kwargs) -> int:
        """Calculate priority for a goal category."""
        import logging
        import traceback
        if args or kwargs:
            logging.error("Mismatched call to _calculate_goal_priority")
            logging.error(f"Arguments: {args}")
            logging.error(f"Keyword Arguments: {kwargs}")
            logging.error(traceback.format_exc())

        priorities = {
            "learning": 6,      # Important but not urgent
            "improvement": 7,   # Self-improvement is valuable
            "exploration": 5,   # Discovery is good but not critical
            "maintenance": 8,   # Keep system healthy
            "creativity": 4,    # Nice to have
            "analysis": 6       # Understanding is valuable
        }
        return priorities.get(category, 5)

    def _is_currently_researching(self) -> bool:
        """Check if the agent is currently performing research."""
        # Check if there's an active research state
        if self.agent.current_research_state:
            return True

        # Check if any automation tasks are running research-related tasks
        if hasattr(self.agent, 'automation_engine') and self.agent.automation_engine:
            active_tasks = self.agent.automation_engine.get_active_tasks()
            research_task_types = ['web_scraping', 'analysis', 'data_processing', 'reporting']

            for task in active_tasks:
                if task.get('task_type') in research_task_types:
                    return True

        return False


    def get_autonomous_status(self) -> Dict[str, Any]:
        """Get status of autonomous goal system."""
        return {
            "autonomous_mode": self.autonomous_mode,
            "goal_interval_minutes": self.goal_interval_minutes,
            "last_goal_time": datetime.fromtimestamp(self.last_goal_time).isoformat(),
            "active_goal": self.active_goal,
            "goals_completed": len(self.goal_history),
            "currently_researching": self._is_currently_researching(),
            "recent_goals": self.goal_history[-5:] if self.goal_history else []
        }

    def get_time_until_next_goal(self) -> Optional[float]:
        """Get seconds until next autonomous goal execution."""
        if not self.agent.enable_super_intelligence:
            return None

        current_time = time.time()
        time_since_last_goal = current_time - self.last_goal_time
        time_until_next = (self.goal_interval_minutes * 60) - time_since_last_goal

        return max(0, time_until_next) if time_until_next > 0 else 0

    def _get_all_autonomous_goals(self):
        """Get the complete list of autonomous goals."""
        return [
            # Self-Improvement Goals
            {
                'id': 'self_1',
                'title': 'Optimize Code Performance',
                'category': 'self_improvement',
                'base_priority': 7,
                'description': 'Analyze and optimize code performance bottlenecks'
            },
            {
                'id': 'self_2',
                'title': 'Improve Error Handling',
                'category': 'self_improvement',
                'base_priority': 6,
                'description': 'Enhance error handling and exception management'
            },
            {
                'id': 'self_3',
                'title': 'Update Documentation',
                'category': 'self_improvement',
                'base_priority': 5,
                'description': 'Improve code documentation and comments'
            },
            {
                'id': 'self_4',
                'title': 'Refactor Code Structure',
                'category': 'self_improvement',
                'base_priority': 6,
                'description': 'Refactor code for better maintainability'
            },

            # Intelligence Enhancement Goals
            {
                'id': 'intel_1',
                'title': 'Expand Knowledge Base',
                'category': 'intelligence',
                'base_priority': 8,
                'description': 'Learn new concepts and expand knowledge database'
            },
            {
                'id': 'intel_2',
                'title': 'Improve Pattern Recognition',
                'category': 'intelligence',
                'base_priority': 7,
                'description': 'Enhance pattern recognition algorithms'
            },
            {
                'id': 'intel_3',
                'title': 'Optimize Learning Algorithms',
                'category': 'intelligence',
                'base_priority': 7,
                'description': 'Improve machine learning and adaptation algorithms'
            },

            # Research Goals
            {
                'id': 'research_1',
                'title': 'Conduct Web Research',
                'category': 'research',
                'base_priority': 6,
                'description': 'Perform automated web research on relevant topics'
            },
            {
                'id': 'research_2',
                'title': 'Analyze Research Data',
                'category': 'research',
                'base_priority': 5,
                'description': 'Analyze collected research data for insights'
            },
            {
                'id': 'research_3',
                'title': 'Generate Research Questions',
                'category': 'research',
                'base_priority': 6,
                'description': 'Generate intelligent research questions'
            },

            # Automation Goals
            {
                'id': 'auto_1',
                'title': 'Optimize Task Scheduling',
                'category': 'automation',
                'base_priority': 5,
                'description': 'Improve automated task scheduling efficiency'
            },
            {
                'id': 'auto_2',
                'title': 'Enhance Workflow Orchestration',
                'category': 'automation',
                'base_priority': 6,
                'description': 'Improve automated workflow management'
            },

            # Performance Goals
            {
                'id': 'perf_1',
                'title': 'Optimize Memory Usage',
                'category': 'performance',
                'base_priority': 7,
                'description': 'Reduce memory usage and improve efficiency'
            },
            {
                'id': 'perf_2',
                'title': 'Improve Response Times',
                'category': 'performance',
                'base_priority': 6,
                'description': 'Optimize response times and latency'
            },
            {
                'id': 'perf_3',
                'title': 'Enhance Parallel Processing',
                'category': 'performance',
                'base_priority': 5,
                'description': 'Improve parallel processing capabilities'
            },

            # Security Goals
            {
                'id': 'sec_1',
                'title': 'Security Audit',
                'category': 'security',
                'base_priority': 4,
                'description': 'Perform security audit and vulnerability assessment'
            },
            {
                'id': 'sec_2',
                'title': 'Improve Data Protection',
                'category': 'security',
                'base_priority': 5,
                'description': 'Enhance data protection and privacy measures'
            },

            # Thinking Improvements Goals
            {
                'id': 'think_1',
                'title': 'Evaluate Reasoning Abilities',
                'category': 'thinking',
                'base_priority': 8,
                'description': 'Evaluate and improve logical reasoning capabilities'
            }
        ]

    def _select_autonomous_goal(self):
        """Select the next autonomous goal based on system state."""
        # Analyze current system state
        system_state = self._analyze_system_state()

        # Goal selection logic based on priorities
        goals_by_priority = self._get_goals_by_priority(system_state)

        # Filter out recently selected goals to ensure variety
        recent_goals = self.goal_history[-3:] if len(self.goal_history) >= 3 else self.goal_history
        recent_goal_ids = [goal.get('id') for goal in recent_goals]
        
        # Remove recently selected goals from consideration
        available_goals = [goal for goal in goals_by_priority if goal['id'] not in recent_goal_ids]
        
        # If no goals available after filtering, use all goals
        if not available_goals:
            available_goals = goals_by_priority

        # Add variety by sometimes selecting from top 3 goals instead of always the first
        import random
        if available_goals and len(available_goals) >= 3:
            # 70% chance to pick the top goal, 20% for second, 10% for third
            weights = [0.7, 0.2, 0.1]
            selected_index = random.choices(range(3), weights=weights)[0]
            selected_goal = available_goals[selected_index]
        elif available_goals:
            # If less than 3 goals, pick randomly from available
            selected_goal = random.choice(available_goals)
        else:
            # Fallback to random selection if no priorities
            selected_goal = self._get_random_goal()

        # Track the selected goal in history
        self.goal_history.append(selected_goal)
        if len(self.goal_history) > 10:  # Keep only last 10 goals
            self.goal_history = self.goal_history[-10:]

        return selected_goal

    def _analyze_system_state(self):
        """Analyze current system state for goal selection."""
        import random
        import time
        
        # Add some variability to prevent always selecting the same goal
        base_intelligence = getattr(self, 'last_intelligence_score', 50)
        # Add small random variation to intelligence score
        intelligence_variation = random.uniform(-5, 5)
        intelligence_score = max(10, min(90, base_intelligence + intelligence_variation))
        
        state = {
            'intelligence_score': intelligence_score,
            'memory_usage': self.agent._get_memory_usage(),
            'active_components': self.agent._count_active_components(),
            'recent_performance': self.agent._analyze_recent_performance(),
            'bottlenecks': self.agent._identify_bottlenecks(),
            'opportunities': self.agent._identify_improvement_opportunities(),
            'time_factor': time.time() % 3600,  # Add time-based variation
            'random_factor': random.random()  # Add pure randomness
        }
        return state

    def _get_goals_by_priority(self, system_state):
        """Get goals sorted by priority based on system state."""
        all_goals = self._get_all_autonomous_goals()

        # Score each goal based on system state
        scored_goals = []
        for goal in all_goals:
            score = self._calculate_goal_priority_with_state(goal, system_state)
            scored_goals.append({
                **goal,
                'priority_score': score
            })

        # Sort by priority score (highest first)
        scored_goals.sort(key=lambda x: x['priority_score'], reverse=True)

        return scored_goals

    def _calculate_goal_priority_with_state(self, goal, system_state):
        """Calculate priority score for a goal based on system state."""
        import random
        
        score = goal['base_priority']

        # Intelligence improvement goals get bonus if intelligence is low
        if goal['category'] == 'intelligence' and system_state['intelligence_score'] < 70:
            score += 3

        # Performance goals get bonus if memory usage is high
        if goal['category'] == 'performance' and system_state['memory_usage'] > 80:
            score += 3

        # Self-improvement goals get bonus if there are bottlenecks
        if goal['category'] == 'self_improvement' and system_state['bottlenecks']:
            score += 2

        # Research goals get bonus if intelligence is high (can handle complex research)
        if goal['category'] == 'research' and system_state['intelligence_score'] > 75:
            score += 2

        # Add some randomness to prevent always selecting the same goal
        random_bonus = random.uniform(-1, 1)
        score += random_bonus
        
        # Time-based variation - different goals get slight bonuses at different times
        time_bonus = 0.5 * (system_state['time_factor'] / 3600) * (hash(goal['id']) % 3 - 1)
        score += time_bonus

        return min(max(score, 1), 10)  # Cap between 1 and 10

    def _get_random_goal(self):
        """Get a random goal as fallback."""
        import random
        goals = self._get_all_autonomous_goals()
        return random.choice(goals)

    def start_autonomous_mode(self):
        """Start autonomous goal pursuit mode."""
        if self.autonomous_mode:
            print("Autonomous mode already running")
            return

        self.autonomous_mode = True
        self.agent.autonomous_goal_count = 0
        self.agent.autonomous_start_time = datetime.now()

        print("🧠 ARINN AUTONOMOUS MODE ACTIVATED")
        print("=" * 50)
        print("Pursuing goals every 5 minutes for continuous self-improvement")
        print("Available goals: 90+ across 10 categories")
        print("Goal categories: Self-improvement, Intelligence, Research, Automation, Data, Security, UX, Integration, Performance, Innovation")
        print()

        # Start autonomous goal loop
        self._run_autonomous_loop()

    def stop_autonomous_mode(self):
        """Stop autonomous goal pursuit mode."""
        self.agent.autonomous_active = False
        duration = datetime.now() - self.agent.autonomous_start_time

        print("🛑 ARINN AUTONOMOUS MODE DEACTIVATED")
        print(f"Goals completed: {self.agent.autonomous_goal_count}")
        print(f"Duration: {duration}")
        print(".1f")
        print()

    def _run_autonomous_loop(self):
        """Run the autonomous goal pursuit loop."""
        import threading
        import time

        def autonomous_worker():
            while self.agent.autonomous_active:
                try:
                    # Check if it's time for a goal (every 5 minutes)
                    current_minute = datetime.now().minute
                    current_second = datetime.now().second

                    # Trigger on 5-minute marks (:00, :05, :10, :15, etc.)
                    should_trigger = (current_minute % 5 == 0) and (current_second < 10)

                    if should_trigger and not hasattr(self, '_last_goal_time'):
                        self._last_goal_time = datetime.now()
                        self.agent.goal_executor._execute_autonomous_goal()
                    elif should_trigger and hasattr(self, '_last_goal_time'):
                        # Check if it's been at least 4 minutes since last goal
                        time_since_last = (datetime.now() - self._last_goal_time).total_seconds()
                        if time_since_last >= 240:  # 4 minutes to avoid duplicates
                            self._last_goal_time = datetime.now()
                            self.agent.goal_executor._execute_autonomous_goal()

                    time.sleep(5)  # Check every 5 seconds

                except Exception as e:
                    print(f"Autonomous loop error: {e}")
                    time.sleep(30)  # Wait 30 seconds on error

        # Start autonomous thread
        autonomous_thread = threading.Thread(target=autonomous_worker, daemon=True)
        autonomous_thread.start()

        print("Autonomous goal pursuit thread started")
        print("Goals will be executed every 5 minutes")
        print()

    def _execute_autonomous_goal(self):
        """Execute a single autonomous goal."""
        try:
            self.agent.autonomous_goal_count += 1
            goal_start_time = datetime.now()

            print(f"[GOAL] GOAL #{self.agent.autonomous_goal_count} - {goal_start_time.strftime('%H:%M:%S')}")
            print("-" * 50)

            # Select a goal based on current system state
            selected_goal = self._select_autonomous_goal()

            print(f"Selected Goal: {selected_goal['title']}")
            print(f"Category: {selected_goal['category']}")
            # Use computed priority_score if present, else base_priority; fall back to 'N/A'
            priority_value = selected_goal.get('priority', selected_goal.get('priority_score', selected_goal.get('base_priority', 'N/A')))
            print(f"Priority: {priority_value}/10")
            print(f"Description: {selected_goal['description']}")
            print()

            # Execute the goal
            result = self.agent.goal_executor._pursue_goal(selected_goal)

            goal_duration = datetime.now() - goal_start_time

            print(f"[SUCCESS] GOAL COMPLETED in {goal_duration.total_seconds():.1f}s")
            print(f"Result: {result['status']}")
            if result.get('details'):
                print(f"Details: {result['details']}")
            print()

        except Exception as e:
            print(f"[ERROR] GOAL FAILED: {e}")
            print()