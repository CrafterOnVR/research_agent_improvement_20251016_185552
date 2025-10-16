from typing import Any, Dict, List, Optional
import logging
import time
from datetime import datetime

class WebScrapingManager:
    """Manages the web scraping process of the research agent."""

    def __init__(self, agent):
        self.agent = agent

    def scrape_specific_site(self, site_url: str, max_depth: int = 2, delay_between_requests: float = 1.0,
                           content_filters: Optional[List[str]] = None, max_pages: int = 50,
                           respect_robots: bool = True, timeout: int = 30) -> Dict[str, Any]:
        """Scrape a specific website with configurable parameters and time monitoring."""
        print(f"[ARINN-LOG] {datetime.now().isoformat()} - WEB-SCRAPING: Starting scrape of {site_url}")
        print(f"[ARINN-LOG] {datetime.now().isoformat()} - WEB-SCRAPING: Config - max_depth={max_depth}, max_pages={max_pages}, respect_robots={respect_robots}")

        # Top-level exception handling
        try:
            start_time = time.time()
            estimated_completion = start_time + (25 * 60)  # 25 minutes estimate

            results = {
                "site_url": site_url,
                "scraping_config": {
                    "max_depth": max_depth,
                    "delay_between_requests": delay_between_requests,
                    "content_filters": content_filters or [],
                    "max_pages": max_pages,
                    "respect_robots": respect_robots,
                    "timeout": timeout
                },
                "scraping_stats": {
                    "pages_scraped": 0,
                    "pages_failed": 0,
                    "total_links_found": 0,
                    "content_size_bytes": 0,
                    "start_time": datetime.now().isoformat(),
                    "elapsed_time_seconds": 0
                },
                "scraped_content": [],
                "errors": [],
                "completion_status": "in_progress"
            }

            # Check robots.txt if requested
            if respect_robots:
                print(f"[ARINN-LOG] {datetime.now().isoformat()} - WEB-SCRAPING: Checking robots.txt for {site_url}")
                robots_allowed = self._check_robots_txt(site_url)
                if not robots_allowed:
                    print(f"[ARINN-LOG] {datetime.now().isoformat()} - WEB-SCRAPING: BLOCKED by robots.txt - aborting scrape")
                    results["errors"].append("Scraping blocked by robots.txt")
                    results["completion_status"] = "blocked_by_robots"
                    return results
                print(f"[ARINN-LOG] {datetime.now().isoformat()} - WEB-SCRAPING: robots.txt check passed")

            # Initialize scraping queue and visited set
            from urllib.parse import urljoin, urlparse
            from collections import deque

            queue = deque([(site_url, 0)])  # (url, depth)
            visited = set()
            base_domain = urlparse(site_url).netloc

            while queue and results["scraping_stats"]["pages_scraped"] < max_pages:
                current_url, depth = queue.popleft()

                # Skip if already visited or exceeds max depth
                if current_url in visited or depth > max_depth:
                    continue

                visited.add(current_url)

                # Time monitoring - check if approaching time limit
                elapsed = time.time() - start_time
                if elapsed > (25 * 60):  # Over 25 minutes
                    results["errors"].append(f"Scraping exceeded 25-minute limit ({elapsed:.1f}s)")
                    results["completion_status"] = "timeout_warning"
                    break
                elif elapsed > (20 * 60):  # Over 20 minutes
                    print(f"⚠️  WARNING: Scraping has been running for {elapsed/60:.1f} minutes. "
                          f"Estimated completion in {((25*60)-elapsed)/60:.1f} minutes.")

                try:
                    # Fetch page content with enhanced method and fallback
                    page_content = self._fetch_page_content(current_url, timeout)

                    # If enhanced fetch fails, try fallback to Selenium
                    if not page_content:
                        logging.info(f"Enhanced fetch failed for {current_url}, trying Selenium fallback")
                        page_content = self._fetch_page_content_with_fallback(current_url, timeout)

                    if not page_content:
                        results["scraping_stats"]["pages_failed"] += 1
                        continue

                    # Process content
                    processed_content = self._process_scraped_content(
                        current_url, page_content, content_filters
                    )

                    # Store content in database
                    self._store_scraped_content(processed_content)

                    # Add to results
                    results["scraped_content"].append(processed_content)
                    results["scraping_stats"]["pages_scraped"] += 1
                    results["scraping_stats"]["content_size_bytes"] += len(page_content)

                    # Extract and queue internal links
                    if depth < max_depth:
                        internal_links = self._extract_internal_links(
                            page_content, current_url, base_domain
                        )
                        results["scraping_stats"]["total_links_found"] += len(internal_links)

                        for link in internal_links:
                            if link not in visited and link not in [url for url, _ in queue]:
                                queue.append((link, depth + 1))

                    # Respect delay between requests
                    if delay_between_requests > 0:
                        time.sleep(delay_between_requests)

                except Exception as e:
                    error_msg = f"Failed to scrape {current_url}: {str(e)}"
                    results["errors"].append(error_msg)
                    results["scraping_stats"]["pages_failed"] += 1
                    logging.warning(error_msg)

            # Finalize results
            end_time = time.time()
            results["scraping_stats"]["elapsed_time_seconds"] = end_time - start_time
            results["scraping_stats"]["end_time"] = datetime.now().isoformat()

            if results["scraping_stats"]["pages_scraped"] > 0:
                results["completion_status"] = "completed"
            else:
                results["completion_status"] = "no_content_scraped"

            # Generate summary
            results["summary"] = self._generate_scraping_summary(results)

            status = results["completion_status"]
            pages_scraped = results["scraping_stats"]["pages_scraped"]
            elapsed = results["scraping_stats"]["elapsed_time_seconds"]

            print(f"[ARINN-LOG] {datetime.now().isoformat()} - WEB-SCRAPING: Completed - Status: {status}, Pages: {pages_scraped}, Time: {elapsed:.1f}s")

            return results

        except Exception as e:
            error_msg = f"Scraping failed: {str(e)}"
            print(f"[ARINN-LOG] {datetime.now().isoformat()} - WEB-SCRAPING ERROR: {error_msg}")
            results["errors"].append(error_msg)
            results["completion_status"] = "failed"
            return results

    def _check_robots_txt(self, site_url: str) -> bool:
        """Check if scraping is allowed by robots.txt."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(site_url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

            # Try to fetch robots.txt
            try:
                import fetch
                robots_content = fetch.fetch_url(robots_url, timeout=10)
                if robots_content and "User-agent: *" in robots_content:
                    # Simple check - in production would parse properly
                    if "Disallow: /" in robots_content:
                        return False
            except Exception:
                pass  # If robots.txt can't be fetched, assume allowed

            return True
        except Exception:
            return True  # Default to allowed if check fails

    def _fetch_page_content(self, url: str, timeout: int) -> Optional[str]:
        """Enhanced fetch function with multiple fallback strategies for reliable web scraping."""
        try:
            import requests
            from urllib.parse import urlparse

            # Enhanced headers that work better with various sites including Python.org
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0',
                'DNT': '1'
            }

            # Create a session with retry strategy
            session = requests.Session()
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry

            retry_strategy = Retry(
                total=3,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS"],
                backoff_factor=1
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

            session.headers.update(headers)

            # First try with SSL verification
            try:
                response = session.get(url, timeout=timeout, allow_redirects=True)
            except requests.exceptions.SSLError:
                # If SSL fails, try without verification (safe for well-known sites like python.org)
                logging.info(f"SSL verification failed for {url}, trying without verification")
                response = session.get(url, timeout=timeout, allow_redirects=True, verify=False)
            except requests.exceptions.RequestException as e:
                logging.warning(f"Request failed for {url}: {e}")
                return None

            # Check response
            if response.status_code != 200:
                logging.warning(f"HTTP {response.status_code} for {url}")
                return None

            # Check content type
            content_type = response.headers.get('Content-Type', '').lower()
            if not ('html' in content_type or 'text' in content_type or 'xml' in content_type):
                logging.warning(f"Unexpected content type for {url}: {content_type}")
                return None

            # Check content length
            if len(response.text.strip()) < 100:
                logging.warning(f"Content too short for {url}: {len(response.text)} chars")
                return None

            return response.text

        except Exception as e:
            logging.warning(f"Enhanced fetch failed for {url}: {e}")
            return None

    def _fetch_page_content_with_fallback(self, url: str, timeout: int) -> Optional[str]:
        """Fetch with regular requests first, fallback to Selenium for JavaScript-heavy sites."""
        # Try enhanced requests first
        content = self._fetch_page_content(url, timeout)
        if content:
            return content

        # Fallback to Selenium for JavaScript-heavy or blocking sites
        try:
            # Check if Selenium is available
            try:
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options
                SELENIUM_AVAILABLE = True
            except ImportError:
                SELENIUM_AVAILABLE = False
                logging.warning("Selenium not available for fallback scraping")
                return None

            if not SELENIUM_AVAILABLE:
                return None

            logging.info(f"Using Selenium fallback for {url}")

            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')  # Speed up loading
            options.add_argument(f'--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

            try:
                driver = webdriver.Chrome(options=options)
            except Exception:
                # Try Firefox if Chrome fails
                from selenium.webdriver.firefox.options import Options as FirefoxOptions
                firefox_options = FirefoxOptions()
                firefox_options.add_argument('--headless')
                driver = webdriver.Firefox(options=firefox_options)

            driver.set_page_load_timeout(timeout)
            driver.get(url)

            # Wait for content to load
            import time
            time.sleep(3)  # Give JavaScript time to execute

            content = driver.page_source
            driver.quit()

            if content and len(content.strip()) > 100:
                return content

        except Exception as e:
            logging.warning(f"Selenium fallback also failed for {url}: {e}")

        return None

    def scrape_with_proxy_support(self, site_url: str, proxy_url: Optional[str] = None,
                                proxy_type: str = "http", **kwargs) -> Dict[str, Any]:
        """Scrape a site with proxy support for bypassing IP blocks."""
        if proxy_url:
            logging.info(f"Using proxy: {proxy_url}")

            # Set environment variables for proxy
            import os
            if proxy_type.lower() == "socks5":
                os.environ['HTTPS_PROXY'] = proxy_url
                os.environ['HTTP_PROXY'] = proxy_url
            else:
                # HTTP/HTTPS proxy
                proxy_dict = {
                    'http': proxy_url,
                    'https': proxy_url
                }
                # Store proxy config for use in fetch function
                self.agent._proxy_config = proxy_dict

        try:
            result = self.scrape_specific_site(site_url, **kwargs)
            return result
        finally:
            # Clean up proxy settings
            if proxy_url:
                os.environ.pop('HTTPS_PROXY', None)
                os.environ.pop('HTTP_PROXY', None)
                self.agent._proxy_config = None

    def diagnose_web_access(self, test_urls: List[str] = None) -> Dict[str, Any]:
        """Diagnose web access issues and provide detailed connectivity information."""
        if test_urls is None:
            test_urls = [
                "https://httpbin.org/get",  # Simple test
                "https://docs.python.org/3/",  # Target site
                "https://www.google.com/",  # Major site
                "https://github.com/",  # Development site
            ]

        results = {
            "timestamp": datetime.now().isoformat(),
            "diagnostics": [],
            "recommendations": []
        }

        for url in test_urls:
            diag = {
                "url": url,
                "connectivity": False,
                "ssl_working": False,
                "content_type": None,
                "response_size": 0,
                "status_code": None,
                "error": None,
                "headers": {}
            }

            try:
                import requests

                # Test basic connectivity
                response = requests.head(url, timeout=10, allow_redirects=True)
                diag["status_code"] = response.status_code
                diag["connectivity"] = True
                diag["headers"] = dict(response.headers)
                diag["content_type"] = response.headers.get('Content-Type')

                # Test SSL
                if url.startswith('https://'):
                    try:
                        requests.get(url, timeout=10, verify=True)
                        diag["ssl_working"] = True
                    except requests.exceptions.SSLError:
                        diag["ssl_working"] = False
                        diag["ssl_error"] = "SSL verification failed"

                # Test full content fetch
                if response.status_code == 200:
                    full_response = requests.get(url, timeout=15)
                    diag["response_size"] = len(full_response.text)

            except requests.exceptions.SSLError as e:
                diag["error"] = f"SSL Error: {e}"
                diag["ssl_working"] = False
            except requests.exceptions.ConnectionError as e:
                diag["error"] = f"Connection Error: {e}"
            except requests.exceptions.Timeout as e:
                diag["error"] = f"Timeout Error: {e}"
            except Exception as e:
                diag["error"] = f"General Error: {e}"

            results["diagnostics"].append(diag)

        # Generate recommendations
        all_connect = all(d["connectivity"] for d in results["diagnostics"])
        ssl_issues = any(not d.get("ssl_working", True) for d in results["diagnostics"] if d["url"].startswith("https://"))

        if not all_connect:
            results["recommendations"].append("Network connectivity issues detected. Check internet connection.")
        if ssl_issues:
            results["recommendations"].append("SSL verification issues. Consider using verify=False for trusted sites.")
        if any(d["status_code"] == 429 for d in results["diagnostics"]):
            results["recommendations"].append("Rate limiting detected. Implement delays between requests.")
        if any(d["status_code"] in [403, 429] for d in results["diagnostics"]):
            results["recommendations"].append("Possible blocking. Try different user agents or proxies.")

        return results

    def get_from_web_archive(self, url: str, target_date: Optional[str] = None) -> Optional[str]:
        """Get content from Internet Archive Wayback Machine."""
        try:
            import requests

            # Construct Wayback Machine URL
            if target_date:
                # Format: YYYYMMDDHHMMSS
                wayback_url = f"https://web.archive.org/web/{target_date}/{url}"
            else:
                # Get latest available snapshot
                wayback_url = f"https://web.archive.org/web/2/{url}"

            logging.info(f"Fetching from Wayback Machine: {wayback_url}")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }

            response = requests.get(wayback_url, headers=headers, timeout=30)

            if response.status_code == 200 and 'text/html' in response.headers.get('Content-Type', ''):
                return response.text

        except Exception as e:
            logging.warning(f"Wayback Machine fetch failed for {url}: {e}")

        return None

    def intelligent_web_search(self, query: str, max_results: int = 10,
                             search_engine: str = "duckduckgo") -> Dict[str, Any]:
        """Perform intelligent web search using available search engines."""
        results = {
            "query": query,
            "search_engine": search_engine,
            "results": [],
            "total_found": 0,
            "timestamp": datetime.now().isoformat()
        }

        try:
            if search_engine.lower() == "duckduckgo":
                # Use DuckDuckGo search (already available in the system)
                search_results = self.agent.search_web(query, max_results=max_results)

                for result in search_results.get("results", []):
                    results["results"].append({
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "snippet": result.get("snippet", ""),
                        "source": "duckduckgo"
                    })

            elif search_engine.lower() == "google":
                # Placeholder for Google Custom Search API integration
                logging.warning("Google Custom Search API not configured")
                results["error"] = "Google Custom Search API not configured"

            results["total_found"] = len(results["results"])

        except Exception as e:
            results["error"] = str(e)
            logging.error(f"Intelligent web search failed: {e}")

        return results

    def _process_scraped_content(self, url: str, content: str, content_filters: List[str]) -> Dict[str, Any]:
        """Process and structure scraped content."""
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(content, 'html.parser')

            # Extract basic metadata
            title = soup.title.string if soup.title else "No title"
            meta_description = ""
            meta_keywords = ""

            # Get meta tags
            for meta in soup.find_all('meta'):
                if meta.get('name') == 'description':
                    meta_description = meta.get('content', '')
                elif meta.get('name') == 'keywords':
                    meta_keywords = meta.get('content', '')

            # Extract main content
            main_content = self._extract_main_content(soup)

            # Check content filters
            content_relevance = 0.0
            if content_filters:
                filter_text = ' '.join(content_filters).lower()
                content_text = (title + ' ' + meta_description + ' ' + main_content).lower()
                content_relevance = sum(1 for filter_word in filter_text.split()
                                      if filter_word in content_text) / len(filter_text.split())

            # Extract headings for structure
            headings = []
            for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                headings.append({
                    "level": int(h.name[1]),
                    "text": h.get_text(separator=' ', strip=True),
                    "id": h.get('id', '')
                })

            return {
                "url": url,
                "title": title,
                "meta_description": meta_description,
                "meta_keywords": meta_keywords,
                "main_content": main_content,
                "headings": headings,
                "content_length": len(content),
                "content_relevance": content_relevance,
                "scraped_at": datetime.now().isoformat(),
                "word_count": len(main_content.split()) if main_content else 0
            }

        except Exception as e:
            return {
                "url": url,
                "error": str(e),
                "content_length": len(content) if content else 0,
                "scraped_at": datetime.now().isoformat()
            }

    def _extract_main_content(self, soup) -> str:
        """Extract main content from HTML soup."""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        # Try to find main content areas
        content_selectors = [
            'main',
            '[role="main"]',
            '.content',
            '.main-content',
            '#content',
            '#main',
            'article',
            '.post-content',
            '.entry-content'
        ]

        for selector in content_selectors:
            main_element = soup.select_one(selector)
            if main_element:
                return main_element.get_text(separator=' ', strip=True)

        # Fallback: get text from body
        body = soup.find('body')
        if body:
            return body.get_text(separator=' ', strip=True)

        return soup.get_text(separator=' ', strip=True)

    def _extract_internal_links(self, content: str, base_url: str, base_domain: str) -> List[str]:
        """Extract internal links from page content."""
        try:
            from bs4 import BeautifulSoup
            from urllib.parse import urljoin, urlparse

            soup = BeautifulSoup(content, 'html.parser')
            internal_links = []

            for a in soup.find_all('a', href=True):
                href = a['href']
                absolute_url = urljoin(base_url, href)

                # Check if it's an internal link
                parsed = urlparse(absolute_url)
                if parsed.netloc == base_domain and parsed.scheme in ['http', 'https']:
                    # Avoid fragments and query-only URLs
                    if not parsed.path or parsed.path != '/':
                        internal_links.append(absolute_url)

            return list(set(internal_links))  # Remove duplicates

        except Exception as e:
            logging.warning(f"Failed to extract links from {base_url}: {e}")
            return []

    def _store_scraped_content(self, content_data: Dict[str, Any]):
        """Store scraped content in database with duplicate prevention."""
        try:
            if not hasattr(self.agent, 'db') or not self.agent.db:
                return

            # Create a topic for web scraping if it doesn't exist
            topic_id = self.agent.db.get_or_create_topic("web_scraping")

            # Store as document - this automatically prevents duplicates via content hash
            content = content_data.get("main_content", "")
            if content:  # Only store if there's actual content
                added, doc_id = self.agent.db.add_document(
                    topic_id=topic_id,
                    url=content_data["url"],
                    title=content_data.get("title", "Scraped Content"),
                    content=content,
                    created_at=content_data.get("scraped_at", datetime.now().isoformat())
                )

                # If document was added (not a duplicate), add snippets for searchability
                if added and doc_id:
                    self.agent.db.add_snippets_from_text(
                        topic_id=topic_id,
                        doc_id=doc_id,
                        text=content,
                        created_at=content_data.get("scraped_at", datetime.now().isoformat()),
                        min_len=100  # Shorter snippets for web content
                    )

        except Exception as e:
            logging.warning(f"Failed to store scraped content: {e}")

    def _generate_scraping_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of scraping results."""
        stats = results["scraping_stats"]

        summary = {
            "total_pages_processed": stats["pages_scraped"] + stats["pages_failed"],
            "success_rate": (stats["pages_scraped"] / max(1, stats["pages_scraped"] + stats["pages_failed"])) * 100,
            "average_page_size": stats["content_size_bytes"] / max(1, stats["pages_scraped"]),
            "total_content_size_mb": stats["content_size_bytes"] / (1024 * 1024),
            "scraping_duration_minutes": stats["elapsed_time_seconds"] / 60,
            "pages_per_minute": (stats["pages_scraped"] / max(1, stats["elapsed_time_seconds"])) * 60,
            "links_discovered": stats["total_links_found"]
        }

        # Content analysis summary
        if results["scraped_content"]:
            content_lengths = [c.get("content_length", 0) for c in results["scraped_content"] if "content_length" in c]
            word_counts = [c.get("word_count", 0) for c in results["scraped_content"] if "word_count" in c]

            summary["content_stats"] = {
                "average_content_length": sum(content_lengths) / max(1, len(content_lengths)),
                "total_words": sum(word_counts),
                "average_words_per_page": sum(word_counts) / max(1, len(word_counts))
            }

        return summary