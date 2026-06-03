# AI CV Evaluator & Job Finder

Một ứng dụng web thông minh giúp tự động tìm kiếm các công việc phù hợp nhất trên Google Jobs và sử dụng Trí tuệ Nhân tạo (Google Gemini) để chấm điểm mức độ phù hợp giữa CV của bạn và Mô tả công việc (JD).

## Tính năng nổi bật

* **Tìm kiếm việc làm Real-time:** Tích hợp `SerpApi` (Engine: Google Jobs) để lấy dữ liệu việc làm thực tế, vượt qua các rào cản chống Bot (Anti-bot/CAPTCHA) của các trang web tuyển dụng thông thường.
* **Đánh giá CV bằng AI:** Sử dụng mô hình **Google Gemini** để đọc CV (định dạng text) và đối chiếu với từng Job Description, từ đó đưa ra điểm số phù hợp (%) và lời giải thích chi tiết.
* **Cơ chế Smart Model Cascade (Auto-Fallback):** Hệ thống tự động hạ cấp mô hình AI (từ `gemini-2.5-pro` xuống các bản `flash` hoặc `lite`) nếu tài khoản gặp lỗi giới hạn Quota (Lỗi 429), đảm bảo ứng dụng luôn chạy mượt mà không bị gián đoạn.
* **Giao diện trực quan:** Xây dựng bằng `Streamlit` với bảng xếp hạng màu sắc, thanh tiến trình (Progress bar) và các thẻ chi tiết công việc có thể mở rộng.

## Công nghệ sử dụng

* **Ngôn ngữ:** Python 3.x
* **Giao diện Web:** Streamlit, Pandas
* **API Việc làm:** SerpApi (Google Jobs Engine)
* **Trí tuệ nhân tạo:** Google Gemini API (Google AI Studio)

## Hướng dẫn cài đặt

**Bước 1: Clone dự án về máy**
```bash
git clone [https://github.com/togbaam/ai-cv-evaluator.git](https://github.com/togbaam/ai-cv-evaluator.git)
cd ai-cv-evaluator