#!/usr/bin/env python3
"""
Super Intelligence Examples for the Enhanced Research Agent.

This script demonstrates the maximum capabilities of the research agent
without requiring any API keys - showing how to make it incredibly powerful.
"""

import os
import time
import json
from datetime import datetime

# Import the super enhanced agent
from research_agent.super_enhanced_agent import SuperEnhancedResearchAgent
from research_agent.enhanced_heuristics import EnhancedHeuristicIntelligence
from research_agent.pattern_intelligence import AdvancedPatternIntelligence
from research_agent.automation_engine import AdvancedAutomationEngine, AutomationTask, AutomationRule


def example_super_intelligent_research():
    """Example of super intelligent research without API key."""
    print("=== Super Intelligent Research Example ===")
    
    # Initialize super enhanced agent
    agent = SuperEnhancedResearchAgent(
        enable_advanced=True,
        enable_super_intelligence=True,
        safety_config="safety_config.json"
    )
    
    try:
        # Perform super intelligent research
        research_config = {
            "enable_web_research": True,
            "enable_github_research": True,
            "enable_file_analysis": True,
            "enable_workflow_execution": True,
            "web_urls": ["https://httpbin.org/html", "https://httpbin.org/json"],
            "analysis_directory": "./research_data"
        }
        
        print("Starting super intelligent research...")
        results = agent.super_intelligent_research("Artificial Intelligence Safety", research_config)
        
        if results.get("success"):
            print(f"✅ Super intelligent research completed!")
            print(f"Intelligence Score: {results.get('intelligence_score', 'N/A')}")
            print(f"Research Phases: {len(results.get('research_phases', {}))}")
            
            # Display key findings
            if "topic_analysis" in results["research_phases"]:
                analysis = results["research_phases"]["topic_analysis"]
                print(f"Keywords identified: {len(analysis.get('keywords', []))}")
                print(f"Entities found: {len(analysis.get('entities', []))}")
                print(f"Concepts discovered: {len(analysis.get('concepts', []))}")
            
            if "pattern_research" in results["research_phases"]:
                pattern_research = results["research_phases"]["pattern_research"]
                print(f"Central concepts: {len(pattern_research.get('central_concepts', []))}")
                print(f"Concept clusters: {len(pattern_research.get('concept_clusters', []))}")
            
            if "automation_results" in results["research_phases"]:
                automation = results["research_phases"]["automation_results"]
                metrics = automation.get("automation_metrics", {})
                print(f"Automation success rate: {metrics.get('success_rate', 0):.2%}")
                print(f"Tasks executed: {metrics.get('task_count', 0)}")
            
            # Save comprehensive report
            if "comprehensive_report" in results["research_phases"]:
                report = results["research_phases"]["comprehensive_report"]
                report_path = f"./super_intelligent_report_{int(time.time())}.md"
                with open(report_path, "w", encoding="utf-8") as f:
                    f.write(report)
                print(f"📄 Comprehensive report saved to: {report_path}")
        else:
            print(f"❌ Super intelligent research failed: {results.get('error')}")
            
    except Exception as e:
        print(f"❌ Error in super intelligent research: {e}")
    finally:
        agent.close()


def example_advanced_heuristic_intelligence():
    """Example of advanced heuristic intelligence."""
    print("\n=== Advanced Heuristic Intelligence Example ===")
    
    # Initialize heuristic intelligence
    heuristic = EnhancedHeuristicIntelligence()
    
    try:
        # Analyze topic semantics
        topic = "Machine Learning in Healthcare"
        context = """
        Machine learning is revolutionizing healthcare through predictive analytics, 
        medical imaging analysis, and personalized treatment recommendations. 
        Key technologies include deep learning, natural language processing, 
        and computer vision applications in medical diagnosis.
        """
        
        print(f"Analyzing topic: {topic}")
        research_context = heuristic.analyze_topic_semantics(topic, context)
        
        print(f"✅ Semantic analysis completed:")
        print(f"Keywords: {', '.join(research_context.keywords[:5])}")
        print(f"Entities: {', '.join(research_context.entities[:3])}")
        print(f"Concepts: {', '.join(research_context.concepts[:3])}")
        print(f"Relationships: {len(research_context.relationships)} connections")
        
        # Generate intelligent questions
        print("\nGenerating intelligent questions...")
        questions = heuristic.generate_intelligent_questions(topic, context, target=20)
        
        print(f"✅ Generated {len(questions)} intelligent questions:")
        for i, question in enumerate(questions[:5], 1):
            print(f"  {i}. {question}")
        
        # Generate comprehensive summary
        print("\nGenerating comprehensive summary...")
        summary = heuristic.generate_comprehensive_summary(topic, context)
        
        print(f"✅ Comprehensive summary generated ({len(summary)} characters)")
        print("Summary preview:")
        print(summary[:300] + "..." if len(summary) > 300 else summary)
        
    except Exception as e:
        print(f"❌ Heuristic intelligence error: {e}")


def example_pattern_intelligence():
    """Example of advanced pattern intelligence."""
    print("\n=== Pattern Intelligence Example ===")
    
    # Initialize pattern intelligence
    pattern_intel = AdvancedPatternIntelligence()
    
    try:
        # Sample content for analysis
        content = """
        Machine learning algorithms are becoming increasingly sophisticated, with deep learning
        models achieving state-of-the-art performance in computer vision tasks. The use of
        convolutional neural networks (CNNs) has revolutionized image recognition, while
        transformer architectures have transformed natural language processing.
        
        Recent developments in 2024 show significant improvements in model efficiency,
        with techniques like knowledge distillation and neural architecture search
        enabling deployment on resource-constrained devices. The integration of
        machine learning with edge computing is creating new opportunities for
        real-time inference and privacy-preserving applications.
        """
        
        print("Analyzing content patterns...")
        pattern_matches = pattern_intel.analyze_content_patterns(content)
        
        print(f"✅ Found {len(pattern_matches)} pattern matches:")
        for match in pattern_matches[:3]:
            print(f"  Category: {match.category}")
            print(f"  Confidence: {match.confidence:.2f}")
            print(f"  Matches: {match.matches[:2]}")
            print()
        
        # Generate intelligence insights
        print("Generating intelligence insights...")
        insights = pattern_intel.generate_intelligence_insights(content)
        
        print(f"✅ Generated {len(insights)} insights:")
        for insight in insights[:3]:
            print(f"  Type: {insight.insight_type}")
            print(f"  Description: {insight.description}")
            print(f"  Confidence: {insight.confidence:.2f}")
            print()
        
        # Build knowledge graph
        print("Building knowledge graph...")
        content_list = [content, "Additional content about AI and machine learning applications"]
        knowledge_graph = pattern_intel.build_knowledge_graph(content_list)
        
        print(f"✅ Knowledge graph built:")
        print(f"  Nodes: {knowledge_graph.number_of_nodes()}")
        print(f"  Edges: {knowledge_graph.number_of_edges()}")
        
        # Find central concepts
        central_concepts = pattern_intel.find_central_concepts(knowledge_graph, 5)
        print(f"  Central concepts: {[concept for concept, score in central_concepts[:3]]}")
        
    except Exception as e:
        print(f"❌ Pattern intelligence error: {e}")


def example_automation_engine():
    """Example of advanced automation engine."""
    print("\n=== Automation Engine Example ===")
    
    # Initialize automation engine
    automation = AdvancedAutomationEngine(max_workers=3)
    automation.start()
    
    try:
        # Create automation tasks
        tasks = []
        
        # Task 1: Web scraping
        web_task = automation.create_task(
            name="Web scraping for AI research",
            task_type="web_scraping",
            parameters={
                "url": "https://httpbin.org/html",
                "selectors": ["h1", "h2", "p"]
            },
            priority=8
        )
        tasks.append(web_task)
        
        # Task 2: Data processing
        data_task = automation.create_task(
            name="Process research data",
            task_type="data_processing",
            parameters={
                "data": ["AI", "ML", "Deep Learning", "Neural Networks"],
                "operation": "analyze"
            },
            priority=7
        )
        tasks.append(data_task)
        
        # Task 3: Analysis
        analysis_task = automation.create_task(
            name="Analyze patterns",
            task_type="analysis",
            parameters={
                "data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "analysis_type": "statistical"
            },
            priority=6
        )
        tasks.append(analysis_task)
        
        # Submit tasks
        print("Submitting automation tasks...")
        for task in tasks:
            automation.submit_task(task)
            print(f"  ✅ Submitted: {task.name}")
        
        # Wait for completion
        print("Waiting for task completion...")
        time.sleep(5)  # Give tasks time to complete
        
        # Check task status
        print("Task status:")
        for task in tasks:
            status = automation.get_task_status(task.id)
            if status:
                print(f"  {task.name}: {status['status']}")
                if status['status'] == 'completed':
                    print(f"    Result: {status['result']}")
        
        # Get performance metrics
        metrics = automation.get_performance_metrics()
        print(f"\n✅ Automation metrics:")
        print(f"  Task count: {metrics['task_count']}")
        print(f"  Success rate: {metrics['success_rate']:.2%}")
        print(f"  Average duration: {metrics['average_duration']:.2f}s")
        print(f"  Throughput: {metrics['throughput']:.2f} tasks/min")
        
    except Exception as e:
        print(f"❌ Automation engine error: {e}")
    finally:
        automation.stop()


def example_comprehensive_workflow():
    """Example of comprehensive workflow without API key."""
    print("\n=== Comprehensive Workflow Example ===")
    
    # Initialize super enhanced agent
    agent = SuperEnhancedResearchAgent(
        enable_advanced=True,
        enable_super_intelligence=True
    )
    
    try:
        # Create research data directory
        os.makedirs("./comprehensive_research", exist_ok=True)
        
        # Create sample research files
        sample_files = {
            "ai_safety_notes.md": """
# AI Safety Research Notes

## Key Concepts
- Alignment problem
- Interpretability
- Robustness
- Fairness

## Current Research
- Constitutional AI
- RLHF (Reinforcement Learning from Human Feedback)
- Adversarial training
- Uncertainty quantification
            """,
            "ml_applications.json": """
{
    "applications": [
        {"domain": "healthcare", "technologies": ["CNN", "RNN", "Transformer"]},
        {"domain": "finance", "technologies": ["LSTM", "Random Forest", "SVM"]},
        {"domain": "autonomous_vehicles", "technologies": ["CNN", "YOLO", "PointNet"]}
    ]
}
            """,
            "research_questions.txt": """
What are the key challenges in AI safety?
How can we ensure AI systems are aligned with human values?
What role does interpretability play in AI safety?
How can we make AI systems more robust?
What are the ethical implications of advanced AI?
            """
        }
        
        for filename, content in sample_files.items():
            filepath = f"./comprehensive_research/{filename}"
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  ✅ Created: {filename}")
        
        # Perform comprehensive research
        research_config = {
            "enable_web_research": True,
            "enable_github_research": True,
            "enable_file_analysis": True,
            "enable_workflow_execution": True,
            "web_urls": ["https://httpbin.org/html"],
            "analysis_directory": "./comprehensive_research"
        }
        
        print("\nStarting comprehensive research workflow...")
        results = agent.super_intelligent_research("AI Safety and Ethics", research_config)
        
        if results.get("success"):
            print(f"✅ Comprehensive workflow completed!")
            print(f"Intelligence Score: {results.get('intelligence_score', 'N/A')}")
            
            # Display workflow results
            phases = results.get("research_phases", {})
            print(f"\nWorkflow phases completed:")
            for phase_name, phase_data in phases.items():
                print(f"  ✅ {phase_name.replace('_', ' ').title()}")
                if isinstance(phase_data, dict) and "error" not in phase_data:
                    if "keywords" in phase_data:
                        print(f"    Keywords: {len(phase_data['keywords'])}")
                    if "central_concepts" in phase_data:
                        print(f"    Central concepts: {len(phase_data['central_concepts'])}")
                    if "task_results" in phase_data:
                        print(f"    Tasks executed: {len(phase_data['task_results'])}")
            
            # Get super intelligence status
            status = agent.get_super_intelligence_status()
            print(f"\nSuper intelligence status:")
            print(f"  Enabled: {status.get('enabled', False)}")
            print(f"  Heuristic intelligence: {status.get('heuristic_intelligence', False)}")
            print(f"  Pattern intelligence: {status.get('pattern_intelligence', False)}")
            print(f"  Automation engine: {status.get('automation_engine', False)}")
            
        else:
            print(f"❌ Comprehensive workflow failed: {results.get('error')}")
            
    except Exception as e:
        print(f"❌ Comprehensive workflow error: {e}")
    finally:
        agent.close()


def main():
    """Run all super intelligence examples."""
    print("🚀 Super Enhanced Research Agent - Maximum Intelligence Examples")
    print("=" * 70)
    print("Demonstrating maximum capabilities WITHOUT requiring API keys!")
    print("=" * 70)
    
    # Set up environment
    os.makedirs("./research_data", exist_ok=True)
    os.makedirs("./comprehensive_research", exist_ok=True)
    
    try:
        # Run examples
        example_super_intelligent_research()
        example_advanced_heuristic_intelligence()
        example_pattern_intelligence()
        example_automation_engine()
        example_comprehensive_workflow()
        
        print("\n" + "=" * 70)
        print("🎉 All super intelligence examples completed!")
        print("\nKey Benefits of Super Enhanced Research Agent:")
        print("✅ No API key required - completely self-contained")
        print("✅ Advanced heuristic intelligence for smart question generation")
        print("✅ Pattern recognition for deep content analysis")
        print("✅ Automation engine for complex task orchestration")
        print("✅ Multi-modal research capabilities")
        print("✅ Comprehensive safety controls")
        print("✅ Real-time performance monitoring")
        print("✅ Advanced workflow orchestration")
        print("\nThe neural network now has MAXIMUM control and intelligence!")
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        # Cleanup
        print("\nCleaning up...")
        try:
            import shutil
            if os.path.exists("./research_data"):
                shutil.rmtree("./research_data")
            if os.path.exists("./comprehensive_research"):
                shutil.rmtree("./comprehensive_research")
        except Exception:
            pass


if __name__ == "__main__":
    main()
