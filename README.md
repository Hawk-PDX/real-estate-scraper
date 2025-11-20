# Real Estate Scraper

Scraping real estate sites turned out way harder than I expected. After 8 years in real estate, I knew exactly what data I needed - price trends, days on market, comparables. The challenge was getting past Cloudflare, CAPTCHAs, and all the anti-bot stuff these sites throw at you.

## What This Does

Pulls property listings from major real estate sites. I needed market data for analysis without manually clicking through hundreds of pages. Started simple, then had to get creative when I kept hitting rate limits and blocks.

## The Bot Detection Problem

These sites really don't want you scraping them:

**Cloudflare** - Hits you with JavaScript challenges immediately. Regular Selenium gets caught instantly because of `navigator.webdriver` flags.

**Fingerprinting** - They check your browser fingerprint. Same user agent + headers every time = instant ban.

**Rate Limiting** - Make 50 requests from the same IP and you're done. Had to learn about residential proxies the hard way.

**CAPTCHAs** - reCAPTCHA v2 shows up after suspicious activity. Killed hours of scraping runs until I figured out 2Captcha.

## How I Got Around It

### Undetected Chrome

Switched from regular Selenium to `undetected-chromedriver`. It patches the automation flags that sites check for. Had to disable headless mode though - sites can detect that too.

```python
import undetected_chromedriver as uc

options = uc.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
driver = uc.Chrome(options=options, version_main=120)
```

### Proxy Rotation

Bought residential proxies (not cheap but necessary). Rotate them every 30-50 requests. Keep a proxy-session mapping so you don't break authenticated flows.

```python
# Simple round-robin rotation
def get_next_proxy(self):
    proxy = self.proxies[self.current_index]
    self.current_index = (self.current_index + 1) % len(self.proxies)
    return proxy
```

### Fingerprint Randomization

Rotate user agents, screen resolutions, timezones. Made a list of realistic combinations. Found out the hard way that random strings don't work - sites check for valid browser/OS combos.

### Human-Like Timing

Added random delays (3-8 seconds). Scroll the page gradually. Move the mouse around occasionally. Sounds paranoid but it works.

## Project Structure

```
scrapers/
  base_scraper.py       # Common anti-bot logic
  zillow_scraper.py     # Zillow specific stuff
  redfin_scraper.py     # Redfin implementation
  
utils/
  stealth_browser.py    # Undetected Chrome setup
  proxy_manager.py      # Proxy rotation
  fingerprint.py        # User agent cycling
  
database/
  models.py             # SQLAlchemy models
  
config/
  settings.py
  proxies.txt           # One proxy per line (format: ip:port:user:pass)
```

## Data I'm Capturing

From my real estate background, I know what metrics actually matter:

- Price, beds, baths, sqft (the basics)
- Days on market (shows how fast things move)
- Price reductions (indicates seller motivation)
- List-to-sale ratio (for CMA work)
- Comparable sales within 0.5 miles
- Property tax history

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# You need Chrome installed
# brew install chromium
```

Copy `.env.example` to `.env` and fill in:
```
DATABASE_URL=sqlite:///listings.db
CAPTCHA_API_KEY=your_key_here  # Get from 2captcha.com
USE_PROXIES=true
```

## Running It

```python
from scrapers.zillow_scraper import ZillowScraper

scraper = ZillowScraper()
listings = scraper.search("Portland, OR", max_pages=3)
scraper.save_to_db(listings)
```

Runs about 2-3 pages per minute safely. Faster than that and you'll get blocked.

## What I Learned

**Start slow.** I burned through 20 IPs trying to go fast. Sites would rather block you than serve you.

**Proxies matter.** Datacenter IPs get flagged. Residential proxies cost more but actually work.

**Headless = detected.** Had to run with a visible browser. Pain during development but necessary.

**Sessions are sticky.** Keep cookies tied to the same proxy. Don't mix them.

**User agents need to match.** Can't use a mobile UA with desktop screen resolution. Sites check this.

## Why I Built This

I spent years pulling comps manually for CMAs. Tedious work. Wanted to automate the data gathering so I could focus on analysis. Also wanted to track price trends over time - something MLS systems don't do well.

This project taught me more about real web scraping than any tutorial. When you're bypassing actual production anti-bot systems, you learn fast.

## Notes

This is for learning and portfolio purposes. Real estate sites have APIs (though expensive). This demonstrates the technical challenge of working with protected sites.

Built during my transition from real estate to software development. Combines 8 years of knowing what data matters with learning how to actually extract it at scale.
