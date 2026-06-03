import json
import requests
import re
import time

class JobEvaluationResult:
    def __init__(self, score: int, reasoning: str):
        self.score = score
        self.reasoning = reasoning

class ATS_Evaluator:
    def __init__(self, api_key: str, cv_text: str):
        self.cv_text = cv_text
        self.api_key = api_key
        # Danh sách model xếp hạng từ "thông minh/nặng nhất" xuống "nhẹ/nhanh nhất"
        self.model_cascade = [
            'gemini-2.5-pro',
            'gemini-2.5-flash',
            'gemini-2.0-flash',
            'gemini-2.0-flash-001',
            'gemini-2.0-flash-lite-001'
        ]
        # Bắt đầu với model xịn nhất ở vị trí số 0
        self.current_model_idx = 0

    @property
    def current_model(self):
        return self.model_cascade[self.current_model_idx]

    def evaluate_job(self, job: dict) -> JobEvaluationResult:
        # Bỏ qua nếu JD quá ngắn
        if not job.get('Description') or len(job.get('Description', '')) < 50:
            return JobEvaluationResult(score=0, reasoning="Bỏ qua do mô tả công việc (JD) quá ngắn, không đủ dữ liệu cho AI đánh giá.")

        prompt = f"""
Bạn là chuyên gia tuyển dụng ATS. Đánh giá độ phù hợp của ứng viên với công việc.

CV ứng viên:
{str(self.cv_text)[:3000]}

Công việc: {job.get('Job Title')} tại {job.get('Company')}
Mô tả: {str(job.get('Description'))[:3000]}

Đánh giá điểm phù hợp (0-100) và giải thích tiếng Việt.
Trả về định dạng JSON DUY NHẤT sau, KHÔNG THÊM BẤT KỲ VĂN BẢN NÀO KHÁC BÊN NGOÀI:
{{"score": 85, "reasoning": "Lý do..."}}
"""
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}
        }
        
        # Vòng lặp tự động hạ cấp model
        while True:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.current_model}:generateContent?key={self.api_key}"
            
            try:
                resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
                
                if resp.status_code == 200:
                    data = resp.json()
                    raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    
                    json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                    parsed = json.loads(json_match.group(0)) if json_match else json.loads(raw_text)
                        
                    # Mẹo UI: Gắn thêm tên Model vào đầu câu nhận xét để bạn biết hệ thống đang dùng model nào
                    reasoning = f"[{self.current_model}] " + str(parsed.get('reasoning', ''))
                    return JobEvaluationResult(score=int(parsed.get('score', 0)), reasoning=reasoning)
                
                elif resp.status_code == 429: # NẾU BÁO LỖI QUOTA EXCEEDED
                    # Kiểm tra xem còn model nào để hạ cấp không
                    if self.current_model_idx < len(self.model_cascade) - 1:
                        print(f"⚠️ Model '{self.current_model}' hết Quota. Đang chuyển xuống '{self.model_cascade[self.current_model_idx + 1]}'...")
                        self.current_model_idx += 1
                        time.sleep(2) # Nghỉ 2 giây để tránh bị Google chặn spam
                        continue      # Lặp lại vòng while với model mới
                    else:
                        # Đã hạ cấp đến model Lite cuối cùng mà vẫn hết Quota
                        return JobEvaluationResult(score=0, reasoning="⛔ Bỏ qua: Đã thử toàn bộ danh sách Model nhưng tài khoản của bạn đã cạn kiệt Quota hoàn toàn.")
                
                else:
                    return JobEvaluationResult(score=0, reasoning=f"Lỗi API ({self.current_model}): {resp.text}")
                    
            except Exception as e:
                return JobEvaluationResult(score=0, reasoning=f"Lỗi hệ thống ({self.current_model}): {str(e)}")