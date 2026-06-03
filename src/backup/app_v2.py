import streamlit as st
import asyncio
import pandas as pd
from scrapers import ITViecScraper, TopCVScraper
from evaluator import ATS_Evaluator
import os
from dotenv import load_dotenv
import time

# Load env variables
load_dotenv()

st.set_page_config(page_title="DS Job Evaluator", layout="wide", page_icon="🕵️")

if 'df_results' not in st.session_state:
    st.session_state.df_results = None

def render_sidebar():
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # 1. Ô nhập liệu luôn để trống (value=""), chỉ dùng placeholder để hướng dẫn
        user_api_key = st.text_input(
            "Gemini API Key của bạn", 
            type="password", 
            value="", 
            placeholder="Để trống để dùng API Key mặc định của hệ thống"
        )
        
        st.divider()
        st.header("📄 Upload Your CV")
        uploaded_file = st.file_uploader("Choose a .txt file", type=["txt"])
        
        cv_text = ""
        if uploaded_file is not None:
            cv_text = uploaded_file.getvalue().decode("utf-8")
            st.success("✅ CV Uploaded Successfully!")
            
        st.session_state.cv_text = cv_text
        
        # 2. Logic xử lý ẩn (Fallback) chỉ chạy ở Backend
        if user_api_key.strip():
            # Nếu người dùng tự điền, ưu tiên dùng key của họ
            final_api_key = user_api_key.strip()
            st.info("🔑 Đang sử dụng API Key của bạn.")
        else:
            # Nếu người dùng bỏ trống, hệ thống tự lấy key ẩn từ file .env hoặc Secrets
            # Đoạn này thay thế linh hoạt giữa os.getenv và st.secrets
            final_api_key = os.getenv("GEMINI_API_KEY", "")
            
            if final_api_key:
                st.write("🔒 Đang sử dụng API Key mặc định (Đã được bảo mật).")
            else:
                st.error("⚠️ Hệ thống chưa được cấu hình API Key mặc định. Vui lòng tự điền key của bạn.")
        
        st.session_state.google_api_key = final_api_key
        return final_api_key

def main():
    st.title("🚀 Data Science Job Finder & Evaluator")
    st.markdown("Tìm kiếm việc làm từ ITviec & TopCV, sau đó dùng AI đánh giá độ phù hợp với CV của bạn.")
    
    api_key = render_sidebar()
    
    c1, c2 = st.columns([3, 1])
    with c1:
        query = st.text_input("Job Title Search", value="Data Scientist")
    with c2:
        st.write("")
        st.write("")
        search_pressed = st.button("🔍 Search Jobs", width="stretch")
    
    if search_pressed:
        if not api_key:
            st.error("Vui lòng nhập Gemini API Key ở thanh công cụ bên trái.")
            return
            
        if not st.session_state.cv_text:
            st.error("Vui lòng tải lên file CV (.txt) của bạn trước khi tìm kiếm.")
            return
            
        with st.spinner("Đang cào dữ liệu từ ITviec và TopCV... Chờ chút nhé!"):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            itviec = ITViecScraper()
            topcv = TopCVScraper()
            
            st.toast("Fetching jobs from ITviec...")
            itviec_jobs = loop.run_until_complete(itviec.scrape_jobs(query, max_jobs=5))
            
            st.toast("Fetching jobs from TopCV...")
            topcv_jobs = loop.run_until_complete(topcv.scrape_jobs(query, max_jobs=5))
            
            all_jobs = itviec_jobs + topcv_jobs
            
        if not all_jobs:
            st.warning("Không tìm thấy công việc nào phù hợp với từ khóa.")
            return
            
        st.success(f"Đã tìm thấy {len(all_jobs)} công việc. Đang nhờ Gemini đánh giá...")
        
        # Đưa cv_text nguyên bản vào Evaluator thay vì dictionary profile
        evaluator = ATS_Evaluator(api_key=api_key, cv_text=st.session_state.cv_text)
        
        progress_bar = st.progress(0)
        evaluated_jobs = []
        for i, job in enumerate(all_jobs):
            res = evaluator.evaluate_job(job)
            if res:
                job['Match Score'] = res.score
                job['AI Reasoning'] = res.reasoning
            else:
                job['Match Score'] = 0
                job['AI Reasoning'] = "Lỗi không xác định."
                
            evaluated_jobs.append(job)
            progress_bar.progress((i + 1) / len(all_jobs))
            
            # QUAN TRỌNG: Bắt buộc nghỉ 4 giây giữa mỗi Job để tránh lỗi 429 Rate Limit
            if i < len(all_jobs) - 1:
                time.sleep(4)
            
        df = pd.DataFrame(evaluated_jobs)
        
        # CHỈNH SỬA Ở ĐÂY: Đưa 'Description' vào danh sách hiển thị và xuất file
        cols = ['Match Score', 'Job Title', 'Company', 'Location', 'Salary', 'Source', 'URL', 'Description', 'AI Reasoning']
        final_cols = [c for c in cols if c in df.columns]
        df = df[final_cols]
        
        st.session_state.df_results = df
        st.session_state.raw_jobs = evaluated_jobs

    # Render results
    if st.session_state.df_results is not None:
        st.subheader("📊 Evaluation Results")
        
        df = st.session_state.df_results.sort_values(by="Match Score", ascending=False).reset_index(drop=True)
        st.dataframe(
            df.style.background_gradient(subset=['Match Score'], cmap='viridis', vmin=0, vmax=100)
            .format({'Match Score': "{:.0f}%"}),
            width="stretch",
            height=300
        )
        
        st.subheader("🔍 Detailed Breakdown")
        sorted_jobs = sorted(st.session_state.raw_jobs, key=lambda x: x.get('Match Score', 0), reverse=True)
        
        for job in sorted_jobs:
            with st.expander(f"{job.get('Match Score', 0)}% - {job.get('Job Title', 'Unknown Title')} @ {job.get('Company', 'Unknown Company')}"):
                c_info, c_ai = st.columns([1, 2])
                with c_info:
                    st.markdown(f"**Location:** {job.get('Location', 'N/A')}")
                    st.markdown(f"**Salary:** {job.get('Salary', 'N/A')}")
                    st.markdown(f"**Source:** {job.get('Source', 'N/A')}")
                    if job.get('URL'):
                        st.markdown(f"[View Original Posting]({job['URL']})")
                    
                    st.divider()
                    st.markdown("**Job Description Snippet:**")
                    jd = str(job.get('Description', ''))
                    st.markdown(jd[:600] + "..." if len(jd) > 600 else jd)
                
                with c_ai:
                    st.markdown("### 🤖 AI Evaluation Reasoning")
                    st.info(job.get('AI Reasoning', 'N/A'))

if __name__ == "__main__":
    main()
