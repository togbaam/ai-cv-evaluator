import requests
import os

def fetch_jobs_from_serpapi(query, location="Hanoi", max_jobs=20):
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return {"error": "Thiếu SERPAPI_API_KEY trong file .env."}

    url = "https://serpapi.com/search"
    formatted_jobs = []
    
    # Tính toán số trang cần gọi (Mỗi trang có 10 kết quả)
    pages_to_fetch = (max_jobs // 10) + (1 if max_jobs % 10 > 0 else 0)

    for page in range(pages_to_fetch):
        # Tính toán điểm bắt đầu (0, 10, 20...)
        start_index = page * 10
        
        params = {
            "engine": "google_jobs",
            "q": query,
            "location": f"{location}, Vietnam",
            "gl": "vn",
            "hl": "vi",
            "start": start_index, # Bí kíp nhảy trang nằm ở đây
            "api_key": api_key
        }

        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            jobs = data.get("jobs_results", [])
            if not jobs:
                break # Hết kết quả (Đã cào đến trang cuối cùng)
            
            for j in jobs:
                if len(formatted_jobs) >= max_jobs:
                    break # Dừng nếu đã thu thập đủ số lượng yêu cầu
                    
                formatted_jobs.append({
                    "Job Title": j.get('title', 'Unknown Title'),
                    "Company": j.get('company_name', 'Unknown Company'),
                    "Location": j.get('location', location),
                    "Salary": "Thỏa thuận",
                    "Source": j.get('via', 'Google Jobs'),
                    "URL": j.get('share_link', '#'),
                    "Description": j.get('description', 'Không có mô tả chi tiết.')
                })
                
        except requests.exceptions.RequestException as e:
            return {"error": f"Lỗi kết nối SerpApi ở trang {page + 1}: {str(e)}"}

    if not formatted_jobs:
         return {"error": f"Không tìm thấy công việc nào cho '{query}' tại '{location}'."}

    return {"error": None, "jobs": formatted_jobs}