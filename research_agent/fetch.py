import asyncio
import re
import time
import urllib.parse
from typing import Optional, Dict, Any, List, Union, Callable, Tuple
import json
import logging
import random
import threading
import socket
from datetime import datetime
from http.cookies import SimpleCookie
import urllib3

import httpx
try:
    # Try relative imports first (for package execution)
    from .text import html_to_text
except ImportError:
    # Fallback to absolute imports (for direct execution)
    from text import html_to_text

# Optional imports for enhanced capabilities
try:
    from selenium import webdriver  # type: ignore
    from selenium.webdriver.common.by import By  # type: ignore
    from selenium.webdriver.support.ui import WebDriverWait  # type: ignore
    from selenium.webdriver.support import expected_conditions as EC  # type: ignore
    from selenium.webdriver.chrome.options import Options as ChromeOptions  # type: ignore
    from selenium.webdriver.firefox.options import Options as FirefoxOptions  # type: ignore
    from selenium.common.exceptions import TimeoutException, WebDriverException  # type: ignore
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# Optional imports for proxy support
try:
    import socks
    PROXY_AVAILABLE = True
except ImportError:
    PROXY_AVAILABLE = False

# Optional imports for WebSocket support
try:
    from websocket import WebSocketApp
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False


DEFAULT_UA = "ResearchAgent/0.1 (+https://example.org/agent; contact: none)"

# Advanced user agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1"
]


class Fetcher:
    def __init__(self, user_agent: str = DEFAULT_UA, timeout: int = 20, enable_state_changing: bool = False,
                 selenium_driver: str = "chrome", headless: bool = True, enable_proxy_rotation: bool = False,
                 enable_user_agent_rotation: bool = False, proxy_list: Optional[List[str]] = None):
        self.ua = user_agent
        self.timeout = timeout
        self.enable_state_changing = enable_state_changing
        self.selenium_driver = selenium_driver
        self.headless = headless
        self.enable_proxy_rotation = enable_proxy_rotation
        self.enable_user_agent_rotation = enable_user_agent_rotation
        self.proxy_list = proxy_list or []
        self.current_proxy_index = 0
        self.original_socket = socket.socket  # Save original socket for proxy reset

        # Initialize async client with retry strategy
        self.client = httpx.AsyncClient(
            headers={"User-Agent": self.ua, "Accept": "text/html,application/xhtml+xml"},
            timeout=self.timeout,
            transport=httpx.AsyncHTTPTransport(retries=3)
        )
        self.webdriver = None
        self.rate_limit_delay = 1.0  # Minimum delay between requests
        self.last_request_time = 0

        # Cookie management
        self.cookie_jar = {}

        # WebSocket connections
        self.websocket_connections = {}

        # Safety controls
        self.max_requests_per_minute = 30
        self.request_count = 0
        self.request_window_start = time.time()
        self.blocked_domains = set()  # Domains to avoid
        self.allowed_domains = set()  # If set, only these domains are allowed

        # Advanced scraping settings
        self.scraping_strategies = {
            "aggressive": {"delay": 0.5, "max_concurrent": 5},
            "moderate": {"delay": 1.0, "max_concurrent": 3},
            "conservative": {"delay": 2.0, "max_concurrent": 1}
        }
        self.current_strategy = "moderate"

    async def _check_rate_limit(self):
        """Enforce rate limiting for ethical web scraping"""
        current_time = time.time()
        
        # Reset counter every minute
        if current_time - self.request_window_start > 60:
            self.request_count = 0
            self.request_window_start = current_time
        
        # Check if we've exceeded rate limit
        if self.request_count >= self.max_requests_per_minute:
            sleep_time = 60 - (current_time - self.request_window_start)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
                self.request_count = 0
                self.request_window_start = time.time()
        
        # Enforce minimum delay between requests
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        
        self.request_count += 1
        self.last_request_time = time.time()

    def _check_domain_safety(self, url: str) -> bool:
        """Check if domain is safe to interact with"""
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.lower()

            # Check blocked domains
            if self.blocked_domains and any(blocked in domain for blocked in self.blocked_domains):
                return False

            # Check allowed domains (if restriction is enabled)
            if self.allowed_domains and not any(allowed in domain for allowed in self.allowed_domains):
                return False

            return True
        except Exception:
            return False

    def _get_rotated_user_agent(self) -> str:
        """Get a rotated user agent for requests"""
        if self.enable_user_agent_rotation:
            return random.choice(USER_AGENTS)
        return self.ua

    def _get_next_proxy(self) -> Optional[str]:
        """Get the next proxy from the rotation list"""
        if not self.enable_proxy_rotation or not self.proxy_list:
            return None

        proxy = self.proxy_list[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_list)
        return proxy



    def set_user_agent_rotation(self, enabled: bool = True):
        """Enable or disable user agent rotation"""
        self.enable_user_agent_rotation = enabled

    def set_proxy_rotation(self, enabled: bool = True, proxy_list: Optional[List[str]] = None):
        """Enable proxy rotation with optional proxy list"""
        self.enable_proxy_rotation = enabled
        if proxy_list:
            self.proxy_list = proxy_list
        self.current_proxy_index = 0

    def add_proxies(self, proxies: List[str]):
        """Add proxies to the rotation list"""
        self.proxy_list.extend(proxies)

    def manage_cookies(self, url: str, cookies: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Manage cookies for a domain"""
        domain = urllib.parse.urlparse(url).netloc
        if cookies:
            self.cookie_jar[domain] = cookies
        return self.cookie_jar.get(domain, {})

    def clear_cookies(self, domain: Optional[str] = None):
        """Clear cookies for a domain or all domains"""
        if domain:
            self.cookie_jar.pop(domain, None)
        else:
            self.cookie_jar.clear()

    def _get_webdriver(self):
        """Initialize and return a WebDriver instance"""
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is not available. Install with: pip install selenium")
        
        if self.webdriver is None:
            try:
                if self.selenium_driver.lower() == "chrome":
                    options = ChromeOptions()
                    if self.headless:
                        options.add_argument("--headless")
                    options.add_argument("--no-sandbox")
                    options.add_argument("--disable-dev-shm-usage")
                    options.add_argument(f"--user-agent={self.ua}")
                    self.webdriver = webdriver.Chrome(options=options)
                elif self.selenium_driver.lower() == "firefox":
                    options = FirefoxOptions()
                    if self.headless:
                        options.add_argument("--headless")
                    options.add_argument(f"--user-agent={self.ua}")
                    self.webdriver = webdriver.Firefox(options=options)
                else:
                    raise ValueError(f"Unsupported driver: {self.selenium_driver}")
                
                self.webdriver.set_page_load_timeout(self.timeout)
            except Exception as e:
                logging.error(f"Failed to initialize WebDriver: {e}")
                raise
        
        return self.webdriver

    async def fetch_text(self, url: str, use_proxy: bool = True, custom_headers: Optional[Dict[str, str]] = None) -> Optional[str]:
        """Fetch text content from URL with advanced options"""
        if not self._check_domain_safety(url):
            return None

        await self._check_rate_limit()

        try:
            # Setup request parameters
            headers = {"User-Agent": self._get_rotated_user_agent(), "Accept": "text/html,application/xhtml+xml"}
            if custom_headers:
                headers.update(custom_headers)

            # Add cookies if available
            domain = urllib.parse.urlparse(url).netloc
            cookies = self.manage_cookies(url)
            if cookies:
                headers.update({"Cookie": "; ".join([f"{k}={v}" for k, v in cookies.items()])})

            proxies = self._get_next_proxy() if use_proxy else None

            async with httpx.AsyncClient(proxies=proxies) as client:
                resp = await client.get(url, timeout=self.timeout, follow_redirects=True, headers=headers)

            # Store cookies from response
            if resp.cookies:
                cookie_dict = {cookie.name: cookie.value for cookie in resp.cookies}
                self.manage_cookies(url, cookie_dict)

            # Only process HTML-like content
            ctype = resp.headers.get("Content-Type", "").lower()
            if resp.status_code != 200 or ("html" not in ctype and "xml" not in ctype and "text/" not in ctype):
                return None
            text = html_to_text(resp.text)
            text = self._clean(text)
            if len(text.strip()) < 200:
                return None
            return text
        except Exception as e:
            logging.error(f"Text fetch failed for {url}: {e}")
            return None

    async def fetch_with_selenium(self, url: str, wait_for_element: Optional[str] = None, 
                           wait_timeout: int = 10) -> Optional[str]:
        """Fetch content using Selenium for JavaScript-heavy sites"""
        if not self.enable_state_changing:
            return await self.fetch_text(url)
        
        if not self._check_domain_safety(url):
            return None
            
        await self._check_rate_limit()
        
        try:
            driver = self._get_webdriver()
            await asyncio.to_thread(driver.get, url)
            
            # Wait for specific element if specified
            if wait_for_element:
                try:
                    await asyncio.to_thread(WebDriverWait(driver, wait_timeout).until, 
                        EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_element))
                    )
                except TimeoutException:
                    pass  # Continue even if element not found
            
            # Get page source and extract text
            html = driver.page_source
            text = html_to_text(html)
            text = self._clean(text)
            
            if len(text.strip()) < 200:
                return None
            return text
            
        except Exception as e:
            logging.error(f"Selenium fetch failed for {url}: {e}")
            return None

    async def submit_form(self, url: str, form_data: Dict[str, Any], 
                   form_selector: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Submit a form and return the result"""
        if not self.enable_state_changing:
            raise ValueError("State-changing actions are disabled")
        
        if not self._check_domain_safety(url):
            return None
            
        await self._check_rate_limit()
        
        try:
            driver = self._get_webdriver()
            await asyncio.to_thread(driver.get, url)
            
            # Find form if selector provided
            if form_selector:
                form = await asyncio.to_thread(driver.find_element, By.CSS_SELECTOR, form_selector)
            else:
                form = await asyncio.to_thread(driver.find_element, By.TAG_NAME, "form")
            
            # Fill form fields
            for field_name, value in form_data.items():
                try:
                    field = await asyncio.to_thread(form.find_element, By.NAME, field_name)
                    await asyncio.to_thread(field.clear)
                    await asyncio.to_thread(field.send_keys, str(value))
                except Exception:
                    # Try by ID if name doesn't work
                    try:
                        field = await asyncio.to_thread(form.find_element, By.ID, field_name)
                        await asyncio.to_thread(field.clear)
                        await asyncio.to_thread(field.send_keys, str(value))
                    except Exception:
                        logging.warning(f"Could not find form field: {field_name}")
            
            # Submit form
            await asyncio.to_thread(form.submit)
            
            # Wait for response
            await asyncio.sleep(2)
            
            # Return result
            result = {
                "url": driver.current_url,
                "title": driver.title,
                "text": self._clean(html_to_text(driver.page_source)),
                "status": "success"
            }
            
            return result
            
        except Exception as e:
            logging.error(f"Form submission failed for {url}: {e}")
            return {"status": "error", "message": str(e)}

    async def make_api_request(self, url: str, method: str = "GET", data: Optional[Dict] = None, 
                        headers: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Make API requests with various HTTP methods"""
        if not self.enable_state_changing and method != "GET":
            raise ValueError("State-changing actions are disabled")
        
        if not self._check_domain_safety(url):
            return None
            
        await self._check_rate_limit()
        
        try:
            request_headers = {"User-Agent": self.ua}
            if headers:
                request_headers.update(headers)
            
            async with httpx.AsyncClient() as client:
                if method.upper() == "GET":
                    resp = await client.get(url, headers=request_headers, timeout=self.timeout)
                elif method.upper() == "POST":
                    resp = await client.post(url, json=data, headers=request_headers, timeout=self.timeout)
                elif method.upper() == "PUT":
                    resp = await client.put(url, json=data, headers=request_headers, timeout=self.timeout)
                elif method.upper() == "DELETE":
                    resp = await client.delete(url, headers=request_headers, timeout=self.timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
            
            result = {
                "status_code": resp.status_code,
                "headers": dict(resp.headers),
                "url": str(resp.url)
            }
            
            # Try to parse JSON response
            try:
                result["json"] = resp.json()
            except:
                result["text"] = resp.text
            
            return result
            
        except Exception as e:
            logging.error(f"API request failed for {url}: {e}")
            return {"status": "error", "message": str(e)}

    def connect_websocket(self, url: str, on_message: Optional[Callable] = None,
                         on_error: Optional[Callable] = None, on_close: Optional[Callable] = None) -> str:
        """Establish a WebSocket connection for real-time communication"""
        if not WEBSOCKET_AVAILABLE:
            logging.warning("WebSocket support not available. Install 'websocket-client' package.")
            return ""

        connection_id = f"ws_{int(time.time())}_{len(self.websocket_connections)}"

        def on_message_wrapper(ws, message):
            if on_message:
                on_message(message)
            else:
                logging.info(f"WebSocket message: {message}")

        def on_error_wrapper(ws, error):
            logging.error(f"WebSocket error: {error}")
            if on_error:
                on_error(error)

        def on_close_wrapper(ws, close_status_code, close_msg):
            logging.info(f"WebSocket closed: {close_status_code} - {close_msg}")
            if on_close:
                on_close(close_status_code, close_msg)
            # Remove from connections
            self.websocket_connections.pop(connection_id, None)

        try:
            ws = WebSocketApp(
                url,
                on_message=on_message_wrapper,
                on_error=on_error_wrapper,
                on_close=on_close_wrapper
            )

            # Start WebSocket in a separate thread
            ws_thread = threading.Thread(target=ws.run_forever, daemon=True)
            ws_thread.start()

            self.websocket_connections[connection_id] = {
                'websocket': ws,
                'thread': ws_thread,
                'url': url
            }

            return connection_id

        except Exception as e:
            logging.error(f"Failed to connect WebSocket to {url}: {e}")
            return ""

    def send_websocket_message(self, connection_id: str, message: str) -> bool:
        """Send a message through WebSocket connection"""
        if connection_id not in self.websocket_connections:
            return False

        try:
            ws = self.websocket_connections[connection_id]['websocket']
            ws.send(message)
            return True
        except Exception as e:
            logging.error(f"Failed to send WebSocket message: {e}")
            return False

    def close_websocket(self, connection_id: str) -> bool:
        """Close a WebSocket connection"""
        if connection_id not in self.websocket_connections:
            return False

        try:
            ws = self.websocket_connections[connection_id]['websocket']
            ws.close()
            del self.websocket_connections[connection_id]
            return True
        except Exception as e:
            logging.error(f"Failed to close WebSocket: {e}")
            return False

    async def make_advanced_api_request(self, url: str, method: str = "GET",
                                data: Optional[Any] = None,
                                headers: Optional[Dict[str, str]] = None,
                                auth: Optional[Tuple[str, str]] = None,
                                files: Optional[Dict[str, Any]] = None,
                                params: Optional[Dict[str, str]] = None,
                                json_data: Optional[Dict] = None,
                                timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Make advanced API requests with full HTTP capabilities"""
        if not self.enable_state_changing and method.upper() not in ["GET", "HEAD", "OPTIONS"]:
            raise ValueError("State-changing actions are disabled")

        if not self._check_domain_safety(url):
            return None

        await self._check_rate_limit()

        try:
            # Setup request parameters
            request_headers = {"User-Agent": self._get_rotated_user_agent()}
            if headers:
                request_headers.update(headers)

            # Add cookies if available
            domain = urllib.parse.urlparse(url).netloc
            cookies = self.manage_cookies(url)
            if cookies:
                request_headers.update({"Cookie": "; ".join([f"{k}={v}" for k, v in cookies.items()])})

            proxies = self._get_next_proxy()
            request_timeout = timeout or self.timeout

            async with httpx.AsyncClient(proxies=proxies) as client:
                # Prepare request data
                request_kwargs = {
                    'method': method.upper(),
                    'url': url,
                    'headers': request_headers,
                    'timeout': request_timeout,
                    'follow_redirects': True
                }

                if auth:
                    request_kwargs['auth'] = auth
                if params:
                    request_kwargs['params'] = params
                if files:
                    request_kwargs['files'] = files

                # Handle different data types
                if json_data is not None:
                    request_kwargs['json'] = json_data
                    request_headers['Content-Type'] = 'application/json'
                elif data is not None:
                    if isinstance(data, dict):
                        request_kwargs['data'] = data
                    else:
                        request_kwargs['data'] = str(data)

                resp = await client.request(**request_kwargs)

            # Store cookies from response
            if resp.cookies:
                cookie_dict = {cookie.name: cookie.value for cookie in resp.cookies}
                self.manage_cookies(url, cookie_dict)

            result = {
                "status_code": resp.status_code,
                "headers": dict(resp.headers),
                "url": str(resp.url),
                "elapsed": resp.elapsed.total_seconds(),
                "encoding": resp.encoding
            }

            # Try to parse response content
            try:
                result["json"] = resp.json()
            except:
                try:
                    result["text"] = resp.text
                except:
                    result["content"] = resp.content

            return result

        except Exception as e:
            logging.error(f"Advanced API request failed for {url}: {e}")
            return {"status": "error", "message": str(e)}

    async def scrape_with_strategy(self, urls: List[str], strategy: str = "moderate",
                           custom_selectors: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Scrape multiple URLs using different strategies"""
        if strategy not in self.scraping_strategies:
            strategy = "moderate"

        strategy_config = self.scraping_strategies[strategy]
        results = {}

        for url in urls:
            if not self._check_domain_safety(url):
                results[url] = {"error": "Domain not allowed"}
                continue

            await self._check_rate_limit()

            try:
                # Use Selenium for advanced scraping
                driver = self._get_webdriver()
                await asyncio.to_thread(driver.get, url)

                # Wait for dynamic content
                await asyncio.sleep(strategy_config["delay"])

                scraped_data = {}

                # Extract common elements
                try:
                    scraped_data["title"] = driver.title
                except:
                    scraped_data["title"] = ""

                try:
                    scraped_data["url"] = driver.current_url
                except:
                    scraped_data["url"] = url

                # Extract text content
                text = html_to_text(driver.page_source)
                scraped_data["text"] = self._clean(text)

                # Extract custom selectors if provided
                if custom_selectors:
                    for name, selector in custom_selectors.items():
                        try:
                            elements = await asyncio.to_thread(driver.find_elements, By.CSS_SELECTOR, selector)
                            scraped_data[name] = [elem.text for elem in elements if elem.text]
                        except:
                            scraped_data[name] = []

                # Extract metadata
                scraped_data["meta_tags"] = {}
                try:
                    meta_tags = await asyncio.to_thread(driver.find_elements, By.CSS_SELECTOR, "meta")
                    for tag in meta_tags:
                        name = tag.get_attribute("name") or tag.get_attribute("property")
                        content = tag.get_attribute("content")
                        if name and content:
                            scraped_data["meta_tags"][name] = content
                except:
                    pass

                results[url] = scraped_data

            except Exception as e:
                results[url] = {"error": str(e)}

        return results

    async def perform_security_scan(self, url: str) -> Dict[str, Any]:
        """Perform basic web security scanning"""
        scan_results = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }

        try:
            # Check HTTPS
            parsed = urllib.parse.urlparse(url)
            scan_results["checks"]["https_enforced"] = parsed.scheme == "https"

            # Check for common security headers
            async with httpx.AsyncClient() as client:
                resp = await client.head(url, timeout=self.timeout)
            headers = resp.headers

            security_headers = {
                "Strict-Transport-Security": headers.get("Strict-Transport-Security"),
                "X-Content-Type-Options": headers.get("X-Content-Type-Options"),
                "X-Frame-Options": headers.get("X-Frame-Options"),
                "Content-Security-Policy": headers.get("Content-Security-Policy"),
                "X-XSS-Protection": headers.get("X-XSS-Protection")
            }

            scan_results["checks"]["security_headers"] = security_headers

            # Check for exposed directories (basic check)
            common_paths = ["/admin", "/login", "/wp-admin", "/administrator"]
            exposed_paths = []

            for path in common_paths:
                test_url = urllib.parse.urljoin(url, path)
                try:
                    async with httpx.AsyncClient() as client:
                        test_resp = await client.get(test_url, timeout=5)
                    if test_resp.status_code == 200:
                        exposed_paths.append(path)
                except:
                    pass

            scan_results["checks"]["exposed_paths"] = exposed_paths

            # Check SSL certificate (basic)
            if parsed.scheme == "https":
                try:
                    import ssl
                    hostname = parsed.hostname
                    context = ssl.create_default_context()
                    async with await asyncio.open_connection(hostname, 443, ssl=context) as (reader, writer):
                        cert = writer.get_extra_info('peercert')
                        scan_results["checks"]["ssl_valid"] = True
                        scan_results["checks"]["ssl_expiry"] = cert.get('notAfter')
                except:
                    scan_results["checks"]["ssl_valid"] = False

        except Exception as e:
            scan_results["error"] = str(e)

        return scan_results

    async def close(self):
        """Clean up resources"""
        # Reset socket to original
        socket.socket = self.original_socket

        # Close WebSocket connections
        for conn_id, conn_info in self.websocket_connections.items():
            try:
                conn_info['websocket'].close()
            except:
                pass
        self.websocket_connections.clear()

        # Close WebDriver
        if self.webdriver:
            try:
                await asyncio.to_thread(self.webdriver.quit)
            except Exception:
                pass
            self.webdriver = None

        await self.client.aclose()

    @staticmethod
    def _clean(text: str) -> str:
        # collapse whitespace, remove very long runs
        text = re.sub(r"\s+", " ", text)
        return text.strip()
# Simple fetch_url function for backward compatibility
async def fetch_url(url: str, timeout: int = 20, headers: Optional[Dict[str, str]] = None) -> Optional[str]:
    """Simple function to fetch URL content - for backward compatibility"""
    fetcher = Fetcher(timeout=timeout)
    try:
        # Use the advanced API request method for HTML content
        result = await fetcher.make_advanced_api_request(url, headers=headers or {})
        if result and result.get("status_code") == 200:
            return result.get("text") or result.get("content", "").decode("utf-8", errors="ignore") if isinstance(result.get("content"), bytes) else ""
        return None
    except Exception as e:
        logging.error(f"fetch_url failed for {url}: {e}")
        return None
    finally:
        await fetcher.close()

