"""
Browser setup that doesn't get immediately flagged as a bot.

Took forever to figure out all the settings that sites check.
Regular Selenium just sets navigator.webdriver = true and you're dead.
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import time


class StealthBrowser:
    def __init__(self, proxy=None, headless=False):
        """
        headless=True gets detected immediately, don't bother unless testing.
        proxy format: 'ip:port:user:pass' or 'ip:port'
        """
        self.proxy = proxy
        self.headless = headless
        self.driver = None
        
    def start(self):
        options = uc.ChromeOptions()
        
        # These help but aren't foolproof
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-web-security')
        
        # Fake a real user's window size (not 800x600)
        options.add_argument('--window-size=1920,1080')
        
        # Language settings (some sites check this)
        options.add_argument('--lang=en-US')
        
        if self.proxy:
            # Format: ip:port:user:pass
            if ':' in self.proxy:
                parts = self.proxy.split(':')
                if len(parts) == 4:
                    proxy_str = f'{parts[0]}:{parts[1]}'
                    options.add_argument(f'--proxy-server={proxy_str}')
                else:
                    options.add_argument(f'--proxy-server={self.proxy}')
        
        # Don't use headless unless you absolutely have to
        # Sites can detect it through various means
        if self.headless:
            options.add_argument('--headless=new')
        
        try:
            self.driver = uc.Chrome(options=options, version_main=120)
            
            # Override some JS properties that leak automation
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    
                    // Make chrome look more legitimate
                    window.chrome = {
                        runtime: {}
                    };
                '''
            })
            
        except Exception as e:
            print(f"Failed to start browser: {e}")
            raise
            
        return self.driver
    
    def human_delay(self, min_seconds=2, max_seconds=5):
        """
        Random delay that feels more human.
        Don't just use time.sleep(1) everywhere - that's a pattern.
        """
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def scroll_slowly(self):
        """
        Scroll the page like a human would.
        Helps trigger lazy-loaded content too.
        """
        total_height = self.driver.execute_script("return document.body.scrollHeight")
        current_position = 0
        scroll_increment = random.randint(300, 500)
        
        while current_position < total_height:
            current_position += scroll_increment
            self.driver.execute_script(f"window.scrollTo(0, {current_position});")
            time.sleep(random.uniform(0.3, 0.8))
    
    def move_mouse_randomly(self):
        """
        Some advanced fingerprinting tracks mouse movement.
        This is probably overkill but doesn't hurt.
        """
        try:
            self.driver.execute_script("""
                var event = new MouseEvent('mousemove', {
                    'view': window,
                    'bubbles': true,
                    'cancelable': true,
                    'clientX': Math.random() * window.innerWidth,
                    'clientY': Math.random() * window.innerHeight
                });
                document.dispatchEvent(event);
            """)
        except:
            pass  # Not critical if this fails
    
    def wait_for_element(self, selector, by=By.CSS_SELECTOR, timeout=10):
        """Cleaner than writing WebDriverWait every time."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return element
        except:
            return None
    
    def close(self):
        if self.driver:
            self.driver.quit()
