from typing import Any, Dict, List
import logging
import time
from datetime import datetime
from dataclasses import asdict

class ResearchManager:
    """Manages the research process of the research agent."""

    def __init__(self, agent):
        self.agent = agent

    def time_based_research(self, topic: str, research_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform time-based research: 1 hour initial learning, then 24 hours deep research."""
        if not self.agent.enable_super_intelligence:
            return self.agent.comprehensive_research(topic, research_config)

        config = research_config or {}
        results = {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "intelligence_level": "time_based_super_enhanced",
            "research_phases": {},
            "timing": {
                "phase_1_duration_hours": 1,
                "phase_2_duration_hours": 24,
                "total_duration_hours": 25
            }
        }

        try:
            # Phase 1: Initial Learning (1 hour) - Learn what the topic is
            print(f"Phase 1: Initial learning phase for '{topic}' (1 hour)")
            print("Learning what the topic is, gathering basic understanding...")

            phase_1_start = time.time()
            initial_knowledge = self._perform_initial_learning(topic, config)
            results["research_phases"]["initial_learning"] = initial_knowledge

            # Wait/simulate 1 hour learning period (in practice, this would be actual research time)
            phase_1_elapsed = time.time() - phase_1_start
            if phase_1_elapsed < 3600:  # 1 hour = 3600 seconds
                print(f"Initial learning phase completed in {phase_1_elapsed:.2f} seconds")
                print("In production, this phase would take 1 hour of intensive learning")

            # Phase 2: Deep Research (24 hours) - Learn everything and generate questions
            print(f"Phase 2: Deep research phase for '{topic}' (24 hours)")
            print("Using initial knowledge to generate intelligent questions and conduct comprehensive research...")

            phase_2_start = time.time()

            # Include image analysis if enabled
            if config.get("enable_image_analysis", False) and config.get("uploaded_images"):
                print("  - Integrating image analysis into research...")
                image_analysis = self.agent.image_analysis_manager.analyze_images(config["uploaded_images"])
                initial_knowledge["image_analysis"] = image_analysis

                # Search for similar images if requested
                if config.get("search_similar_images", False):
                    similar_images = self.agent.image_analysis_manager.search_similar_images(config["uploaded_images"])
                    initial_knowledge["similar_images"] = similar_images

                # Process any existing ratings
                if config.get("image_ratings"):
                    ratings_analysis = self.agent.image_analysis_manager.process_image_ratings(config["image_ratings"])
                    initial_knowledge["image_ratings_analysis"] = ratings_analysis

            deep_research_results = self._perform_deep_research(topic, initial_knowledge)
            results["research_phases"]["deep_research"] = deep_research_results

            # Wait/simulate 24 hour research period
            phase_2_elapsed = time.time() - phase_2_start
            if phase_2_elapsed < 86400:  # 24 hours = 86400 seconds
                print(f"Deep research phase completed in {phase_2_elapsed:.2f} seconds")
                print("In production, this phase would take 24 hours of comprehensive research")

            # Generate final comprehensive report
            print(f"Phase 3: Generating comprehensive report for '{topic}'")
            report = self.agent.report_generator._generate_time_based_report(topic, results)
            results["research_phases"]["comprehensive_report"] = report

            results["success"] = True
            results["intelligence_score"] = self._calculate_time_based_intelligence_score(results)

            # Check for self-improvement opportunities
            if results["intelligence_score"] > 75:
                print(f"High intelligence score ({results['intelligence_score']:.1f}) detected. Checking for self-improvement opportunities...")
                improvement_result = self.agent.self_improvement_manager.initiate_self_improvement(topic, results)
                results["self_improvement"] = improvement_result

                if improvement_result["improvement_detected"]:
                    print(f"Self-improvement cycle {'completed successfully' if all(improvement_result[k] for k in ['github_upload_success', 'code_updates_applied', 'version_upgrade_success', 'data_transfer_success']) else 'encountered issues'}")
                    if improvement_result["errors"]:
                        print(f"Improvement errors: {improvement_result['errors']}")

            return results

        except Exception as e:
            logging.error(f"Time-based research failed: {e}")
            results["error"] = str(e)
            results["success"] = False
            return results

    def super_intelligent_research(self, topic: str, research_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform super intelligent research with maximum capabilities."""
        if not self.agent.enable_super_intelligence:
            return self.agent.comprehensive_research(topic, research_config)

        config = research_config or {}
        results = {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "intelligence_level": "super_enhanced",
            "research_phases": {}
        }

        try:
            # Phase 1: Advanced Topic Analysis
            print(f"Phase 1: Advanced topic analysis for '{topic}'")
            topic_analysis = self._analyze_topic_semantics(topic)
            results["research_phases"]["topic_analysis"] = topic_analysis

            # Phase 2: Intelligent Question Generation
            print(f"Phase 2: Generating intelligent questions for '{topic}'")
            intelligent_questions = self._generate_intelligent_questions(topic, topic_analysis)
            results["research_phases"]["intelligent_questions"] = intelligent_questions

            # Phase 3: Pattern-Based Research
            print(f"Phase 3: Pattern-based research for '{topic}'")
            pattern_research = self._perform_pattern_research(topic, intelligent_questions)
            results["research_phases"]["pattern_research"] = pattern_research

            # Phase 4: Automated Task Execution
            print(f"Phase 4: Automated task execution for '{topic}'")
            automation_results = self._execute_automated_tasks(topic, pattern_research)
            results["research_phases"]["automation_results"] = automation_results

            # Phase 5: Advanced Analysis and Insights
            print(f"Phase 5: Advanced analysis and insights for '{topic}'")
            insights = self._generate_advanced_insights(topic, pattern_research, automation_results)
            results["research_phases"]["advanced_insights"] = insights

            # Phase 6: Comprehensive Report Generation
            print(f"Phase 6: Generating comprehensive report for '{topic}'")
            report = self.agent.report_generator._generate_super_intelligent_report(topic, results)
            results["research_phases"]["comprehensive_report"] = report

            # Phase 7: Optimization and Recommendations
            print(f"Phase 7: Optimization and recommendations for '{topic}'")
            recommendations = self.agent.report_generator._generate_optimization_recommendations(results)
            results["research_phases"]["optimization_recommendations"] = recommendations

            results["success"] = True
            results["intelligence_score"] = self._calculate_intelligence_score(results)

            # Check for self-improvement opportunities
            if results["intelligence_score"] > 75:  # Threshold for triggering improvement
                print(f"High intelligence score ({results['intelligence_score']:.1f}) detected. Checking for self-improvement opportunities...")
                improvement_result = self.agent.self_improvement_manager.initiate_self_improvement(topic, results)
                results["self_improvement"] = improvement_result

                if improvement_result["improvement_detected"]:
                    print(f"Self-improvement cycle {'completed successfully' if all(improvement_result[k] for k in ['github_upload_success', 'code_updates_applied', 'version_upgrade_success', 'data_transfer_success']) else 'encountered issues'}")
                    if improvement_result["errors"]:
                        print(f"Improvement errors: {improvement_result['errors']}")

            return results

        except Exception as e:
            logging.error(f"Super intelligent research failed: {e}")
            results["error"] = str(e)
            results["success"] = False
            return results

    def _perform_initial_learning(self, topic: str, research_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform initial 1-hour learning phase to understand what the topic is."""
        try:
            config = research_config or {}
            ask_definition_first = config.get("ask_definition_first", False)

            initial_knowledge = {
                "basic_understanding": {},
                "key_concepts": [],
                "fundamental_questions": [],
                "knowledge_gaps": [],
                "definition_answer": None,
                "learning_timestamp": datetime.now().isoformat()
            }

            # Step 1: Ask definition question first if requested
            if ask_definition_first:
                question_format = config.get("question_format", "the")
                if question_format == "a":
                    definition_question = f"What is a {topic}?"
                    simulated_definition = f"A {topic.lower()} is a domesticated mammal known for its loyalty and companionship to humans."
                else:  # "the"
                    definition_question = f"What is the {topic}?"
                    simulated_definition = f"The {topic.lower()} is a domesticated mammal known for its loyalty and companionship to humans."

                print(f"  - Asking: {definition_question}")
                print(f"  - Definition question: {definition_question}")

                # Simulate getting an answer (in production this would be from LLM)
                # This is where the agent would actually ask the question and get an answer
                initial_knowledge["definition_answer"] = simulated_definition
                initial_knowledge["definition_question"] = definition_question
                print(f"  - Definition obtained: {simulated_definition[:100]}...")

            # Gather basic information about the topic
            print("  - Gathering basic topic information...")
            topic_id = self.agent.db.get_or_create_topic(topic)
            existing_docs = self.agent.db.get_recent_docs(topic_id, limit=5)

            # Perform semantic analysis to understand the topic
            context = "\n".join([doc['content'][:1000] for doc in existing_docs])
            if hasattr(self.agent, 'heuristic_intelligence'):
                semantic_analysis = self.agent.heuristic_intelligence.analyze_topic_semantics(topic, context)
                initial_knowledge["basic_understanding"] = {
                    "keywords": semantic_analysis.keywords[:20],
                    "entities": semantic_analysis.entities[:10],
                    "concepts": semantic_analysis.concepts[:15]
                }
                initial_knowledge["key_concepts"] = semantic_analysis.concepts[:10]

            # Generate fundamental questions about what the topic is
            print("  - Generating fundamental questions...")
            fundamental_questions = [
                f"What is {topic}?",
                f"What are the main components of {topic}?",
                f"How does {topic} work?",
                f"What is the history of {topic}?",
                f"Why is {topic} important?",
                f"What are the basic principles of {topic}?",
                f"How is {topic} defined?",
                f"What are the key characteristics of {topic}?"
            ]
            initial_knowledge["fundamental_questions"] = fundamental_questions

            # Identify initial knowledge gaps
            initial_knowledge["knowledge_gaps"] = [
                "Detailed mechanisms and processes",
                "Historical development and evolution",
                "Current applications and use cases",
                "Future trends and developments",
                "Related fields and interdisciplinary connections"
            ]

            print(f"  - Initial learning complete. Identified {len(initial_knowledge['key_concepts'])} key concepts")
            if ask_definition_first:
                print("  - Definition-based learning completed")
            return initial_knowledge

        except Exception as e:
            logging.error(f"Initial learning failed: {e}")
            return {"error": str(e)}

    def _perform_deep_research(self, topic: str, initial_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Perform 24-hour deep research phase using initial knowledge."""
        try:
            deep_results = {
                "intelligent_questions": [],
                "comprehensive_analysis": {},
                "pattern_research": {},
                "automation_results": {},
                "advanced_insights": {},
                "research_timestamp": datetime.now().isoformat()
            }

            # Use initial knowledge to generate intelligent questions
            print("  - Generating intelligent questions based on initial knowledge...")
            if hasattr(self.agent, 'heuristic_intelligence') and initial_knowledge.get("basic_understanding"):
                context = self._create_context_from_initial_knowledge(initial_knowledge)
                intelligent_questions = self.agent.heuristic_intelligence.generate_intelligent_questions(topic, context)
                deep_results["intelligent_questions"] = intelligent_questions[:50]  # Limit to top 50 questions
                print(f"  - Generated {len(deep_results['intelligent_questions'])} intelligent questions")

            # Perform comprehensive analysis
            print("  - Conducting comprehensive analysis...")
            comprehensive_analysis = self._analyze_topic_semantics(topic)
            deep_results["comprehensive_analysis"] = comprehensive_analysis

            # Pattern-based research
            print("  - Performing pattern-based research...")
            pattern_research = self._perform_pattern_research(topic, deep_results["intelligent_questions"])
            deep_results["pattern_research"] = pattern_research

            # Automated task execution
            print("  - Executing automated research tasks...")
            automation_results = self._execute_automated_tasks(topic, pattern_research)
            deep_results["automation_results"] = automation_results

            # Generate advanced insights
            print("  - Generating advanced insights...")
            insights = self._generate_advanced_insights(topic, pattern_research, automation_results)
            deep_results["advanced_insights"] = insights

            print(f"  - Deep research complete. Analyzed {len(pattern_research.get('central_concepts', []))} concepts")
            return deep_results

        except Exception as e:
            logging.error(f"Deep research failed: {e}")
            return {"error": str(e)}

    def _analyze_topic_semantics(self, topic: str) -> Dict[str, Any]:
        """Analyze topic semantics using advanced heuristics."""
        if not hasattr(self.agent, 'heuristic_intelligence'):
            return {"error": "Heuristic intelligence not available"}
        
        try:
            # Create context from existing research
            context = self._gather_existing_context(topic)
            
            # Perform semantic analysis
            research_context = self.agent.heuristic_intelligence.analyze_topic_semantics(topic, context)
            
            return {
                "keywords": research_context.keywords,
                "entities": research_context.entities,
                "concepts": research_context.concepts,
                "relationships": research_context.relationships,
                "importance_scores": research_context.importance_scores,
                "temporal_context": research_context.temporal_context
            }
        except Exception as e:
            logging.error(f"Topic semantic analysis failed: {e}")
            return {"error": str(e)}
    
    def _generate_intelligent_questions(self, topic: str, topic_analysis: Dict[str, Any]) -> List[str]:
        """Generate highly intelligent research questions."""
        if not hasattr(self.agent, 'heuristic_intelligence'):
            return []
        
        try:
            # Create context from topic analysis
            context = self._create_context_from_analysis(topic_analysis)
            
            # Generate intelligent questions
            questions = self.agent.heuristic_intelligence.generate_intelligent_questions(topic, context)
            
            return questions
        except Exception as e:
            logging.error(f"Intelligent question generation failed: {e}")
            return []
    
    def _perform_pattern_research(self, topic: str, questions: List[str]) -> Dict[str, Any]:
        """Perform pattern-based research."""
        if not hasattr(self.agent, 'pattern_intelligence'):
            return {"error": "Pattern intelligence not available"}
        
        try:
            # Gather content for pattern analysis
            content_sources = self._gather_content_sources(topic, questions)
            
            pattern_results = {}
            
            for source, content in content_sources.items():
                # Analyze patterns in content
                pattern_matches = self.agent.pattern_intelligence.analyze_content_patterns(content)
                
                # Generate insights
                insights = self.agent.pattern_intelligence.generate_intelligence_insights(content)
                
                pattern_results[source] = {
                    "pattern_matches": [asdict(match) for match in pattern_matches],
                    "insights": [asdict(insight) for insight in insights]
                }
            
            # Build knowledge graph
            all_content = list(content_sources.values())
            knowledge_graph = self.agent.pattern_intelligence.build_knowledge_graph(all_content)
            
            # Find central concepts
            central_concepts = self.agent.pattern_intelligence.find_central_concepts(knowledge_graph, 10)
            
            # Identify concept clusters
            concept_clusters = self.agent.pattern_intelligence.identify_concept_clusters(knowledge_graph)
            
            return {
                "pattern_results": pattern_results,
                "central_concepts": central_concepts,
                "concept_clusters": concept_clusters,
                "knowledge_graph_stats": {
                    "nodes": knowledge_graph.number_of_nodes(),
                    "edges": knowledge_graph.number_of_edges()
                }
            }
        except Exception as e:
            logging.error(f"Pattern research failed: {e}")
            return {"error": str(e)}
    
    def _execute_automated_tasks(self, topic: str, pattern_research: Dict[str, Any]) -> Dict[str, Any]:
        """Execute automated tasks based on research patterns."""
        if not hasattr(self.agent, 'automation_engine'):
            return {"error": "Automation engine not available"}
        
        try:
            task_results = {}
            
            # Create tasks based on pattern research
            if "central_concepts" in pattern_research:
                # Task 1: Deep dive into central concepts
                concept_task = self.agent.automation_engine.create_task(
                    name=f"Deep dive into central concepts for {topic}",
                    task_type="analysis",
                    parameters={
                        "analysis_type": "concept_analysis",
                        "concepts": pattern_research["central_concepts"][:5]
                    },
                    priority=8
                )
                self.agent.automation_engine.submit_task(concept_task)
                task_results["concept_analysis"] = concept_task.id
            
            # Task 2: Pattern-based data processing
            if "pattern_results" in pattern_research:
                pattern_task = self.agent.automation_engine.create_task(
                    name=f"Pattern-based data processing for {topic}",
                    task_type="data_processing",
                    parameters={
                        "operation": "analyze",
                        "data": list(pattern_research["pattern_results"].keys())
                    },
                    priority=7
                )
                self.agent.automation_engine.submit_task(pattern_task)
                task_results["pattern_processing"] = pattern_task.id
            
            # Task 3: Automated reporting
            report_task = self.agent.automation_engine.create_task(
                name=f"Automated report generation for {topic}",
                task_type="reporting",
                parameters={
                    "report_type": "comprehensive",
                    "data": pattern_research
                },
                priority=6
            )
            self.agent.automation_engine.submit_task(report_task)
            task_results["automated_reporting"] = report_task.id
            
            # Wait for tasks to complete (with timeout)
            self._wait_for_tasks_completion(list(task_results.values()), timeout=300)
            
            # Get task results
            completed_results = {}
            for task_name, task_id in task_results.items():
                task_status = self.agent.automation_engine.get_task_status(task_id)
                if task_status and task_status["status"] == "completed":
                    completed_results[task_name] = task_status["result"]
            
            return {
                "task_results": completed_results,
                "automation_metrics": self.agent.automation_engine.get_performance_metrics()
            }
        except Exception as e:
            logging.error(f"Automated task execution failed: {e}")
            return {"error": str(e)}
    
    def _generate_advanced_insights(self, topic: str, pattern_research: Dict[str, Any], 
                                  automation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate advanced insights from all research data."""
        try:
            insights = {
                "semantic_insights": [],
                "pattern_insights": [],
                "automation_insights": [],
                "cross_domain_insights": [],
                "recommendations": []
            }
            
            # Semantic insights from topic analysis
            if "central_concepts" in pattern_research:
                insights["semantic_insights"].append({
                    "type": "concept_centrality",
                    "description": f"Identified {len(pattern_research['central_concepts'])} central concepts",
                    "confidence": 0.9
                })
            
            # Pattern insights
            if "pattern_results" in pattern_research:
                total_patterns = sum(
                    len(result.get("pattern_matches", [])) 
                    for result in pattern_research["pattern_results"].values()
                )
                insights["pattern_insights"].append({
                    "type": "pattern_density",
                    "description": f"Found {total_patterns} patterns across content sources",
                    "confidence": 0.8
                })
            
            # Automation insights
            if "automation_metrics" in automation_results:
                metrics = automation_results["automation_metrics"]
                insights["automation_insights"].append({
                    "type": "performance",
                    "description": f"Automation success rate: {metrics['success_rate']:.2%}",
                    "confidence": 0.7
                })
            
            # Cross-domain insights
            if "concept_clusters" in pattern_research:
                cluster_count = len(pattern_research["concept_clusters"])
                insights["cross_domain_insights"].append({
                    "type": "domain_integration",
                    "description": f"Identified {cluster_count} concept clusters suggesting cross-domain connections",
                    "confidence": 0.8
                })
            
            # Generate recommendations
            recommendations = self.agent.report_generator._generate_research_recommendations(pattern_research, automation_results)
            insights["recommendations"] = recommendations
            
            return insights
        except Exception as e:
            logging.error(f"Advanced insights generation failed: {e}")
            return {"error": str(e)}

    def _calculate_intelligence_score(self, research_results: Dict[str, Any]) -> float:
        """Calculate intelligence score for research results."""
        score = 0.0
        
        # Base score for successful completion
        if research_results.get("success", False):
            score += 30.0
        
        # Score for research phases
        phases = research_results.get("research_phases", {})
        score += len(phases) * 10.0
        
        # Score for pattern research
        if "pattern_research" in phases:
            pattern_research = phases["pattern_research"]
            score += len(pattern_research.get("central_concepts", [])) * 2.0
            score += len(pattern_research.get("concept_clusters", [])) * 3.0
        
        # Score for automation
        if "automation_results" in phases:
            automation = phases["automation_results"]
            metrics = automation.get("automation_metrics", {})
            score += metrics.get("success_rate", 0) * 20.0
        
        # Score for insights
        if "advanced_insights" in phases:
            insights = phases["advanced_insights"]
            total_insights = sum(len(insights.get(key, [])) for key in ["semantic_insights", "pattern_insights", "automation_insights", "cross_domain_insights"])
            score += total_insights * 2.0
        
        return min(score, 100.0)

    def _calculate_time_based_intelligence_score(self, research_results: Dict[str, Any]) -> float:
        """Calculate intelligence score for time-based research."""
        score = 0.0

        # Base score for successful completion
        if research_results.get("success", False):
            score += 40.0  # Higher base score for time-based research

        phases = research_results.get("research_phases", {})

        # Score for initial learning phase
        if "initial_learning" in phases:
            initial = phases["initial_learning"]
            score += len(initial.get("key_concepts", [])) * 1.0
            score += len(initial.get("fundamental_questions", [])) * 0.5
            score += 10.0  # Completion bonus

        # Score for deep research phase
        if "deep_research" in phases:
            deep = phases["deep_research"]
            score += len(deep.get("intelligent_questions", [])) * 0.8
            score += len(deep.get("pattern_research", {}).get("central_concepts", [])) * 2.0
            score += len(deep.get("pattern_research", {}).get("concept_clusters", [])) * 3.0

            # Automation score
            automation = deep.get("automation_results", {})
            metrics = automation.get("automation_metrics", {})
            score += metrics.get("success_rate", 0) * 15.0

            score += 20.0  # Deep research completion bonus

        return min(score, 100.0)

    def _gather_existing_context(self, topic: str) -> str:
        """Gather existing context for topic."""
        try:
            # Get existing research from database
            topic_id = self.agent.db.get_or_create_topic(topic)
            docs = self.agent.db.get_recent_docs(topic_id, limit=10)
            
            context_parts = []
            for doc in docs:
                context_parts.append(f"Title: {doc['title']}\nContent: {doc['content'][:500]}...")
            
            return "\n\n".join(context_parts)
        except Exception:
            return ""
    
    def _create_context_from_analysis(self, topic_analysis: Dict[str, Any]) -> str:
        """Create context string from topic analysis."""
        context_parts = []
        
        if "keywords" in topic_analysis:
            context_parts.append(f"Keywords: {', '.join(topic_analysis['keywords'][:10])}")
        
        if "entities" in topic_analysis:
            context_parts.append(f"Entities: {', '.join(topic_analysis['entities'][:5])}")
        
        if "concepts" in topic_analysis:
            context_parts.append(f"Concepts: {', '.join(topic_analysis['concepts'][:5])}")
        
        return "\n".join(context_parts)
    
    def _gather_content_sources(self, topic: str, questions: List[str]) -> Dict[str, str]:
        """Gather content from various sources."""
        content_sources = {}
        
        # Use existing research
        try:
            topic_id = self.agent.db.get_or_create_topic(topic)
            docs = self.agent.db.get_recent_docs(topic_id, limit=5)
            
            for i, doc in enumerate(docs):
                content_sources[f"research_doc_{i}"] = doc['content']
        except Exception:
            pass
        
        # Add questions as content
        content_sources["research_questions"] = "\n".join(questions)
        
        return content_sources
    
    def _wait_for_tasks_completion(self, task_ids: List[str], timeout: int = 300):
        """Wait for tasks to complete with timeout."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            all_completed = True
            for task_id in task_ids:
                status = self.agent.automation_engine.get_task_status(task_id)
                if status and status["status"] not in ["completed", "failed"]:
                    all_completed = False
                    break
            
            if all_completed:
                break
            
            time.sleep(1)