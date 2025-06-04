# recon.py
import asyncio
import aiohttp
from urllib.parse import urlparse
import dns.resolver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
import os
from utils import classify_page

# Setting up headless Chrome
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# Async subdomain enumeration
async def find_subdomains(domain, wordlist_file):
    subdomains = set()
    try:
        with open(wordlist_file, 'r') as f:
            subdomains_list = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        subdomains_list = []
    
    # Active DNS brute-forcing
    async with aiohttp.ClientSession() as session:
        tasks = [check_dns(f"{sub}.{domain}", session) for sub in subdomains_list]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for test_domain, resolved in results:
            if resolved:
                subdomains.add(test_domain)
    
    # Passive recon
    passive_subdomains = await passive_recon(domain)
    subdomains.update(passive_subdomains)
    return subdomains

# Checking DNS resolution
async def check_dns(domain, session):
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 2
        resolver.lifetime = 2
        answers = resolver.resolve(domain, 'A')
        return domain, len(answers) > 0
    except Exception:
        return domain, False

# Passive recon via public APIs
async def passive_recon(domain):
    subdomains = set()
    url = f"https://crt.sh/?q=%.{domain}&output=json"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    for entry in data:
                        subdomain = entry.get('name_value', '').strip()
                        if subdomain.endswith(domain) and not subdomain.startswith('*'):
                            subdomains.add(subdomain)
    except Exception as e:
        print(f"Passive recon error for {domain}: {e}")
    return subdomains

# Taking screenshot
def take_screenshot(url, driver, output_dir, category):
    try:
        driver.get(url)
        time.sleep(2)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{output_dir}/{category}/{urlparse(url).netloc}_{timestamp}.png"
        os.makedirs(f"{output_dir}/{category}", exist_ok=True)
        driver.save_screenshot(filename)
        return filename
    except Exception as e:
        print(f"Error capturing {url}: {e}")
        return None

# Red team scan for multiple domains
async def run_red_team_scan(domains, output_dir, wordlist_file, keywords):
    os.makedirs(output_dir, exist_ok=True)
    driver = setup_driver()
    results = {}
    
    for domain in domains:
        subdomains = await find_subdomains(domain, wordlist_file)
        domain_results = {}
        async with aiohttp.ClientSession() as session:
            for subdomain in subdomains:
                url = f"http://{subdomain}"
                try:
                    async with session.get(url, timeout=5) as response:
                        if response.status == 200:
                            content = await response.text()
                            category = classify_page(url, content, keywords)
                            screenshot = take_screenshot(url, driver, output_dir, category)
                            passive_source = "DNS Brute-Force" if subdomain in subdomains else "Passive Recon"
                            domain_results[subdomain] = {
                                'url': url,
                                'category': category,
                                'screenshot': screenshot,
                                'passive_source': passive_source
                            }
                except Exception as e:
                    print(f"Error processing {url}: {e}")
        results[domain] = domain_results
    
    driver.quit()
    return results

