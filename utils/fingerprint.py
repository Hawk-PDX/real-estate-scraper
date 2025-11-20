"""
User agent rotation and fingerprinting.

Can't just use random strings - sites validate browser/OS combos.
These are real user agent strings I pulled from actual traffic.
"""

import random


class FingerprintRotator:
    def __init__(self):
        # Real user agents from Chrome on different platforms
        # Don't make these up - sites check if they're valid
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        
        # Screen resolutions that match the OS
        # Windows machines commonly use these
        self.screen_resolutions = [
            {'width': 1920, 'height': 1080},
            {'width': 1536, 'height': 864},
            {'width': 1440, 'height': 900},
            {'width': 2560, 'height': 1440},
        ]
        
        # Match timezone to location if using geo-proxies
        # For now just use common US timezones
        self.timezones = [
            'America/New_York',
            'America/Chicago',
            'America/Denver',
            'America/Los_Angeles',
        ]
    
    def get_random_user_agent(self):
        """Pick a random but valid user agent."""
        return random.choice(self.user_agents)
    
    def get_random_screen_resolution(self):
        """Get a realistic screen resolution."""
        return random.choice(self.screen_resolutions)
    
    def get_random_timezone(self):
        """Get a US timezone."""
        return random.choice(self.timezones)
    
    def generate_fingerprint(self):
        """
        Generate a full browser fingerprint.
        Keep these consistent within a session - don't change mid-scrape.
        """
        resolution = self.get_random_screen_resolution()
        
        return {
            'user_agent': self.get_random_user_agent(),
            'screen_width': resolution['width'],
            'screen_height': resolution['height'],
            'timezone': self.get_random_timezone(),
            'language': 'en-US',
            'platform': self._get_platform_from_ua(self.user_agents[0]),
        }
    
    def _get_platform_from_ua(self, user_agent):
        """Extract platform from user agent so they match."""
        if 'Windows' in user_agent:
            return 'Win32'
        elif 'Mac' in user_agent:
            return 'MacIntel'
        elif 'Linux' in user_agent:
            return 'Linux x86_64'
        return 'Win32'  # Default fallback
    
    def get_headers(self, user_agent=None):
        """
        Generate realistic HTTP headers.
        Order matters - sites can fingerprint based on header order.
        """
        if not user_agent:
            user_agent = self.get_random_user_agent()
        
        # Header order mimics Chrome
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',  # Do Not Track
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
        
        return headers
