import requests

# Bổ sung tham số api_key vào hàm và xóa import os
def fetch_jobs_from_serpapi(query, location="Hanoi", max_jobs=20, api_key=""):
    if not api_key:
        return {"error": "Thiếu SerpApi Key. Vui lòng nhập ở giao diện chính."}

    url = "https://serpapi.com/search"
    formatted_jobs = []
    
    pages_to_fetch = (max_jobs // 10) + (1 if max_jobs % 10 > 0 else 0)

    for page in range(pages_to_fetch):
        start_index = page * 10
        
        params = {
            "engine": "google_jobs",
            "q": query,
            "location": f"{location}, Vietnam",
            "gl": "vn",
            "hl": "vi",
            "start": start_index,
            "api_key": api_key
        }

        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            # ... (Giữ nguyên phần xử lý JSON bên dưới của bạn) ...