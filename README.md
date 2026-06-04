# 🚀 AI CV Evaluator & Job Finder

Một ứng dụng web thông minh giúp tự động tìm kiếm các công việc phù hợp nhất trên Google Jobs và sử dụng Trí tuệ Nhân tạo (Google Gemini) để chấm điểm mức độ phù hợp giữa CV của bạn và Mô tả công việc (JD).

---

## ✨ Tính năng nổi bật

* **Tìm kiếm việc làm Real-time:** Tích hợp `SerpApi` (Engine: Google Jobs) để lấy dữ liệu việc làm thực tế, vượt qua các rào cản chống Bot (Anti-bot/CAPTCHA) của các trang web tuyển dụng thông thường.
* **Đánh giá CV bằng AI:** Sử dụng mô hình **Google Gemini** để đọc CV (định dạng text) và đối chiếu với từng Job Description, từ đó đưa ra điểm số phù hợp (%) và lời giải thích chi tiết.
* **Cơ chế Smart Model Cascade (Auto-Fallback):** Hệ thống tự động hạ cấp mô hình AI (từ `gemini-2.5-pro` xuống các bản `flash` hoặc `lite`) nếu tài khoản gặp lỗi giới hạn Quota (Lỗi 429), đảm bảo ứng dụng luôn chạy mượt mà không bị gián đoạn.
* **Giao diện trực quan:** Xây dựng bằng `Streamlit` với bảng xếp hạng màu sắc, thanh tiến trình (Progress bar) và các thẻ chi tiết công việc có thể mở rộng.

---

## 🛠️ Công nghệ sử dụng

* **Ngôn ngữ:** Python 3.x
* **Giao diện Web:** Streamlit, Pandas
* **API Việc làm:** SerpApi (Google Jobs Engine)
* **Trí tuệ nhân tạo:** Google Gemini API (Google AI Studio)

---

## 🔑 Hướng dẫn lấy API Key (Dành cho người mới)

Để ứng dụng này có thể đi cào dữ liệu và nhờ AI chấm điểm, bạn cần trang bị cho nó 2 chiếc "chìa khóa" (API Key) hoàn toàn miễn phí.

### 1. Lấy Google Gemini API Key (Bộ não AI)
* **Truy cập link:** [Google AI Studio - API Keys](https://aistudio.google.com/app/apikey)
* Đăng nhập bằng tài khoản Google của bạn.
* Bấm nút **Create API Key** (màu xanh) > Chọn **Create API key in new project**.
* Copy chuỗi mã loằng ngoằng vừa hiện ra và lưu tạm ra một file Text/Notepad.

### 2. Lấy SerpApi Key (Động cơ tìm việc)
* **Truy cập link:** [SerpApi.com](https://serpapi.com/)
* Bấm **Register** để tạo tài khoản mới (Bạn có thể chọn đăng nhập nhanh bằng Google hoặc GitHub).
* Sau khi đăng nhập, hệ thống sẽ đưa bạn vào trang Dashboard (Bảng điều khiển). 
* Nhìn sang bên phải, bạn sẽ thấy mục **Your Private API Key**. Hãy copy chuỗi mã đó và lưu lại.

---

## 💻 Hướng dẫn Cài đặt & Chạy ứng dụng

**⚠️ Yêu cầu bắt buộc:** Máy tính của bạn phải được cài đặt sẵn **Python** (phiên bản 3.9 trở lên). Nếu chưa có, hãy tải tại [python.org/downloads](https://www.python.org/downloads/) (Nhớ tích vào ô *Add Python.exe to PATH* khi cài đặt nhé).

**Bước 1: Tải mã nguồn về máy** Mở ứng dụng **Terminal** (trên Mac) hoặc **Command Prompt / PowerShell** (trên Windows) và gõ lệnh sau:
```bash
git clone [https://github.com/togbaam/ai-cv-evaluator.git](https://github.com/togbaam/ai-cv-evaluator.git)
cd ai-cv-evaluator

**Bước 2: Cài đặt các công cụ hỗ trợ** Ứng dụng cần một số thư viện để chạy (như khung giao diện, công cụ kết nối web). Hãy yêu cầu Python tải chúng về bằng lệnh sau:
```bash
pip install -r requirements.txt

**Bước 3: Khởi động ứng dụng** Sau khi chạy xong bước 2, bạn gõ lệnh cuối cùng này để đánh thức ứng dụng:
```bash
streamlit run app.py




