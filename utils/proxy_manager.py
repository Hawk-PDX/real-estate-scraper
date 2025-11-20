"""
Proxy rotation because you'll get banned fast without it.

Learned this the hard way - burned through my entire home IP range
testing before I figured out I needed residential proxies.
"""

import random
from pathlib import Path


class ProxyManager:
    def __init__(self, proxy_file='config/proxies.txt', rotation_strategy='round_robin'):
        """
        Load proxies from file. Format per line:
        ip:port:user:pass  or just  ip:port
        
        rotation_strategy: 'round_robin', 'random', or 'least_used'
        """
        self.proxy_file = proxy_file
        self.rotation_strategy = rotation_strategy
        self.proxies = []
        self.proxy_usage = {}  # Track how many requests per proxy
        self.current_index = 0
        self.max_requests_per_proxy = 50  # Switch after this many requests
        
        self._load_proxies()
    
    def _load_proxies(self):
        """Read proxies from file."""
        try:
            path = Path(self.proxy_file)
            if not path.exists():
                print(f"No proxy file found at {self.proxy_file}")
                print("Running without proxies (risky)")
                return
            
            with open(path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        self.proxies.append(line)
                        self.proxy_usage[line] = 0
            
            print(f"Loaded {len(self.proxies)} proxies")
        except Exception as e:
            print(f"Error loading proxies: {e}")
    
    def get_proxy(self):
        """
        Get next proxy based on rotation strategy.
        Returns None if no proxies available.
        """
        if not self.proxies:
            return None
        
        if self.rotation_strategy == 'round_robin':
            return self._round_robin()
        elif self.rotation_strategy == 'random':
            return self._random_proxy()
        elif self.rotation_strategy == 'least_used':
            return self._least_used()
        else:
            return self._round_robin()
    
    def _round_robin(self):
        """Simple rotation through the list."""
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        self.proxy_usage[proxy] += 1
        return proxy
    
    def _random_proxy(self):
        """Pick random proxy each time."""
        proxy = random.choice(self.proxies)
        self.proxy_usage[proxy] += 1
        return proxy
    
    def _least_used(self):
        """Use the proxy that's been hit the least."""
        proxy = min(self.proxy_usage.keys(), key=lambda k: self.proxy_usage[k])
        self.proxy_usage[proxy] += 1
        return proxy
    
    def should_rotate(self, current_proxy):
        """
        Check if we've used this proxy too much.
        Helps avoid rate limits on a single IP.
        """
        if not current_proxy:
            return False
        
        usage = self.proxy_usage.get(current_proxy, 0)
        return usage >= self.max_requests_per_proxy
    
    def mark_proxy_bad(self, proxy):
        """
        Remove a proxy that's been banned or isn't working.
        In production you'd want to retry it later, but for now just kill it.
        """
        if proxy in self.proxies:
            print(f"Removing bad proxy: {proxy}")
            self.proxies.remove(proxy)
            if proxy in self.proxy_usage:
                del self.proxy_usage[proxy]
            
            # Adjust index if needed
            if self.current_index >= len(self.proxies) and len(self.proxies) > 0:
                self.current_index = 0
    
    def reset_usage(self):
        """Reset usage counters. Useful if you're scraping over multiple sessions."""
        for proxy in self.proxy_usage:
            self.proxy_usage[proxy] = 0
        self.current_index = 0
    
    def get_stats(self):
        """See which proxies are getting hammered."""
        return {
            'total_proxies': len(self.proxies),
            'usage_per_proxy': self.proxy_usage,
            'current_index': self.current_index
        }
