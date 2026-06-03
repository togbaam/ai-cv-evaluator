import streamlit as st
import pandas as pd
import time
from serper_client import fetch_jobs_from_serpapi
from evaluator import ATS_Evaluator

st.set_page_config(page_title="DS Job Evaluator", layout="wide", page_icon="🕵️")

if 'df_results' not in st.session_state:
    st.session_state.df_results = None

def render_sidebar():
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.markdown("Vui lòng cung cấp API Keys để sử dụng ứng dụng.")
        
        user_gemini_key = st.text_input(
            "1. Gemini API Key", 
            type="password", 
            value="", 
            placeholder="Nhập Google Gemini API Key"
        )
        
        user_serpapi_key = st.text_input(
            "2. SerpApi.com Key", 
            type="password", 
            value="", 
            placeholder="Nhập SerpApi API Key"
        )
        
        st.divider()
        st.header("📄 Upload Your CV")
        uploaded_file = st.file_uploader("Choose a .txt file", type=["txt"])
        
        cv_text = ""
        if uploaded_file is not None:
            cv_text = uploaded_file.getvalue().decode("utf-8")
            st.success("✅ CV Uploaded Successfully!")
            
        st.session_state.cv_text = cv_text
        
        # Trả về cả hai key do người dùng nhập (Không dùng biến môi trường nữa)
        return user_gemini_key.strip(), user_serpapi_key.strip()

def main():
    st.title("🚀 Google Jobs & AI Evaluator")
    st.markdown("Tìm kiếm việc làm qua Google (SerpApi) và dùng hệ thống **Gemini Auto-Fallback (2.5 Pro ➔ Lite)** để đánh giá độ phù hợp với CV.")
    
    gemini_api_key, serpapi_key = render_sidebar()
    
    c1, c2 = st.columns([3, 1])
    with c1:
        query = st.text_input("Job Title Search", value="Data Scientist")
    with c2:
        st.write("")
        st.write("")
        search_pressed = st.button("🔍 Search Jobs", width="stretch")
    
    if search_pressed:
        # Bắt lỗi nếu người dùng không nhập Key
        if not gemini_api_key or not serpapi_key:
            st.error("⚠️ Vui lòng nhập đầy đủ cả 2 API Keys (Gemini và SerpApi) ở thanh công cụ bên trái.")
            return
            
        if not st.session_state.cv_text:
            st.error("⚠️ Vui lòng tải lên file CV (.txt) của bạn trước khi tìm kiếm.")
            return
            
        with st.spinner("Đang cào dữ liệu từ Google Jobs qua SerpApi..."):
            # CHÚ Ý: Truyền serpapi_key do user nhập vào hàm
            api_response = fetch_jobs_from_serpapi(query, location="Hanoi", max_jobs=20, api_key=serpapi_key)
            
            if api_response.get("error"):
                st.error(api_response["error"])
                return
                
            all_jobs = api_response.get("jobs", [])
            
        if not all_jobs:
            st.warning("Không tìm thấy công việc nào phù hợp với từ khóa.")
            return
            
        st.success(f"Đã tìm thấy {len(all_jobs)} công việc. Đang nhờ hệ thống Gemini AI đánh giá...")
        
        evaluator = ATS_Evaluator(api_key=gemini_api_key, cv_text=st.session_state.cv_text)
        
        progress_bar = st.progress(0)
        evaluated_jobs = []
        
        for i, job in enumerate(all_jobs):
            if job.get('Source') == 'Google Organic Search':
                job['Match Score'] = 0
                job['AI Reasoning'] = "⛔ Bỏ qua đánh giá: Đây là link tổng hợp web, không có mô tả công việc (JD) cụ thể."
            else:
                res = evaluator.evaluate_job(job)
                job['Match Score'] = res.score
                job['AI Reasoning'] = res.reasoning
                
            evaluated_jobs.append(job)
            progress_bar.progress((i + 1) / len(all_jobs))
            
            if i < len(all_jobs) - 1 and job.get('Source') != 'Google Organic Search':
                time.sleep(5) 
            
        df = pd.DataFrame(evaluated_jobs)
        cols = ['Match Score', 'Job Title', 'Company', 'Location', 'Salary', 'Source', 'URL', 'Description', 'AI Reasoning']
        final_cols = [c for c in cols if c in df.columns]
        df = df[final_cols]
        
        st.session_state.df_results = df
        st.session_state.raw_jobs = evaluated_jobs

    if st.session_state.df_results is not None:
        st.subheader("📊 Evaluation Results (Smart Model Cascade)")
        
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
                    st.markdown(f"**Source:** {job.get('Source', 'N/A')}")
                    if job.get('URL') and job.get('URL') != "#":
                        st.markdown(f"[🔗 View Original Posting]({job['URL']})")
                    
                    st.divider()
                    st.markdown("**Job Description Snippet:**")
                    jd = str(job.get('Description', ''))
                    st.markdown(jd[:600] + "..." if len(jd) > 600 else jd)
                
                with c_ai:
                    st.markdown("### 🤖 AI Evaluation Reasoning")
                    st.info(job.get('AI Reasoning', 'N/A'))

if __name__ == "__main__":
    main()