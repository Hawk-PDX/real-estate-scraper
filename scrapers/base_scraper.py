"""
Base scraper class with all the anti-bot stuff.

Individual site scrapers inherit from this so I don't repeat code.
Took a while to figure out what belongs here vs. site-specific logic.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.stealth_browser import StealthBrowser
from utils.proxy_manager import ProxyManager
from utils.fingerprint import FingerprintRotator
import time
import random


class BaseScraper:
    def __init__(self, use_proxies=False, headless=False):
        """
        Base setup for any scraper.
        use_proxies: Whether to rotate proxies (recommended)
        headless: Run browser in background (not recommended, gets detected)
        """
        self.use_proxies = use_proxies
        self.headless = headless
        self.browser = None
        self.current_proxy = None
        self.request_count = 0
        
        # Initialize utilities
        if use_proxies:
            self.proxy_manager = ProxyManager()
            self.current_proxy = self.proxy_manager.get_proxy()
        else:
            self.proxy_manager = None
        
        self.fingerprint = FingerprintRotator()
        
    def start_browser(self):
        """Fire up the stealth browser."""
        self.browser = StealthBrowser(proxy=self.current_proxy, headless=self.headless)
        self.browser.start()
        print(f"Browser started with proxy: {self.current_proxy or 'None'}")
    
    def close_browser(self):
        """Clean shutdown."""
        if self.browser:
            self.browser.close()
            print("Browser closed")
    
    def load_page(self, url, wait_selector=None):
        """
        Load a page with human-like behavior.
        wait_selector: CSS selector to wait for before proceeding
        """
        if not self.browser or not self.browser.driver:
            self.start_browser()
        
        try:
            # Random delay before loading (looks more human)
            self.browser.human_delay(2, 4)
            
            print(f"Loading: {url}")
            self.browser.driver.get(url)
            
            # Wait for page to actually load
            if wait_selector:
                self.browser.wait_for_element(wait_selector)
            else:
                time.sleep(random.uniform(2, 4))
            
            # Scroll like a human looking at the page
            self.browser.scroll_slowly()
            
            # Move mouse randomly (probably overkill)
            self.browser.move_mouse_randomly()
            
            self.request_count += 1
            
            # Check if we should rotate proxy
            if self.proxy_manager and self.proxy_manager.should_rotate(self.current_proxy):
                print("Rotating proxy...")
                self._rotate_identity()
            
            return True
            
        except Exception as e:
            print(f"Error loading page: {e}")
            # If page fails, might be proxy issue
            if self.proxy_manager and self.current_proxy:
                print("Trying different proxy...")
                self.proxy_manager.mark_proxy_bad(self.current_proxy)
                self._rotate_identity()
            return False
    
    def _rotate_identity(self):
        """
        Switch proxy and restart browser.
        Gives you a fresh fingerprint when the current one is burned.
        """
        self.close_browser()
        
        if self.proxy_manager:
            self.current_proxy = self.proxy_manager.get_proxy()
        
        self.start_browser()
        self.request_count = 0
        print("Identity rotated")
    
    def extract_data(self, selectors):
        """
        Pull data from page using CSS selectors.
        selectors: dict like {'price': '.price-class', 'address': '#address-id'}
        """
        if not self.browser or not self.browser.driver:
            return None
        
        data = {}
        for key, selector in selectors.items():
            try:
                element = self.browser.driver.find_element('css selector', selector)
                data[key] = element.text.strip() if element else None
            except:
                data[key] = None
        
        return data
    
    def is_blocked(self):
        """
        Check if we hit a block page.
        Different sites have different block patterns.
        Override this in site-specific scrapers.
        """
        if not self.browser or not self.browser.driver:
            return False
        
        page_source = self.browser.driver.page_source.lower()
        
        # Common block indicators
        block_phrases = [
            'access denied',
            'blocked',
            'captcha',
            'unusual traffic',
            'automation',
            'robot',
        ]
        
        return any(phrase in page_source for phrase in block_phrases)
    
    def handle_captcha(self):
        """
        Detect and handle CAPTCHA if it appears.
        For now just notify - you'd integrate 2captcha here.
        """
        if self.is_blocked():
            print("CAPTCHA or block detected!")
            print("In production, you'd solve this with 2captcha API")
            print("For now, waiting 30 seconds and rotating...")
            time.sleep(30)
            self._rotate_identity()
            return False
        return True
    
    # TODO: Add retry logic with exponential backoff
    # TODO: Integrate 2captcha for production use
