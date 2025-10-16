"""
Advanced Browser Controller for comprehensive web automation.

This module provides extensive browser control capabilities including:
- Complex user interactions (clicks, typing, scrolling, drag-and-drop)
- Screenshot and video recording
- Multi-tab management
- Form automation with validation
- JavaScript execution and monitoring
- Network request interception
- Performance monitoring
"""

import time
import json
import base64
import logging
from typing import Optional, Dict, List, Any, Union, Tuple
from pathlib import Path
from datetime import datetime

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.ui import WebDriverWait, Select
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    import cv2
    import numpy as np
    from PIL import Image
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False


class AdvancedBrowserController:
    """Advanced browser automation with comprehensive control capabilities."""
    
    def __init__(self, driver_type: str = "chrome", headless: bool = True, 
                 enable_recording: bool = False, window_size: Tuple[int, int] = (1920, 1080),
                 user_data_dir: Optional[str] = None, proxy: Optional[str] = None):
        self.driver_type = driver_type.lower()
        self.headless = headless
        self.enable_recording = enable_recording
        self.window_size = window_size
        self.user_data_dir = user_data_dir
        self.proxy = proxy
        
        self.driver = None
        self.actions = None
        self.wait = None
        self.recording_frames = []
        self.performance_logs = []
        self.network_logs = []
        
        # Safety controls
        self.max_execution_time = 300  # 5 minutes max per operation
        self.allowed_domains = set()
        self.blocked_domains = set()
        self.rate_limit_delay = 1.0
        self.last_action_time = 0
        
    def _get_driver_options(self):
        """Configure driver options based on browser type."""
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is not available. Install with: pip install selenium")
        
        if self.driver_type == "chrome":
            options = ChromeOptions()
            if self.headless:
                options.add_argument("--headless")
            options.add_argument(f"--window-size={self.window_size[0]},{self.window_size[1]}")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-images")  # Faster loading
            options.add_argument("--disable-javascript")  # Can be overridden per page
            
            # Performance monitoring
            options.add_argument("--enable-logging")
            options.add_argument("--log-level=0")
            options.set_capability("goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"})
            
            # User data directory for persistent sessions
            if self.user_data_dir:
                options.add_argument(f"--user-data-dir={self.user_data_dir}")
            
            # Proxy configuration
            if self.proxy:
                options.add_argument(f"--proxy-server={self.proxy}")
            
            return options, ChromeService(ChromeDriverManager().install())
            
        elif self.driver_type == "firefox":
            options = FirefoxOptions()
            if self.headless:
                options.add_argument("--headless")
            options.add_argument(f"--width={self.window_size[0]}")
            options.add_argument(f"--height={self.window_size[1]}")
            
            # Performance monitoring
            caps = DesiredCapabilities.FIREFOX
            caps['loggingPrefs'] = {'browser': 'ALL', 'driver': 'ALL'}
            
            return options, FirefoxService(GeckoDriverManager().install())
        else:
            raise ValueError(f"Unsupported driver type: {self.driver_type}")
    
    def start(self) -> bool:
        """Initialize the browser driver."""
        try:
            options, service = self._get_driver_options()
            
            if self.driver_type == "chrome":
                self.driver = webdriver.Chrome(service=service, options=options)
            elif self.driver_type == "firefox":
                self.driver = webdriver.Firefox(service=service, options=options)
            
            self.driver.set_page_load_timeout(30)
            self.actions = ActionChains(self.driver)
            self.wait = WebDriverWait(self.driver, 10)
            
            # Set window size
            self.driver.set_window_size(*self.window_size)
            
            return True
        except Exception as e:
            logging.error(f"Failed to start browser: {e}")
            return False
    
    def navigate_to(self, url: str, wait_for_load: bool = True) -> bool:
        """Navigate to a URL with comprehensive error handling."""
        if not self._check_domain_safety(url):
            return False
        
        self._enforce_rate_limit()
        
        try:
            self.driver.get(url)
            if wait_for_load:
                # Wait for page to be ready
                self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            return True
        except Exception as e:
            logging.error(f"Navigation failed for {url}: {e}")
            return False
    
    def find_element_advanced(self, selector: str, by: str = "css", timeout: int = 10, 
                            wait_for_visible: bool = True) -> Optional[Any]:
        """Advanced element finding with multiple strategies."""
        try:
            by_map = {
                "css": By.CSS_SELECTOR,
                "xpath": By.XPATH,
                "id": By.ID,
                "class": By.CLASS_NAME,
                "tag": By.TAG_NAME,
                "name": By.NAME,
                "link": By.LINK_TEXT,
                "partial_link": By.PARTIAL_LINK_TEXT
            }
            
            by_type = by_map.get(by.lower(), By.CSS_SELECTOR)
            
            if wait_for_visible:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_element_located((by_type, selector))
                )
            else:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by_type, selector))
                )
            
            return element
        except TimeoutException:
            logging.warning(f"Element not found: {selector} (by: {by})")
            return None
        except Exception as e:
            logging.error(f"Error finding element {selector}: {e}")
            return None
    
    def click_element(self, selector: str, by: str = "css", scroll_into_view: bool = True) -> bool:
        """Click an element with advanced options."""
        element = self.find_element_advanced(selector, by)
        if not element:
            return False
        
        try:
            if scroll_into_view:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(0.5)
            
            # Try multiple click strategies
            try:
                element.click()
            except Exception:
                # Fallback to JavaScript click
                self.driver.execute_script("arguments[0].click();", element)
            
            return True
        except Exception as e:
            logging.error(f"Click failed for {selector}: {e}")
            return False
    
    def type_text(self, selector: str, text: str, by: str = "css", clear_first: bool = True) -> bool:
        """Type text into an element with advanced options."""
        element = self.find_element_advanced(selector, by)
        if not element:
            return False
        
        try:
            if clear_first:
                element.clear()
            
            # Type character by character for more realistic behavior
            for char in text:
                element.send_keys(char)
                time.sleep(0.05)  # Small delay between characters
            
            return True
        except Exception as e:
            logging.error(f"Text input failed for {selector}: {e}")
            return False
    
    def fill_form(self, form_data: Dict[str, Any], form_selector: Optional[str] = None) -> bool:
        """Fill a form with comprehensive field detection."""
        try:
            form = None
            if form_selector:
                form = self.find_element_advanced(form_selector)
            else:
                form = self.driver.find_element(By.TAG_NAME, "form")
            
            if not form:
                return False
            
            for field_name, value in form_data.items():
                # Try multiple strategies to find the field
                field = None
                strategies = [
                    (By.NAME, field_name),
                    (By.ID, field_name),
                    (By.CSS_SELECTOR, f"[name='{field_name}']"),
                    (By.CSS_SELECTOR, f"[id='{field_name}']"),
                    (By.CSS_SELECTOR, f"input[placeholder*='{field_name}']"),
                ]
                
                for by_type, selector in strategies:
                    try:
                        field = form.find_element(by_type, selector)
                        break
                    except NoSuchElementException:
                        continue
                
                if not field:
                    logging.warning(f"Could not find form field: {field_name}")
                    continue
                
                # Handle different field types
                field_type = field.get_attribute("type") or "text"
                
                if field_type in ["checkbox", "radio"]:
                    if value and not field.is_selected():
                        field.click()
                elif field_type == "select":
                    select = Select(field)
                    try:
                        select.select_by_visible_text(str(value))
                    except:
                        try:
                            select.select_by_value(str(value))
                        except:
                            select.select_by_index(int(value) if str(value).isdigit() else 0)
                else:
                    field.clear()
                    field.send_keys(str(value))
            
            return True
        except Exception as e:
            logging.error(f"Form filling failed: {e}")
            return False
    
    def submit_form(self, form_selector: Optional[str] = None, 
                   submit_button_selector: Optional[str] = None) -> bool:
        """Submit a form with multiple strategies."""
        try:
            if submit_button_selector:
                return self.click_element(submit_button_selector)
            
            form = None
            if form_selector:
                form = self.find_element_advanced(form_selector)
            else:
                form = self.driver.find_element(By.TAG_NAME, "form")
            
            if not form:
                return False
            
            # Try to find and click submit button
            submit_selectors = [
                "input[type='submit']",
                "button[type='submit']",
                "button:contains('Submit')",
                "button:contains('Send')",
                "button:contains('Save')"
            ]
            
            for selector in submit_selectors:
                try:
                    submit_btn = form.find_element(By.CSS_SELECTOR, selector)
                    submit_btn.click()
                    return True
                except NoSuchElementException:
                    continue
            
            # Fallback to form submission
            form.submit()
            return True
            
        except Exception as e:
            logging.error(f"Form submission failed: {e}")
            return False
    
    def scroll_page(self, direction: str = "down", amount: int = 3) -> bool:
        """Scroll the page in specified direction."""
        try:
            if direction == "down":
                for _ in range(amount):
                    self.driver.execute_script("window.scrollBy(0, window.innerHeight);")
                    time.sleep(0.5)
            elif direction == "up":
                for _ in range(amount):
                    self.driver.execute_script("window.scrollBy(0, -window.innerHeight);")
                    time.sleep(0.5)
            elif direction == "top":
                self.driver.execute_script("window.scrollTo(0, 0);")
            elif direction == "bottom":
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            return True
        except Exception as e:
            logging.error(f"Scrolling failed: {e}")
            return False
    
    def take_screenshot(self, filename: Optional[str] = None, full_page: bool = False) -> Optional[str]:
        """Take a screenshot with advanced options."""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            if full_page:
                # Get full page dimensions
                total_width = self.driver.execute_script("return document.body.scrollWidth")
                total_height = self.driver.execute_script("return document.body.scrollHeight")
                self.driver.set_window_size(total_width, total_height)
            
            screenshot_path = Path(filename)
            self.driver.save_screenshot(str(screenshot_path))
            return str(screenshot_path)
        except Exception as e:
            logging.error(f"Screenshot failed: {e}")
            return None
    
    def execute_javascript(self, script: str, *args) -> Any:
        """Execute JavaScript with arguments."""
        try:
            return self.driver.execute_script(script, *args)
        except Exception as e:
            logging.error(f"JavaScript execution failed: {e}")
            return None
    
    def wait_for_element(self, selector: str, by: str = "css", timeout: int = 10) -> bool:
        """Wait for an element to be present and visible."""
        try:
            by_map = {
                "css": By.CSS_SELECTOR,
                "xpath": By.XPATH,
                "id": By.ID,
                "class": By.CLASS_NAME,
                "tag": By.TAG_NAME
            }
            
            by_type = by_map.get(by.lower(), By.CSS_SELECTOR)
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by_type, selector))
            )
            return True
        except TimeoutException:
            return False
    
    def get_page_info(self) -> Dict[str, Any]:
        """Get comprehensive page information."""
        try:
            info = {
                "url": self.driver.current_url,
                "title": self.driver.title,
                "window_size": self.driver.get_window_size(),
                "page_source_length": len(self.driver.page_source),
                "cookies": self.driver.get_cookies(),
                "local_storage": self.execute_javascript("return Object.keys(localStorage).reduce((obj, key) => { obj[key] = localStorage.getItem(key); return obj; }, {});"),
                "session_storage": self.execute_javascript("return Object.keys(sessionStorage).reduce((obj, key) => { obj[key] = sessionStorage.getItem(key); return obj; }, {});")
            }
            return info
        except Exception as e:
            logging.error(f"Failed to get page info: {e}")
            return {}
    
    def switch_tab(self, tab_index: int = 0) -> bool:
        """Switch to a specific tab."""
        try:
            tabs = self.driver.window_handles
            if 0 <= tab_index < len(tabs):
                self.driver.switch_to.window(tabs[tab_index])
                return True
            return False
        except Exception as e:
            logging.error(f"Tab switching failed: {e}")
            return False
    
    def open_new_tab(self, url: Optional[str] = None) -> bool:
        """Open a new tab."""
        try:
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            if url:
                self.navigate_to(url)
            return True
        except Exception as e:
            logging.error(f"New tab opening failed: {e}")
            return False
    
    def close_tab(self, tab_index: Optional[int] = None) -> bool:
        """Close a tab."""
        try:
            if tab_index is not None:
                self.switch_tab(tab_index)
            self.driver.close()
            if len(self.driver.window_handles) > 0:
                self.driver.switch_to.window(self.driver.window_handles[0])
            return True
        except Exception as e:
            logging.error(f"Tab closing failed: {e}")
            return False
    
    def get_network_logs(self) -> List[Dict[str, Any]]:
        """Get network request logs."""
        try:
            logs = self.driver.get_log("performance")
            network_logs = []
            
            for log in logs:
                message = json.loads(log["message"])
                if message["message"]["method"] == "Network.responseReceived":
                    response = message["message"]["params"]["response"]
                    network_logs.append({
                        "url": response["url"],
                        "status": response["status"],
                        "headers": response.get("headers", {}),
                        "timestamp": log["timestamp"]
                    })
            
            return network_logs
        except Exception as e:
            logging.error(f"Failed to get network logs: {e}")
            return []
    
    def _check_domain_safety(self, url: str) -> bool:
        """Check if domain is safe to interact with."""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc.lower()
            
            if self.blocked_domains and any(blocked in domain for blocked in self.blocked_domains):
                return False
            
            if self.allowed_domains and not any(allowed in domain for allowed in self.allowed_domains):
                return False
            
            return True
        except Exception:
            return False
    
    def _enforce_rate_limit(self):
        """Enforce rate limiting between actions."""
        current_time = time.time()
        time_since_last = current_time - self.last_action_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_action_time = time.time()
    
    def close(self):
        """Close the browser and clean up resources."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
