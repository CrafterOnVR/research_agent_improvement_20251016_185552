#!/usr/bin/env python3
"""
Example usage of the enhanced research agent with state-changing web capabilities.

This script demonstrates how to use the new features for interactive web research.
"""

import sys
import os

# Add the current directory to the path so we can import the research_agent module
sys.path.insert(0, os.path.dirname(__file__))

from agent import ResearchAgent

def example_basic_enhanced_research():
    """Example of basic enhanced research with state-changing capabilities"""
    print("=== Basic Enhanced Research Example ===")
    
    # Create agent with enhanced capabilities enabled
    agent = ResearchAgent(
        enable_state_changing=True,
        selenium_driver="chrome",
        headless=True
    )
    
    try:
        # Example: Fetch content from a JavaScript-heavy site
        url = "https://example.com"
        print(f"Fetching content from {url} with Selenium...")
        content = agent.fetch_with_selenium(url)
        if content:
            print(f"Successfully fetched {len(content)} characters of content")
        else:
            print("Failed to fetch content")
        
        # Example: Make an API request
        api_url = "https://httpbin.org/get"
        print(f"Making API request to {api_url}...")
        response = agent.make_api_request(api_url, method="GET")
        if response:
            print(f"API response status: {response.get('status_code', 'unknown')}")
        
    except Exception as e:
        print(f"Error during enhanced research: {e}")
    finally:
        agent.close()

def example_form_submission():
    """Example of form submission (requires a test form)"""
    print("\n=== Form Submission Example ===")
    
    agent = ResearchAgent(
        enable_state_changing=True,
        selenium_driver="chrome",
        headless=True
    )
    
    try:
        # Example form data (this would need to match actual form fields)
        form_data = {
            "name": "Research Agent",
            "email": "agent@example.com",
            "message": "This is an automated form submission for research purposes"
        }
        
        # Note: This is just an example - you'd need a real form URL
        form_url = "https://httpbin.org/forms/post"
        print(f"Submitting form to {form_url}...")
        
        result = agent.submit_form(form_url, form_data)
        if result and result.get("status") == "success":
            print("Form submitted successfully!")
            print(f"Result URL: {result.get('url', 'unknown')}")
        else:
            print("Form submission failed or not supported by this URL")
            
    except Exception as e:
        print(f"Error during form submission: {e}")
    finally:
        agent.close()

def example_interactive_research():
    """Example of interactive research on specific URLs"""
    print("\n=== Interactive Research Example ===")
    
    agent = ResearchAgent(
        enable_state_changing=True,
        selenium_driver="chrome",
        headless=True
    )
    
    try:
        # List of URLs that might require interactive research
        interactive_urls = [
            "https://httpbin.org/html",
            "https://httpbin.org/json",
            "https://example.com"
        ]
        
        topic = "Web APIs and Testing"
        print(f"Performing interactive research on topic: {topic}")
        agent.interactive_web_research(topic, interactive_urls)
        
    except Exception as e:
        print(f"Error during interactive research: {e}")
    finally:
        agent.close()

def example_safety_controls():
    """Example of using safety controls"""
    print("\n=== Safety Controls Example ===")
    
    agent = ResearchAgent(
        enable_state_changing=True,
        selenium_driver="chrome",
        headless=True
    )
    
    try:
        # The fetcher has built-in safety controls
        fetcher = agent.fetcher
        
        # Example: Set up domain restrictions
        fetcher.blocked_domains = {"malicious-site.com", "spam-site.com"}
        fetcher.allowed_domains = {"httpbin.org", "example.com"}  # Only allow these domains
        
        # Example: Adjust rate limiting
        fetcher.max_requests_per_minute = 10  # More conservative
        fetcher.rate_limit_delay = 2.0  # 2 seconds between requests
        
        print("Safety controls configured:")
        print(f"- Blocked domains: {fetcher.blocked_domains}")
        print(f"- Allowed domains: {fetcher.allowed_domains}")
        print(f"- Max requests per minute: {fetcher.max_requests_per_minute}")
        print(f"- Rate limit delay: {fetcher.rate_limit_delay} seconds")
        
    except Exception as e:
        print(f"Error configuring safety controls: {e}")
    finally:
        agent.close()

if __name__ == "__main__":
    print("Enhanced Research Agent Examples")
    print("=" * 40)
    
    # Run examples
    example_basic_enhanced_research()
    example_form_submission()
    example_interactive_research()
    example_safety_controls()
    
    print("\n" + "=" * 40)
    print("Examples completed!")
    print("\nTo use these features in the command line:")
    print("python -m research_agent --topic 'web automation' --enable-state-changing")
    print("python -m research_agent --topic 'forms' --enable-state-changing --interactive-urls 'https://example.com/form'")
