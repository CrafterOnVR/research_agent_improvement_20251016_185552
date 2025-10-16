#!/usr/bin/env python3
"""
Enhanced Web Capabilities Usage Example

This example demonstrates the advanced web functions now available
in the neural network's enhanced Fetcher class.
"""

import time
import json
from fetch import Fetcher


def demonstrate_proxy_and_user_agent_rotation():
    """Demonstrate proxy support and user agent rotation"""
    print("🔄 Testing Proxy and User Agent Rotation...")

    # Initialize fetcher with advanced options
    fetcher = Fetcher(
        enable_proxy_rotation=True,
        enable_user_agent_rotation=True,
        enable_state_changing=True
    )

    # Add some example proxies (replace with real proxies)
    proxies = [
        "http://proxy1.example.com:8080",
        "https://proxy2.example.com:8080",
        "socks5://proxy3.example.com:1080"
    ]
    fetcher.add_proxies(proxies)

    # Enable rotation features
    fetcher.set_user_agent_rotation(True)
    fetcher.set_proxy_rotation(True)

    # Test with rotated settings
    test_url = "https://httpbin.org/user-agent"
    result = fetcher.make_advanced_api_request(test_url)

    if result and "json" in result:
        print(f"✅ User Agent Rotation Working: {result['json'].get('user-agent', 'Unknown')}")

    fetcher.close()


def demonstrate_websocket_capabilities():
    """Demonstrate WebSocket real-time communication"""
    print("🌐 Testing WebSocket Capabilities...")

    fetcher = Fetcher(enable_state_changing=True)

    messages_received = []

    def on_message(message):
        messages_received.append(message)
        print(f"📨 WebSocket Message: {message}")

    def on_error(error):
        print(f"❌ WebSocket Error: {error}")

    def on_close(close_status_code, close_msg):
        print(f"🔌 WebSocket Closed: {close_status_code} - {close_msg}")

    # Connect to a WebSocket echo service (example)
    ws_url = "wss://echo.websocket.org"  # Public echo service
    connection_id = fetcher.connect_websocket(
        ws_url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    if connection_id:
        print(f"✅ WebSocket Connected: {connection_id}")

        # Send a test message
        fetcher.send_websocket_message(connection_id, "Hello from Neural Network!")

        # Wait for response
        time.sleep(2)

        # Close connection
        fetcher.close_websocket(connection_id)
        print("✅ WebSocket Test Completed")
    else:
        print("❌ WebSocket Connection Failed")

    fetcher.close()


def demonstrate_advanced_api_interactions():
    """Demonstrate advanced API capabilities"""
    print("🔗 Testing Advanced API Interactions...")

    fetcher = Fetcher(enable_state_changing=True)

    # Test different HTTP methods
    base_url = "https://httpbin.org"

    # GET request with custom headers
    print("Testing GET with custom headers...")
    result = fetcher.make_advanced_api_request(
        f"{base_url}/get",
        headers={"X-Custom-Header": "NeuralNetwork-Test"}
    )
    if result and result.get("status_code") == 200:
        print("✅ GET Request Successful")

    # POST request with JSON data
    print("Testing POST with JSON data...")
    result = fetcher.make_advanced_api_request(
        f"{base_url}/post",
        method="POST",
        json_data={"message": "Hello from enhanced neural network", "timestamp": time.time()}
    )
    if result and result.get("status_code") == 200:
        print("✅ POST Request Successful")

    # PUT request
    print("Testing PUT request...")
    result = fetcher.make_advanced_api_request(
        f"{base_url}/put",
        method="PUT",
        data={"updated": True}
    )
    if result and result.get("status_code") == 200:
        print("✅ PUT Request Successful")

    # Test with authentication (example)
    print("Testing with basic auth...")
    result = fetcher.make_advanced_api_request(
        f"{base_url}/basic-auth/user/pass",
        auth=("user", "pass")
    )
    if result and result.get("status_code") == 200:
        print("✅ Basic Auth Successful")

    fetcher.close()


def demonstrate_advanced_scraping():
    """Demonstrate advanced scraping strategies"""
    print("🕷️ Testing Advanced Scraping Strategies...")

    fetcher = Fetcher(enable_state_changing=True, selenium_driver="chrome", headless=True)

    # Test URLs (using example sites)
    test_urls = [
        "https://httpbin.org/html",  # Simple HTML page
        "https://httpbin.org/json"   # JSON endpoint
    ]

    # Custom selectors for scraping
    custom_selectors = {
        "headings": "h1, h2, h3",
        "links": "a[href]",
        "paragraphs": "p"
    }

    # Test different scraping strategies
    strategies = ["conservative", "moderate", "aggressive"]

    for strategy in strategies:
        print(f"Testing {strategy} scraping strategy...")
        results = fetcher.scrape_with_strategy(
            test_urls[:1],  # Test with first URL only
            strategy=strategy,
            custom_selectors=custom_selectors
        )

        for url, data in results.items():
            if "error" not in data:
                print(f"✅ {strategy.title()} Scraping: Found {len(data.get('headings', []))} headings")
            else:
                print(f"❌ {strategy.title()} Scraping Failed: {data['error']}")

    fetcher.close()


def demonstrate_security_scanning():
    """Demonstrate web security scanning capabilities"""
    print("🔒 Testing Web Security Scanning...")

    fetcher = Fetcher()

    # Test security scan on a few sites
    test_sites = [
        "https://github.com",
        "https://httpbin.org"
    ]

    for site in test_sites:
        print(f"Scanning security of {site}...")
        scan_result = fetcher.perform_security_scan(site)

        if "error" not in scan_result:
            checks = scan_result.get("checks", {})
            https_ok = checks.get("https_enforced", False)
            security_headers = checks.get("security_headers", {})
            exposed_paths = checks.get("exposed_paths", [])

            print(f"  ✅ HTTPS: {'Yes' if https_ok else 'No'}")
            print(f"  ✅ Security Headers: {len([h for h in security_headers.values() if h])} present")
            print(f"  ⚠️  Exposed Paths: {len(exposed_paths)} found")

            if exposed_paths:
                print(f"     Paths: {', '.join(exposed_paths)}")
        else:
            print(f"  ❌ Scan failed: {scan_result['error']}")

    fetcher.close()


def demonstrate_cookie_management():
    """Demonstrate advanced cookie management"""
    print("🍪 Testing Cookie Management...")

    fetcher = Fetcher()

    # Set some initial cookies
    test_url = "https://httpbin.org/cookies/set"
    fetcher.manage_cookies(f"{test_url}/test_cookie/test_value")

    # Make a request that should set cookies
    result = fetcher.make_advanced_api_request(f"{test_url}/session_cookie/session_value")

    if result and result.get("status_code") == 200:
        # Check what cookies we have
        cookies = fetcher.manage_cookies("httpbin.org")
        print(f"✅ Cookies managed: {len(cookies)} cookies stored")

        # Test cookie retrieval
        set_result = fetcher.make_advanced_api_request("https://httpbin.org/cookies")
        if set_result and "json" in set_result:
            returned_cookies = set_result["json"].get("cookies", {})
            print(f"✅ Cookies returned: {len(returned_cookies)} cookies")

    fetcher.clear_cookies()  # Clean up
    fetcher.close()


def main():
    """Run all enhanced web capability demonstrations"""
    print("🚀 Neural Network Enhanced Web Capabilities Demo")
    print("=" * 50)

    try:
        # Run demonstrations
        demonstrate_proxy_and_user_agent_rotation()
        print()

        demonstrate_websocket_capabilities()
        print()

        demonstrate_advanced_api_interactions()
        print()

        demonstrate_advanced_scraping()
        print()

        demonstrate_security_scanning()
        print()

        demonstrate_cookie_management()
        print()

        print("🎉 All enhanced web capability tests completed!")

    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()