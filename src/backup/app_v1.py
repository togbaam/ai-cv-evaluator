import streamlit as st
import asyncio
import pandas as pd
from scrapers import ITViecScraper, TopCVScraper
from evaluator import ATS_Evaluator
import os
from dotenv import load_dotenv

# Load env variables
load_dotenv()

st.set_page_config(page_title="DS Job Evaluator", layout="wide", page_icon="🕵️")

# Initialize session state for results if they don't exist
if 'df_results' not in st.session_state:
    st.session_state.df_results = None

def render_sidebar():
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Keys
        google_api_key = st.text_input("Gemini API Key", type="password", value=os.getenv("GEMINI_API_KEY", ""))
        
        st.divider()
        st.header("👤 Your Profile (ATS Focus)")
        
        # Profile Configuration
        role = st.text_input("Role", value="Lead Data Scientist")
        domain = st.text_area("Domain Expertise", value="Risk Modeling, Credit Scoring (A-score, B-score, C-score), Fraud Models, and Early Warning Systems (EWS) for consumer finance.", height=150)
        tech_stack = st.text_area("Tech Stack", value="Python, Machine Learning (XGBoost, Decision Trees), Model Validation (Gini, KS, PSI).", height=100)
        location = st.text_input("Location", value="Hanoi")
        experience = st.text_area("Experience", value="Managing a team of 4-5 people at a major bank. Prioritize Lead or Senior roles.", height=100)
        
        st.session_state.profile = {
            "role": role,
            "domain": domain,
            "tech_stack": tech_stack,
            "location": location,
            "experience": experience
        }
        
        st.session_state.google_api_key = google_api_key
        return st.session_state.google_api_key

def main():
    st.title("🚀 Data Science Job Finder & Evaluator")
    st.markdown("Search ITviec and TopCV for job postings and evaluate them against your profile using AI.")
    
    api_key = render_sidebar()
    
    # Search Query
    c1, c2 = st.columns([3, 1])
    with c1:
        query = st.text_input("Job Title Search", value="Data Scientist")
    with c2:
        st.write("")
        st.write("")
        search_pressed = st.button("🔍 Search Jobs", use_container_width=True)
    
    if search_pressed:
        if not api_key:
            st.error("Please provide a Gemini API Key in the sidebar.")
            return
            
        with st.spinner("Scraping jobs from ITviec and TopCV... This may take a minute due to anti-bot evasions."):
            # Create a new event loop for Playwright async execution
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            itviec = ITViecScraper()
            topcv = TopCVScraper()
            
            # Fetch up to 5 jobs from each source to roughly hit the top 10 relevant limit
            st.toast("Fetching jobs from ITviec...")
            itviec_jobs = loop.run_until_complete(itviec.scrape_jobs(query, max_jobs=5))
            
            st.toast("Fetching jobs from TopCV...")
            topcv_jobs = loop.run_until_complete(topcv.scrape_jobs(query, max_jobs=5))
            
            all_jobs = itviec_jobs + topcv_jobs
            
        if not all_jobs:
            st.warning("No jobs found for the specified query.")
            return
            
        st.success(f"Found {len(all_jobs)} jobs. Beginning LLM evaluation...")
        
        # Evaluate jobs
        evaluator = ATS_Evaluator(api_key=api_key, profile=st.session_state.profile)
        
        progress_bar = st.progress(0)
        evaluated_jobs = []
        for i, job in enumerate(all_jobs):
            res = evaluator.evaluate_job(job)
            if res:
                job['Match Score'] = res.score
                job['AI Reasoning'] = res.reasoning
            else:
                job['Match Score'] = 0
                job['AI Reasoning'] = "Failed to evaluate."
            evaluated_jobs.append(job)
            progress_bar.progress((i + 1) / len(all_jobs))
            
        # Store in session state to display
        df = pd.DataFrame(evaluated_jobs)
        cols = ['Match Score', 'Job Title', 'Company', 'Salary', 'Location', 'Source', 'Post Date', 'URL']
        cols = [c for c in cols if c in df.columns]
        df = df[cols + [c for c in df.columns if c not in cols and c not in ['Description', 'AI Reasoning']]]
        st.session_state.df_results = df
        st.session_state.raw_jobs = evaluated_jobs

    # Render results
    if st.session_state.df_results is not None:
        st.subheader("📊 Evaluation Results")
        
        df = st.session_state.df_results.sort_values(by="Match Score", ascending=False).reset_index(drop=True)
        st.dataframe(
            df.style.background_gradient(subset=['Match Score'], cmap='viridis', vmin=0, vmax=100)
            .format({'Match Score': "{:.0f}%"}),
            use_container_width=True,
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
