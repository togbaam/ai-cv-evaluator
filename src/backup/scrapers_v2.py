import asyncio
from playwright.async_api import async_playwright
import urllib.parse
from bs4 import BeautifulSoup

class Scraper:
    def __init__(self, source_name: str):
        self.source_name = source_name
    
    async def get_page_content(self, url: str) -> str:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=45000)
                await asyncio.sleep(2.5) # Chờ JS tải xong JD
                content = await page.content()
            except Exception as e:
                print(f"[{self.source_name}] Lỗi tải URL: {url} - {e}")
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
        slug = query.strip().lower().replace(' ', '-')
        search_url = f"https://itviec.com/it-jobs/{slug}"
        
        content = await self.get_page_content(search_url)
        if not content: return []
            
        soup = BeautifulSoup(content, 'html.parser')
        jobs = []
        
        # Bám sát cấu trúc của itviec.txt bạn cung cấp
        job_cards = soup.select('div.job-card')
        
        for card in job_cards[:max_jobs]:
            # Lấy Link và Tiêu đề
            title_a = card.select_one('h3.job-title a')
            if not title_a: continue
            title = title_a.text.strip()
            url = f"https://itviec.com{title_a['href']}"
            
            # Lấy Tên công ty
            company_a = card.select_one('.employer-info a')
            company = company_a.text.strip() if company_a else "Unknown Company"
            
            # Lấy Địa điểm
            loc_span = card.select_one('.mt-2 .d-flex span.text-rich-grey, .location span')
            location = loc_span.text.strip() if loc_span else "Vietnam"
            
            # Truy cập trang chi tiết để cào Job Description
            html = await self.get_page_content(url)
            job_soup = BeautifulSoup(html, 'html.parser')
            
            jd_elem = job_soup.select_one('.job-details__paragraph, .jd-page, .job-description, .job-details__content, div.description')
            jd = jd_elem.get_text(separator="\n").strip() if jd_elem else "Không thể trích xuất Job Description."
            
            jobs.append({
                "Job Title": title,
                "Company": company,
                "Salary": "Thỏa thuận",
                "Location": location,
                "URL": url,
                "Description": jd,
                "Source": self.source_name,
                "Post Date": "Mới đây"
            })
            
        return jobs

class TopCVScraper(Scraper):
    def __init__(self):
        super().__init__("TopCV")
        
    async def scrape_jobs(self, query: str, max_jobs: int = 5):
        encoded_kw = urllib.parse.quote(query.strip().lower().replace(' ', '-'))
        search_url = f"https://www.topcv.vn/tim-viec-lam-{encoded_kw}"
        
        content = await self.get_page_content(search_url)
        if not content: return []
            
        soup = BeautifulSoup(content, 'html.parser')
        jobs = []
        
        # Bám sát cấu trúc của topcv.txt bạn cung cấp
        job_items = soup.select('div.job-item-default, div.job-item')
        
        for item in job_items[:max_jobs]:
            # Lấy Link và Tiêu đề
            title_a = item.select_one('h3.title a')
            if not title_a: continue
            title = title_a.text.strip()
            url = title_a['href'].split('?')[0] # Cắt bỏ đoạn tracking phía sau
            if not url.startswith('http'):
                url = "https://www.topcv.vn" + url
                
            # Lấy Tên công ty
            company_a = item.select_one('a.company')
            company = company_a.text.strip() if company_a else "Unknown Company"
            
            # Lấy Địa điểm
            loc_label = item.select_one('label.address, .address')
            location = loc_label.text.strip() if loc_label else "Vietnam"
            
            # Truy cập trang chi tiết để cào Job Description
            html = await self.get_page_content(url)
            job_soup = BeautifulSoup(html, 'html.parser')
            
            jd_elem = job_soup.select_one('.job-detail__information-detail--content, .job-data, .job-description, .job-detail-content')
            jd = jd_elem.get_text(separator="\n").strip() if jd_elem else "Không thể trích xuất Job Description."
            
            jobs.append({
                "Job Title": title,
                "Company": company,
                "Salary": "Thỏa thuận",
                "Location": location,
                "URL": url,
                "Description": jd,
                "Source": self.source_name,
                "Post Date": "Mới đây"
            })
            
        return jobs