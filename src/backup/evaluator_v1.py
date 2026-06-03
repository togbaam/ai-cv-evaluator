import google.generativeai as genai
from pydantic import BaseModel, Field
import json

class JobEvaluationResult(BaseModel):
    score: int = Field(description="A score from 0 to 100 indicating how well the job matches the candidate's profile.")
    reasoning: str = Field(description="A detailed explanation of why this score was given, analyzing pros and cons against the candidate profile.")

class ATS_Evaluator:
    def __init__(self, api_key: str, profile: dict):
        self.profile = profile
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    def evaluate_job(self, job: dict) -> JobEvaluationResult:
        prompt = f"""
You are an expert tech recruiter and career coach evaluating a Job Description. 
I am looking for a Data Science job. Here is my profile:

Role Interest: {self.profile['role']}
Domain Expertise: {self.profile['domain']}
Tech Stack: {self.profile['tech_stack']}
Location Preference: {self.profile['location']}
Experience: {self.profile['experience']}

Here is a job posting:
Title: {job.get('Job Title')}
Company: {job.get('Company')}
Location: {job.get('Location')}
Job Description:
{job.get('Description')}

Evaluate how well this job posting matches my profile. Calculate a percentage match score (0-100) and provide a detailed explanation of your reasoning. Focus on seniority match, domain (banking/risk modeling) match, and tech stack match.

Provide the result as a raw JSON object matching this schema:
{{
    "score": <integer 0-100>,
    "reasoning": "<string detailed explanation>"
}}
"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                )
            )
            data = json.loads(response.text)
            return JobEvaluationResult(score=data['score'], reasoning=data['reasoning'])
        except Exception as e:
            print(f"Error evaluating job {job.get('Job Title')}: {e}")
            return None
