import os
import requests
import json
from dotenv import load_dotenv

# Tải file .env
load_dotenv()

API_KEY = os.getenv("SERPER_API_KEY")

if not API_KEY:
    print("❌ LỖI: Không tìm thấy SERPER_API_KEY trong file .env!")
    exit()

print(f"✅ Đã tìm thấy Serper API Key: {API_KEY[:5]}...{API_KEY[-5:]}\n")

def test_serper(query="Data Scientist", location="Hà Nội"):
    url = "https://google.serper.dev/search"
    
    # Mẹo nhỏ: Chuyển sang tiếng Việt thường dễ kích hoạt Google Jobs ở VN hơn
    search_query = f"Tuyển dụng {query} tại {location}"
    
    payload = {
        "q": search_query,
        "gl": "vn", # Quốc gia: Việt Nam
        "hl": "vi"  # Ngôn ngữ: Tiếng Việt
    }
    headers = {
        'X-API-KEY': API_KEY,
        'Content-Type': 'application/json'
    }

    print(f"🔍 Đang gửi request: '{search_query}'...")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"📡 HTTP Status Code: {response.status_code}\n")
        
        if response.status_code == 200:
            data = response.json()
            print("📦 NỘI DUNG JSON TRẢ VỀ:")
            
            # In ra các key chính để xem Google trả về những khối dữ liệu nào
            keys = list(data.keys())
            print(f"Các khối dữ liệu thu được: {keys}")
            
            if 'jobs' in data:
                print(f"\n✅ TUYỆT VỜI! Tìm thấy widget 'jobs' với {len(data['jobs'])} công việc.")
                print(f"👉 Công việc đầu tiên: {data['jobs'][0].get('title')} tại {data['jobs'][0].get('company_name')}")
            else:
                print("\n⚠️ KHÔNG TÌM THẤY TRƯỜNG 'jobs'. Google không kích hoạt Widget việc làm.")
                if 'organic' in data:
                    print(f"👉 Thay vào đó, tìm thấy {len(data['organic'])} kết quả web 'organic'.")
            
            # Xuất toàn bộ JSON ra file để bạn có thể mở lên xem chi tiết cấu trúc
            with open("serper_debug.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("\n📂 Đã lưu toàn bộ kết quả chi tiết vào file 'serper_debug.json'. Hãy mở file này ra xem!")
            
        else:
            print(f"❌ LỖI API ({response.status_code}): {response.text}")
            
    except Exception as e:
        print(f"❌ Lỗi hệ thống: {e}")

if __name__ == "__main__":
    test_serper()