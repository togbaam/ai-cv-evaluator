import os
import requests
import json
from dotenv import load_dotenv

# Tải biến môi trường từ file .env
load_dotenv()

API_KEY = os.getenv("SERPAPI_API_KEY")

if not API_KEY:
    print("❌ LỖI: Không tìm thấy SERPAPI_API_KEY trong file .env!")
    print("Hãy chắc chắn bạn đã thêm SERPAPI_API_KEY=your_key vào file .env")
    exit()

print(f"✅ Đã tìm thấy SerpApi Key: {API_KEY[:5]}...{API_KEY[-5:]}\n")

def test_serpapi_google_jobs(query="Data Scientist Hanoi"):
    # Endpoint chung của SerpApi
    url = "https://serpapi.com/search"
    
    # Ép dùng engine google_jobs và KHAI BÁO RÕ ĐỊA ĐIỂM
    params = {
        "engine": "google_jobs",
        "q": "Data Scientist",       # Chỉ để tên công việc ở đây
        "location": "Hanoi, Vietnam", # Định vị tọa độ chính xác
        "gl": "vn",                   # Giới hạn trong lãnh thổ Việt Nam
        "hl": "vi",                   # Ngôn ngữ Tiếng Việt
        "api_key": API_KEY
    }

    print(f"🔍 Đang gọi SerpApi với engine 'google_jobs' cho từ khóa: '{query}'...")
    
    try:
        # SerpApi hỗ trợ cả GET request rất tiện lợi
        response = requests.get(url, params=params, timeout=15)
        print(f"📡 HTTP Status Code: {response.status_code}\n")
        
        if response.status_code == 200:
            data = response.json()
            
            # Xuất toàn bộ JSON ra file để bạn check cấu trúc
            with open("serpapi_jobs_debug.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Khối dữ liệu việc làm của SerpApi nằm trong 'jobs_results'
            jobs = data.get("jobs_results", [])
            
            if jobs:
                print(f"🎉 THÀNH CÔNG RỰC RỠ! Tìm thấy {len(jobs)} công việc thực tế.")
                print("-" * 40)
                
                # Lấy thử job đầu tiên để xem độ chi tiết của JD
                first_job = jobs[0]
                print(f"📌 Job đầu tiên:")
                print(f"  - Tiêu đề: {first_job.get('title')}")
                print(f"  - Công ty: {first_job.get('company_name')}")
                print(f"  - Địa điểm: {first_job.get('location')}")
                
                jd = first_job.get('description', '')
                print(f"  - Độ dài mô tả (JD): {len(jd)} ký tự.")
                print(f"  - Bản xem trước JD:\n{jd[:300]}...")
                print("-" * 40)
            else:
                print("⚠️ Kết quả trả về thành công nhưng mảng 'jobs_results' bị trống.")
                
            print("\n📂 Đã lưu cấu trúc JSON chi tiết vào file 'serpapi_jobs_debug.json'.")
            
        else:
            print(f"❌ LỖI API ({response.status_code}): {response.text}")
            
    except Exception as e:
        print(f"❌ Lỗi hệ thống: {e}")

if __name__ == "__main__":
    test_serpapi_google_jobs()