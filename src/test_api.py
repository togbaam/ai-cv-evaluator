import os
import requests
import json
from dotenv import load_dotenv

# 1. Tải biến môi trường từ file .env
load_dotenv()

# 2. Lấy API Key
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("❌ LỖI: Không tìm thấy GEMINI_API_KEY trong file .env!")
    print("Hãy chắc chắn bạn đã tạo file .env và đặt tên biến là GEMINI_API_KEY.")
    exit()

print(f"✅ Đã tìm thấy API Key: {API_KEY[:5]}...{API_KEY[-5:]}\n")

def test_connection():
    """Hàm này sẽ hỏi Google xem API Key này có quyền dùng những model nào"""
    print("🔍 Đang kết nối tới Google AI để kiểm tra Model...")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        models = response.json().get('models', [])
        print(f"✅ THÀNH CÔNG! Tài khoản của bạn hỗ trợ {len(models)} models.")
        
        # Lọc ra các model có thể tạo văn bản (generateContent)
        text_models = [m['name'].split('/')[-1] for m in models if 'generateContent' in m.get('supportedGenerationMethods', [])]
        print(f"👉 Các model AI bạn có thể dùng: {text_models[:5]}...\n")
        
        # Chọn model đầu tiên tìm được để test (thường là gemini-1.5-flash hoặc gemini-pro)
        return text_models[0] if text_models else None
    else:
        print(f"❌ LỖI API KEY ({response.status_code}):\n{response.text}\n")
        return None

def test_chat(model_name):
    """Hàm này thử gửi 1 câu hỏi ngắn cho AI để xem nó có trả lời không"""
    print(f"🤖 Đang thử trò chuyện với model [{model_name}]...")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": "Xin chào, bạn có hoạt động không? Trả lời ngắn gọn trong 1 câu."}]}]
    }
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        reply = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        print(f"✅ AI TRẢ LỜI: {reply}")
    else:
        print(f"❌ LỖI GỌI AI ({response.status_code}):\n{response.text}")

if __name__ == "__main__":
    print("-" * 50)
    # Kiểm tra danh sách model
    model_to_test = test_connection()
    
    # Nếu API Key đúng và có model, thử chat
    if model_to_test:
        test_chat(model_to_test)
    print("-" * 50)

# ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-2.0-flash', 'gemini-2.0-flash-001', 'gemini-2.0-flash-lite-001']