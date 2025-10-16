"""
Research Agent Web UI

A Streamlit-based web interface for the Super Enhanced Research Agent.
Provides an easy-to-use GUI for conducting research with all advanced capabilities.
"""

import streamlit as st
import os
import sys
import time
from datetime import datetime
import threading
import queue

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

try:
    from super_enhanced_agent import SuperEnhancedResearchAgent
except ImportError:
    # Fallback for direct execution
    import super_enhanced_agent
    SuperEnhancedResearchAgent = super_enhanced_agent.SuperEnhancedResearchAgent

# Page configuration
st.set_page_config(
    page_title="Super Enhanced Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5em;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1em;
    }
    .sub-header {
        font-size: 1.5em;
        color: #2ca02c;
        margin-bottom: 0.5em;
    }
    .status-box {
        padding: 1em;
        border-radius: 5px;
        margin: 0.5em 0;
    }
    .success { background-color: #d4edda; border: 1px solid #c3e6cb; }
    .info { background-color: #d1ecf1; border: 1px solid #bee5eb; }
    .warning { background-color: #fff3cd; border: 1px solid #ffeaa7; }
    .error { background-color: #f8d7da; border: 1px solid #f5c6cb; }
</style>
""", unsafe_allow_html=True)

def load_logo():
    """Load and display the logo"""
    logo_path = "Icon.jpg"
    if os.path.exists(logo_path):
        st.image(logo_path, width=100)
    else:
        st.markdown("🔬 **Research Agent**")

def initialize_agent():
    """Initialize the research agent"""
    try:
        agent = SuperEnhancedResearchAgent(
            data_dir="./data",
            use_llm=True,
            max_results=10,
            enable_super_intelligence=True
        )
        return agent
    except Exception as e:
        st.error(f"Failed to initialize agent: {e}")
        return None

def run_research_async(topic, config, result_queue):
    """Run research in a separate thread"""
    try:
        agent = initialize_agent()
        if agent:
            # First run the main research
            result = agent.super_intelligent_research(topic, config)

            # If site scraping is enabled and configured, run it
            if config.get("enable_site_scraping") and config.get("site_scraping"):
                scraping_config = config["site_scraping"]
                if scraping_config.get("url"):
                    print(f"Starting site scraping for: {scraping_config['url']}")

                    # Call the site scraping method
                    scraping_result = agent.scrape_specific_site(
                        site_url=scraping_config["url"],
                        max_depth=scraping_config.get("max_depth", 2),
                        delay_between_requests=scraping_config.get("delay_between_requests", 1.0),
                        content_filters=scraping_config.get("content_filters", []),
                        max_pages=scraping_config.get("max_pages", 50)
                    )

                    # Add scraping results to main result
                    result["site_scraping"] = scraping_result
                    print(f"Site scraping completed: {scraping_result.get('completion_status', 'unknown')}")

            result_queue.put(("success", result))
        else:
            result_queue.put(("error", "Failed to initialize agent"))
    except Exception as e:
        result_queue.put(("error", str(e)))

def display_results(results):
    """Display research results in organized sections"""
    if not results:
        return

    # Overview
    st.markdown("### 📊 Research Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Intelligence Score", f"{results.get('intelligence_score', 0):.1f}")
    with col2:
        st.metric("Research Phases", len(results.get('research_phases', {})))
    with col3:
        st.metric("Success", "✅" if results.get('success') else "❌")

    # Phase details
    if 'research_phases' in results:
        phases = results['research_phases']

        tabs = st.tabs(["Topic Analysis", "Questions", "Patterns", "Automation", "Insights", "Report", "Site Scraping"])

        # Topic Analysis
        with tabs[0]:
            if 'topic_analysis' in phases:
                analysis = phases['topic_analysis']
                if isinstance(analysis, dict) and 'error' not in analysis:
                    st.markdown("**Keywords:**", ", ".join(analysis.get('keywords', [])[:10]))
                    st.markdown("**Entities:**", ", ".join(analysis.get('entities', [])[:5]))
                    st.markdown("**Concepts:**", ", ".join(analysis.get('concepts', [])[:5]))
                else:
                    st.error("Topic analysis failed")

        # Intelligent Questions
        with tabs[1]:
            if 'intelligent_questions' in phases:
                questions = phases['intelligent_questions']
                if isinstance(questions, list):
                    for i, q in enumerate(questions[:10], 1):
                        st.markdown(f"{i}. {q}")
                else:
                    st.error("Question generation failed")

        # Pattern Research
        with tabs[2]:
            if 'pattern_research' in phases:
                pattern_data = phases['pattern_research']
                if isinstance(pattern_data, dict) and 'error' not in pattern_data:
                    st.markdown(f"**Central Concepts:** {len(pattern_data.get('central_concepts', []))}")
                    st.markdown(f"**Concept Clusters:** {len(pattern_data.get('concept_clusters', []))}")
                    st.markdown(f"**Knowledge Graph:** {pattern_data.get('knowledge_graph_stats', {}).get('nodes', 0)} nodes")
                else:
                    st.error("Pattern research failed")

        # Automation Results
        with tabs[3]:
            if 'automation_results' in phases:
                auto_data = phases['automation_results']
                if isinstance(auto_data, dict) and 'error' not in auto_data:
                    metrics = auto_data.get('automation_metrics', {})
                    st.markdown(f"**Tasks Executed:** {len(auto_data.get('task_results', {}))}")
                    st.markdown(f"**Success Rate:** {metrics.get('success_rate', 0):.1%}")
                else:
                    st.error("Automation failed")

        # Advanced Insights
        with tabs[4]:
            if 'advanced_insights' in phases:
                insights = phases['advanced_insights']
                if isinstance(insights, dict) and 'error' not in insights:
                    st.markdown(f"**Semantic Insights:** {len(insights.get('semantic_insights', []))}")
                    st.markdown(f"**Pattern Insights:** {len(insights.get('pattern_insights', []))}")
                    st.markdown(f"**Recommendations:** {len(insights.get('recommendations', []))}")

                    if 'recommendations' in insights:
                        st.markdown("**Top Recommendations:**")
                        for rec in insights['recommendations'][:5]:
                            st.markdown(f"• {rec}")
                else:
                    st.error("Insights generation failed")

        # Comprehensive Report
        with tabs[5]:
            if 'comprehensive_report' in phases:
                report = phases['comprehensive_report']
                if isinstance(report, str):
                    st.markdown(report)
                else:
                    st.error("Report generation failed")

        # Site Scraping Results
        with tabs[6]:
            if 'site_scraping' in results:
                scraping = results['site_scraping']
                if scraping.get('completion_status') == 'completed':
                    st.success("✅ Site scraping completed successfully!")

                    # Scraping statistics
                    stats = scraping.get('scraping_stats', {})
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Pages Scraped", stats.get('pages_scraped', 0))
                    with col2:
                        st.metric("Pages Failed", stats.get('pages_failed', 0))
                    with col3:
                        st.metric("Links Found", stats.get('total_links_found', 0))
                    with col4:
                        st.metric("Duration", f"{stats.get('elapsed_time_seconds', 0):.1f}s")

                    # Summary
                    if 'summary' in scraping:
                        summary = scraping['summary']
                        st.markdown("### 📊 Scraping Summary")
                        st.markdown(f"**Total Content Size:** {summary.get('total_content_size_mb', 0):.2f} MB")
                        st.markdown(f"**Average Page Size:** {summary.get('average_page_size', 0):.0f} bytes")
                        st.markdown(f"**Pages/Minute:** {summary.get('pages_per_minute', 0):.1f}")

                        if 'content_stats' in summary:
                            content_stats = summary['content_stats']
                            st.markdown(f"**Average Content Length:** {content_stats.get('average_content_length', 0):.0f} chars")
                            st.markdown(f"**Total Words:** {content_stats.get('total_words', 0):,}")

                    # Scraped content preview
                    if scraping.get('scraped_content'):
                        st.markdown("### 📄 Scraped Content Preview")
                        content_list = scraping['scraped_content'][:5]  # Show first 5 pages

                        for i, content in enumerate(content_list, 1):
                            with st.expander(f"📄 {content.get('title', f'Page {i}')}"):
                                st.markdown(f"**URL:** {content.get('url', 'N/A')}")
                                st.markdown(f"**Word Count:** {content.get('word_count', 0)}")
                                if content.get('meta_description'):
                                    st.markdown(f"**Description:** {content.get('meta_description')[:200]}...")

                                # Show headings if available
                                if content.get('headings'):
                                    st.markdown("**Headings:**")
                                    for heading in content['headings'][:3]:  # Show first 3 headings
                                        st.markdown(f"- {heading['text']}")

                elif scraping.get('completion_status') == 'timeout_warning':
                    st.warning("⚠️ Site scraping exceeded time limits but completed")
                    st.info("Some content may have been missed due to time constraints")
                elif scraping.get('completion_status') == 'blocked_by_robots':
                    st.error("🚫 Site scraping blocked by robots.txt")
                else:
                    st.error(f"❌ Site scraping failed: {scraping.get('completion_status', 'unknown')}")

                # Show any errors
                if scraping.get('errors'):
                    st.markdown("### ⚠️ Scraping Errors")
                    for error in scraping['errors'][:5]:  # Show first 5 errors
                        st.warning(error)

            else:
                st.info("No site scraping was performed in this research session")

    # Self-improvement status
    if 'self_improvement' in results:
        st.markdown("### 🔄 Self-Improvement")
        improvement = results['self_improvement']
        if improvement.get('improvement_detected'):
            st.success("Self-improvement cycle completed!")
            if improvement.get('errors'):
                st.warning(f"Some issues occurred: {', '.join(improvement['errors'])}")
        else:
            st.info("No improvements detected this cycle")

def main():
    # Header with logo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        load_logo()
        st.markdown('<div class="main-header">Super Enhanced Research Agent</div>', unsafe_allow_html=True)
        st.markdown("*Maximum Intelligence Without API Keys*")

    # Sidebar configuration
    st.sidebar.markdown("## ⚙️ Configuration")

    # Research settings
    enable_web = st.sidebar.checkbox("Enable Web Research", value=True)
    enable_github = st.sidebar.checkbox("Enable GitHub Research", value=True)
    enable_files = st.sidebar.checkbox("Enable File Analysis", value=True)
    enable_automation = st.sidebar.checkbox("Enable Automation", value=True)
    enable_site_scraping = st.sidebar.checkbox("Enable Site Scraping", value=False)

    # Advanced options
    with st.sidebar.expander("Advanced Settings"):
        max_results = st.slider("Max Search Results", 5, 20, 10)
        research_depth = st.selectbox("Research Depth", ["standard", "deep", "comprehensive"], index=1)

        # Site scraping settings (only show if enabled)
        if enable_site_scraping:
            st.markdown("### 🕷️ Site Scraping Settings")
            scrape_url = st.text_input(
                "Site URL to Scrape:",
                placeholder="https://docs.python.org/3",
                help="Enter the base URL of the site you want to scrape"
            )
            scrape_max_depth = st.slider("Scraping Depth", 1, 5, 2,
                                       help="How many link levels deep to follow")
            scrape_delay = st.slider("Request Delay (seconds)", 0.5, 5.0, 1.0, 0.5,
                                   help="Delay between requests to be respectful")
            scrape_max_pages = st.slider("Max Pages to Scrape", 10, 100, 50,
                                       help="Maximum number of pages to scrape")
            scrape_filters = st.text_input(
                "Content Filters (comma-separated):",
                placeholder="tutorial,function,class,api",
                help="Keywords to filter content by (optional)"
            )

    # Main content
    st.markdown("---")

    # Topic input
    st.markdown('<div class="sub-header">🎯 Research Topic</div>', unsafe_allow_html=True)
    topic = st.text_input(
        "Enter your research topic:",
        placeholder="e.g., artificial intelligence, machine learning, quantum computing",
        help="The agent will conduct comprehensive research on this topic using all available capabilities"
    )

    # Research configuration
    config = {
        "enable_web_research": enable_web,
        "enable_github_research": enable_github,
        "enable_file_analysis": enable_files,
        "enable_workflow_execution": enable_automation,
        "max_results": max_results,
        "research_depth": research_depth,
        "enable_site_scraping": enable_site_scraping
    }

    # Add site scraping configuration if enabled
    if enable_site_scraping:
        config.update({
            "site_scraping": {
                "url": scrape_url.strip() if 'scrape_url' in locals() and scrape_url.strip() else "",
                "max_depth": scrape_max_depth if 'scrape_max_depth' in locals() else 2,
                "delay_between_requests": scrape_delay if 'scrape_delay' in locals() else 1.0,
                "max_pages": scrape_max_pages if 'scrape_max_pages' in locals() else 50,
                "content_filters": [f.strip() for f in scrape_filters.split(',') if f.strip()] if 'scrape_filters' in locals() and scrape_filters.strip() else []
            }
        })

    # Research button
    if st.button("🚀 Start Super Intelligent Research", type="primary", use_container_width=True):
        if not topic.strip():
            st.error("Please enter a research topic")
            return

        # Validate site scraping configuration
        if enable_site_scraping:
            if 'scrape_url' not in locals() or not scrape_url.strip():
                st.error("Please enter a site URL to scrape")
                return
            if not scrape_url.startswith(('http://', 'https://')):
                st.error("Site URL must start with http:// or https://")
                return

        # Initialize progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        results_container = st.empty()

        status_text.markdown('<div class="status-box info">🔄 Initializing research agent...</div>', unsafe_allow_html=True)

        # Run research in background thread
        result_queue = queue.Queue()
        research_thread = threading.Thread(
            target=run_research_async,
            args=(topic.strip(), config, result_queue)
        )
        research_thread.start()

        # Progress simulation (since we can't get real progress from the agent)
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

        for i, phase in enumerate(phases):
            progress = (i + 1) / len(phases)
            progress_bar.progress(progress)
            status_text.markdown(f'<div class="status-box info">🔄 {phase}...</div>', unsafe_allow_html=True)
            time.sleep(2)  # Simulate progress

        # Wait for actual results
        research_thread.join(timeout=300)  # 5 minute timeout

        if research_thread.is_alive():
            status_text.markdown('<div class="status-box warning">⏱️ Research is taking longer than expected. Please wait...</div>', unsafe_allow_html=True)
            research_thread.join(timeout=300)  # Additional wait

        # Get results
        if not result_queue.empty():
            status, result = result_queue.get()

            if status == "success":
                progress_bar.progress(1.0)
                status_text.markdown('<div class="status-box success">✅ Research completed successfully!</div>', unsafe_allow_html=True)

                # Display results
                with results_container.container():
                    display_results(result)

            else:
                status_text.markdown(f'<div class="status-box error">❌ Research failed: {result}</div>', unsafe_allow_html=True)
        else:
            status_text.markdown('<div class="status-box error">❌ Research timed out or failed to complete</div>', unsafe_allow_html=True)

    # Site Scraping Section (Independent of Research)
    st.markdown("---")
    st.markdown('<div class="sub-header">🕷️ Independent Site Scraping</div>', unsafe_allow_html=True)
    st.markdown("*Scrape any website without requiring a research topic*")

    # Site scraping controls
    col1, col2 = st.columns([3, 1])
    with col1:
        scrape_url = st.text_input(
            "Website URL to scrape:",
            placeholder="https://docs.python.org/3",
            help="Enter any website URL you want to scrape"
        )
    with col2:
        scrape_now = st.button("🕷️ Scrape Site Now", use_container_width=True)

    # Scraping configuration (shown when URL is entered)
    if scrape_url.strip():
        with st.expander("Scraping Configuration"):
            col1, col2, col3 = st.columns(3)
            with col1:
                scrape_depth = st.slider("Max Depth", 1, 5, 2, help="How many link levels deep to follow")
            with col2:
                scrape_delay = st.slider("Request Delay", 0.5, 5.0, 1.0, 0.5, help="Seconds between requests")
            with col3:
                scrape_max_pages = st.slider("Max Pages", 10, 100, 50, help="Maximum pages to scrape")

            scrape_filters = st.text_input(
                "Content Filters (optional):",
                placeholder="tutorial,function,class,api",
                help="Comma-separated keywords to prioritize. Example: tutorial,function,class,api"
            )

            if st.button("🚀 Start Independent Scraping", type="secondary"):
                if not scrape_url.startswith(('http://', 'https://')):
                    st.error("URL must start with http:// or https://")
                else:
                    # Perform independent site scraping
                    with st.spinner("Scraping site..."):
                        agent = initialize_agent()
                        if agent:
                            scraping_config = {
                                "url": scrape_url.strip(),
                                "max_depth": scrape_depth,
                                "delay_between_requests": scrape_delay,
                                "max_pages": scrape_max_pages,
                                "content_filters": [f.strip() for f in scrape_filters.split(',') if f.strip()]
                            }

                            results = agent.scrape_specific_site(**scraping_config)

                            # Display results
                            if results.get('completion_status') == 'completed':
                                st.success("✅ Site scraping completed successfully!")

                                # Statistics
                                stats = results.get('scraping_stats', {})
                                summary = results.get('summary', {})

                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Pages Scraped", stats.get('pages_scraped', 0))
                                with col2:
                                    st.metric("Content Size", f"{summary.get('total_content_size_mb', 0):.2f} MB")
                                with col3:
                                    st.metric("Duration", f"{stats.get('elapsed_time_seconds', 0):.1f}s")
                                with col4:
                                    st.metric("Success Rate", f"{summary.get('success_rate', 0):.1f}%")

                                # Content preview
                                if results.get('scraped_content'):
                                    st.markdown("### 📄 Scraped Content Preview")
                                    content_df = []
                                    for content in results['scraped_content'][:10]:  # Show first 10
                                        content_df.append({
                                            "Title": content.get('title', 'No title')[:50],
                                            "URL": content.get('url', 'N/A'),
                                            "Words": content.get('word_count', 0),
                                            "Relevance": f"{content.get('content_relevance', 0):.2f}"
                                        })

                                    if content_df:
                                        import pandas as pd
                                        st.dataframe(pd.DataFrame(content_df))

                            else:
                                st.error(f"❌ Scraping failed: {results.get('completion_status', 'unknown')}")

                            # Show errors if any
                            if results.get('errors'):
                                st.warning("Some errors occurred during scraping:")
                                for error in results['errors'][:5]:
                                    st.write(f"• {error}")

    # Footer
    st.markdown("---")
    st.markdown("*Powered by Super Enhanced Research Agent - Maximum Intelligence Without API Keys*")

if __name__ == "__main__":
    main()