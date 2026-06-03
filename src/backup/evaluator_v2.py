import json
import requests
import re

class JobEvaluationResult:
    def __init__(self, score: int, reasoning: str):
        self.score = score
        self.reasoning = reasoning

class ATS_Evaluator:
    def __init__(self, api_key: str, cv_text: str):
        self.cv_text = cv_text
        self.api_key = api_key
        self.best_model = None

    def get_best_model(self):
        """Tự động hỏi Google xem API Key này hỗ trợ Model nào, không bao giờ lo chết API."""
        if self.best_model: 
            return self.best_model
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={self.api_key}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                models = resp.json().get('models', [])
                supported = [m['name'] for m in models if 'generateContent' in m.get('supportedGenerationMethods', [])]
                
                # Ưu tiên tìm các model xịn và mới nhất
                for keyword in ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash']:
                    for m in supported:
                        if keyword in m:
                            self.best_model = m.split('/')[-1]
                            return self.best_model
                            
                # Fallback: Lấy model đầu tiên tìm thấy
                if supported:
                    self.best_model = supported[0].split('/')[-1]
                    return self.best_model
        except Exception:
            pass
            
        # Fallback cuối cùng
        self.best_model = "gemini-1.5-flash"
        return self.best_model

    def evaluate_job(self, job: dict) -> JobEvaluationResult:
        if "Không thể trích xuất" in str(job.get('Description', '')) or not job.get('Description'):
            return JobEvaluationResult(score=0, reasoning="Bỏ qua do website chặn bot lấy mô tả công việc (JD).")

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
        model = self.get_best_model()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1}
        }
        
        try:
            resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                
                # Cứu hộ JSON thông minh bằng Regex
                json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(0))
                else:
                    parsed = json.loads(raw_text)
                    
                return JobEvaluationResult(
                    score=int(parsed.get('score', 0)), 
                    reasoning=str(parsed.get('reasoning', ''))
                )
            else:
                return JobEvaluationResult(score=0, reasoning=f"Lỗi gọi API (Dùng model {model}): {resp.text}")
        except Exception as e:
            return JobEvaluationResult(score=0, reasoning=f"Lỗi hệ thống khi phân tích JSON: {str(e)}")