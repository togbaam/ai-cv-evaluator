import asyncio
from playwright.async_api import async_playwright
import urllib.parse
from bs4 import BeautifulSoup
import re

class Scraper:
    def __init__(self, source_name: str):
        self.source_name = source_name
    
    async def get_page_content(self, url: str) -> str:
        # Use playwright to handle JS-rendered content and bypass simple bot checks
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            
            # Simple stealth evasion
            await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=45000)
                await asyncio.sleep(2) # brief wait for client side rendering
                content = await page.content()
            except Exception as e:
                print(f"Error fetching URL {url}: {e}")
                content = ""
            finally:
                await browser.close()
                
            return content

    async def scrape_jobs(self, query: str, max_jobs: int = 5):
        raise NotImplementedError

class ITViecScraper(Scraper):
    def __init__(self):
        super().__init__("ITviec")
        
    async def scrape_jobs(self, query: str, max_jobs: int = 5):
        encoded_query = urllib.parse.quote(query)
        search_url = f"https://itviec.com/it-jobs/{encoded_query}"
        
        print(f"Scraping ITviec: {search_url}")
        content = await self.get_page_content(search_url)
        if not content:
            return []
            
        soup = BeautifulSoup(content, 'html.parser')
        jobs = []
        
        # ITviec uses 'job-card' classes. If DOM changes, fallback to searching links.
        job_cards = soup.find_all('div', class_=re.compile(r'job-card', re.I))
        if not job_cards:
            items = soup.find_all('a', href=re.compile(r'/it-jobs/'))
            job_cards = [item.parent.parent for item in items if item.text.strip()]
            
        visited_urls = set()
        
        for card in job_cards:
            if len(jobs) >= max_jobs:
                break
                
            title_elem = card.find('h3') or card.find('a')
            if not title_elem:
                continue
            title = title_elem.text.strip()
            
            link_elem = card.find('a', href=True)
            if not link_elem:
                continue
            url = f"https://itviec.com{link_elem['href']}" if link_elem['href'].startswith('/') else link_elem['href']
            
            if url in visited_urls:
                continue
            visited_urls.add(url)
            
            # Extract basic listing info
            company = card.find(string=re.compile("Company", re.I))
            company = company.parent.text.strip() if company else "Unknown"
            
            salary_elem = card.find(string=re.compile(r'\$'))
            salary = salary_elem.strip() if salary_elem else "Negotiable"
            
            location_elem = card.find('div', class_=re.compile('location', re.I))
            location = location_elem.text.strip() if location_elem else "Vietnam"
            
            # Fetch detailed JD sequentially
            job_content = await self.get_page_content(url)
            job_soup = BeautifulSoup(job_content, 'html.parser')
            jd_div = job_soup.find('div', class_=re.compile('description', re.I))
            jd = jd_div.text.strip() if jd_div else "Could not extract full JD. (Possible bot block)"
            
            jobs.append({
                "Job Title": title,
                "Company": company,
                "Salary": salary,
                "Location": location,
                "URL": url,
                "Description": jd,
                "Source": self.source_name,
                "Post Date": "Recent"
            })
            
        return jobs

class TopCVScraper(Scraper):
    def __init__(self):
        super().__init__("TopCV")
        
    async def scrape_jobs(self, query: str, max_jobs: int = 5):
        encoded_query = urllib.parse.quote(query.replace(' ', '-'))
        search_url = f"https://www.topcv.vn/tim-viec-lam-{encoded_query}"
        
        print(f"Scraping TopCV: {search_url}")
        content = await self.get_page_content(search_url)
        if not content:
            return []
            
        soup = BeautifulSoup(content, 'html.parser')
        jobs = []
        
        job_items = soup.find_all('div', class_=re.compile('job-item', re.I))
        if not job_items:
            headers = soup.find_all('h3')
            job_items = [h.parent for h in headers if h.find('a')]
            
        visited_urls = set()
        
        for item in job_items:
            if len(jobs) >= max_jobs:
                break
                
            title_elem = item.find('h3')
            if not title_elem:
                title_elem = item.find('a', class_=re.compile('title', re.I))
            if not title_elem:
                continue
                
            title = title_elem.text.strip()
            
            link_elem = title_elem.find('a', href=True) if title_elem.name != 'a' else title_elem
            if not link_elem:
                continue
            url = link_elem['href']
            if not url.startswith('http'):
                url = "https://www.topcv.vn" + url
                
            if url in visited_urls:
                continue
            visited_urls.add(url)
            
            company_elem = item.find('a', class_=re.compile('company', re.I))
            company = company_elem.text.strip() if company_elem else "Unknown"
            
            # Fetch detailed JD
            job_content = await self.get_page_content(url)
            job_soup = BeautifulSoup(job_content, 'html.parser')
            jd_div = job_soup.find('div', class_=re.compile('job-detail|description|content', re.I))
            jd = jd_div.get_text(separator="\n").strip() if jd_div else "Could not extract full JD."
            
            jobs.append({
                "Job Title": title,
                "Company": company,
                "Salary": "Hidden/Negotiable",
                "Location": "Vietnam",
                "URL": url,
                "Description": jd,
                "Source": self.source_name,
                "Post Date": "Recent"
            })
            
        return jobs
