import streamlit as st
import re
import PyPDF2
import docx
import io
import random
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def read_docx(file):
    doc = docx.Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def is_resume(text):
    text_lower = text.lower()
    keyword_count = sum(1 for keyword in resume_keywords if keyword in text_lower)
    return keyword_count >= 5  # Arbitrary threshold, adjust as needed

def get_skills(resume_text):
    all_skills = set(skill for skills in job_positions.values() for skill in skills)
    user_skills = set(skill for skill in all_skills if skill.lower() in resume_text.lower())
    return user_skills

def evaluate_eligibility(user_skills, position):
    required_skills = set(job_positions.get(position, []))
    missing_skills = required_skills - user_skills
    return len(missing_skills) == 0, list(missing_skills)

def get_suggested_courses(missing_skills):
    suggested_courses = []
    for skill in missing_skills:
        if skill in courses:
            suggested_courses.extend(courses[skill])
    return suggested_courses
# Mock database of job positions and required skills
job_positions = {
    "Software Engineer": ["Python", "JavaScript", "SQL", "Data Structures", "Algorithms"],
    "Data Scientist": ["Python", "R", "Machine Learning", "Statistics", "Big Data"],
    "Web Developer": ["HTML", "CSS", "JavaScript", "React", "Node.js"],
    "DevOps Engineer": ["Linux", "AWS", "Docker", "Kubernetes", "CI/CD"],
    "UI/UX Designer": ["Figma", "Adobe XD", "User Research", "Wireframing", "Prototyping"]
}

# Mock database of courses
courses = {
    "Python": ["Introduction to Python", "Advanced Python Programming"],
    "JavaScript": ["JavaScript Basics", "Advanced JavaScript"],
    "SQL": ["SQL Fundamentals", "Advanced Database Management"],
    "Machine Learning": ["Machine Learning Foundations", "Deep Learning Specialization"],
    "React": ["React Basics", "Advanced React and Redux"],
    "AWS": ["AWS Certified Cloud Practitioner", "AWS Solutions Architect"],
    "Docker": ["Docker Essentials", "Docker for DevOps"],
    "Figma": ["Figma UI/UX Design Essentials", "Advanced Figma Techniques"]
}

# Mock database of course sites with links
course_sites = {
    "Coursera": "https://www.coursera.org",
    "edX": "https://www.edx.org",
    "Udacity": "https://www.udacity.com",
    "Udemy": "https://www.udemy.com",
    "Pluralsight": "https://www.pluralsight.com"
}

# Common resume keywords
resume_keywords = [
    "experience", "education", "skills", "projects", "achievements", "work history",
    "job", "employment", "qualifications", "references", "objective", "summary",
    "contact", "phone", "email", "address", "linkedin", "github"
]

# Function definitions (is_resume, get_skills, evaluate_eligibility, get_suggested_courses, read_pdf, read_docx) remain the same

def plot_skill_match(user_skills, required_skills):
    skills = list(set(user_skills) | set(required_skills))
    user = [1 if skill in user_skills else 0 for skill in skills]
    required = [1 if skill in required_skills else 0 for skill in skills]
    
    fig, ax = plt.subplots(figsize=(10, 5))
    x = range(len(skills))
    width = 0.35
    
    ax.bar([i - width/2 for i in x], user, width, label='Your Skills', color='#3498db')
    ax.bar([i + width/2 for i in x], required, width, label='Required Skills', color='#e74c3c')
    
    ax.set_ylabel('Presence')
    ax.set_title('Your Skills vs. Required Skills')
    ax.set_xticks(x)
    ax.set_xticklabels(skills, rotation=45, ha='right')
    ax.legend()
    
    plt.tight_layout()
    return fig

def generate_report(user_skills, position, is_eligible, missing_skills, suggested_courses):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    eligibility = "Eligible" if is_eligible else "Not Eligible"
    skills_str = ", ".join(user_skills)
    required_skills_str = ", ".join(job_positions[position])
    
    report = [
        "Skill Assessment Report",
        f"Generated on: {now}",
        "",
        f"Position: {position}",
        f"Eligibility: {eligibility}",
        "",
        f"Your Skills: {skills_str}",
        f"Required Skills: {required_skills_str}",
        ""
    ]
    
    if is_eligible:
        report.append("Congratulations! You meet all the requirements for this position.")
    else:
        report.append("Skills to Improve:")
        report.extend([f"- {skill}" for skill in missing_skills])
        report.append("")
        report.append("Suggested Courses:")
        report.extend([f"- {course}" for course in suggested_courses])
        report.append("")
        report.append("Recommended Learning Platforms:")
        report.extend([f"- {site}" for site in course_sites.keys()])
    
    return "\n".join(report)


# Streamlit app
st.set_page_config(page_title="Career Compass: Skill Assessment & Upskilling Guide", page_icon="🧭", layout="wide")

st.title("Career Compass: Skill Assessment & Upskilling Guide")

st.sidebar.header("About")
st.sidebar.info(
    "Career Compass is your personal guide to navigating the job market. "
    "Upload your resume, select a target position, and get instant feedback on your eligibility. "
    "Receive tailored recommendations for upskilling and advancing your career."
)

st.sidebar.header("Instructions")
st.sidebar.markdown(
    "1. Upload your resume (PDF, DOCX, or TXT)\n"
    "2. Select your target job position\n"
    "3. Click 'Analyze Resume & Get Insights'\n"
    "4. Review your personalized assessment and recommendations"
)

uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "docx", "txt"])
position = st.selectbox("Select target job position", options=list(job_positions.keys()))

if uploaded_file is not None and position:
    if st.button("Analyze Resume & Get Insights"):
        try:
            if uploaded_file.type == "application/pdf":
                resume_text = read_pdf(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                resume_text = read_docx(uploaded_file)
            else:
                resume_text = uploaded_file.getvalue().decode("utf-8")

            if not is_resume(resume_text):
                st.error("The uploaded document does not appear to be a resume. Please upload a valid resume.")
            else:
                user_skills = get_skills(resume_text)
                is_eligible, missing_skills = evaluate_eligibility(user_skills, position)

                st.header("Assessment Results")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if is_eligible:
                        st.success(f"Congratulations! You meet the requirements for the {position} position.")
                    else:
                        st.warning(f"Your resume doesn't fully meet the requirements for the {position} position.")
                    
                    st.subheader("Your Skills")
                    st.write(", ".join(user_skills))
                    
                    st.subheader("Required Skills")
                    st.write(", ".join(job_positions[position]))
                
                with col2:
                    st.pyplot(plot_skill_match(user_skills, job_positions[position]))

                if not is_eligible:
                    st.header("Upskilling Recommendations")
                    
                    st.subheader("Skills to Improve")
                    for skill in missing_skills:
                        st.write(f"- {skill}")
                    
                    suggested_courses = get_suggested_courses(missing_skills)
                    st.subheader("Suggested Courses")
                    for course in suggested_courses:
                        st.write(f"- {course}")

                    st.subheader("Recommended Learning Platforms")
                    cols = st.columns(len(course_sites))
                    for i, (site, url) in enumerate(course_sites.items()):
                        cols[i].button(site, key=site, on_click=lambda u=url: st.markdown(f'<a href="{u}" target="_blank">{u}</a>', unsafe_allow_html=True))

                st.header("Download Full Report")
                report = generate_report(user_skills, position, is_eligible, missing_skills, suggested_courses)
                st.download_button(
                    label="Download PDF Report",
                    data=report,
                    file_name=f"skill_assessment_report_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )

        except Exception as e:
            st.error(f"An error occurred while processing the file: {str(e)}")

st.markdown("---")
st.markdown("© 2024 Career Compass. All rights reserved.")