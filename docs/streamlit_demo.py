"""
NextFitAI Resume Analyzer - Streamlit Demo
A complete working Streamlit application for resume analysis using the NextFitAI API.

To run this app:
1. Install dependencies: pip install streamlit requests
2. Run the app: streamlit run streamlit_demo.py
"""

import streamlit as st
import requests
import uuid
import time
import json
from datetime import datetime

# API Configuration
API_BASE_URL = "https://febwc3ocqb.execute-api.us-east-1.amazonaws.com/prod"

# Configure Streamlit page
st.set_page_config(
    page_title="NextFitAI Resume Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #007bff;
    }
    .skill-tag {
        background-color: #dc3545;
        color: white;
        padding: 4px 8px;
        margin: 2px;
        border-radius: 12px;
        font-size: 12px;
        display: inline-block;
    }
    .recommendation-item {
        background: #e8f5e8;
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 5px;
        border-left: 3px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

# API Functions
@st.cache_data(ttl=300)  # Cache for 5 minutes
def check_system_health():
    """Check API system health with caching"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}

def submit_analysis(resume_text, job_description):
    """Submit resume analysis to API"""
    analysis_id = str(uuid.uuid4())
    
    payload = {
        "analysis_id": analysis_id,
        "resume_text": resume_text,
        "job_description": job_description
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/analyze",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        if response.status_code == 202:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
            
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}

def get_analysis_results(analysis_id):
    """Get analysis results from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/results/{analysis_id}", timeout=10)
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        elif response.status_code == 404:
            return {"success": False, "error": "Analysis not found"}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
            
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}

def poll_for_results(analysis_id, max_attempts=30, interval=2):
    """Poll for analysis results with progress tracking"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for attempt in range(max_attempts):
        progress = (attempt + 1) / max_attempts
        progress_bar.progress(progress)
        status_text.text(f"🔄 Analyzing... Attempt {attempt + 1}/{max_attempts}")
        
        result = get_analysis_results(analysis_id)
        
        if result["success"]:
            data = result["data"]
            
            if data["status"] == "completed":
                progress_bar.progress(1.0)
                status_text.text("✅ Analysis completed!")
                time.sleep(1)  # Brief pause to show completion
                progress_bar.empty()
                status_text.empty()
                return {"success": True, "data": data}
            elif data["status"] == "failed":
                progress_bar.empty()
                status_text.empty()
                return {"success": False, "error": data.get("error", "Analysis failed")}
            # Continue polling if status is "processing"
        else:
            progress_bar.empty()
            status_text.empty()
            return result
        
        if attempt < max_attempts - 1:
            time.sleep(interval)
    
    progress_bar.empty()
    status_text.empty()
    return {"success": False, "error": "Analysis timeout - please try again"}

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_sample_data():
    """Get sample resume and job description data"""
    return {
        "sample_resume": """John Doe
Software Engineer

EXPERIENCE
==========
Senior Software Developer | TechCorp Inc. | 2020-Present
• Led development of microservices architecture serving 1M+ users
• Improved application performance by 40% through code optimization
• Mentored team of 3 junior developers
• Technologies: Python, React, AWS, Docker, PostgreSQL

Software Developer | StartupXYZ | 2018-2020
• Built full-stack web applications using modern frameworks
• Implemented CI/CD pipelines reducing deployment time by 60%
• Collaborated with cross-functional teams in agile environment
• Technologies: JavaScript, Node.js, MongoDB, Git

SKILLS
======
• Programming: Python, JavaScript, Java, SQL
• Frameworks: React, Node.js, Express, Django
• Cloud: AWS (EC2, S3, Lambda, RDS), Docker, Kubernetes
• Databases: PostgreSQL, MongoDB, Redis
• Tools: Git, Jenkins, JIRA, Terraform

EDUCATION
=========
• Bachelor of Science in Computer Science | State University | 2018
• AWS Certified Solutions Architect - Associate
• Certified Kubernetes Administrator (CKA)

ACHIEVEMENTS
============
• Led migration to cloud infrastructure saving company $50K annually
• Open source contributor with 500+ GitHub stars
• Speaker at 3 tech conferences on microservices architecture""",
        
        "sample_job": """Senior Software Engineer - Cloud Platform Team

COMPANY: InnovateTech Solutions
LOCATION: Remote / San Francisco, CA
SALARY: $120,000 - $160,000

ABOUT THE ROLE
==============
We are seeking a Senior Software Engineer to join our Cloud Platform team. You will be responsible for designing and building scalable cloud-native applications that serve millions of users worldwide.

REQUIREMENTS
============
• 5+ years of software development experience
• Strong proficiency in Python and JavaScript
• Experience with React and modern frontend frameworks
• Deep knowledge of AWS cloud services (EC2, S3, Lambda, RDS)
• Experience with containerization (Docker, Kubernetes)
• Strong understanding of microservices architecture
• Experience with CI/CD pipelines and DevOps practices
• Excellent problem-solving and communication skills
• Experience leading development teams
• Bachelor's degree in Computer Science or related field

PREFERRED QUALIFICATIONS
========================
• Experience with Infrastructure as Code (Terraform, CloudFormation)
• Knowledge of monitoring and observability tools
• AWS certifications (Solutions Architect, Developer)
• Experience with agile development methodologies
• Open source contributions
• Experience with high-traffic, distributed systems

RESPONSIBILITIES
================
• Design and develop scalable cloud-native applications
• Lead technical discussions and architecture decisions
• Mentor junior developers and conduct code reviews
• Collaborate with product managers and designers
• Ensure code quality and implement best practices
• Participate in on-call rotation for production systems
• Drive continuous improvement initiatives

BENEFITS
========
• Competitive salary and equity package
• Comprehensive health, dental, and vision insurance
• Flexible PTO and remote work options
• $2,000 annual learning and development budget
• Top-tier equipment and home office setup allowance"""
    }

def generate_text_report(results):
    """Generate a formatted text report"""
    report = f"""
NextFitAI Resume Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

EXECUTIVE SUMMARY
=================
Match Score: {results['match_score']}%
Confidence Score: {results['confidence_score']}%
Analysis Date: {results['analysis_timestamp']}

MISSING SKILLS ANALYSIS
=======================
"""
    
    if results['missing_skills']:
        for skill in results['missing_skills']:
            report += f"• {skill}\n"
    else:
        report += "✅ No critical missing skills identified.\n"
    
    report += f"""
IMPROVEMENT RECOMMENDATIONS
===========================
"""
    
    if results['recommendations']:
        for i, rec in enumerate(results['recommendations'], 1):
            report += f"{i}. {rec}\n"
    else:
        report += "✅ No specific recommendations at this time.\n"
    
    report += f"""
NEXT STEPS
==========
1. Address the missing skills through training or certification
2. Update your resume to highlight relevant experience
3. Practice interview questions related to the identified gaps
4. Consider networking with professionals in your target role

Generated by NextFitAI Resume Analyzer
https://github.com/your-repo/NextFitAI-Backend
"""
    
    return report

def display_results(results):
    """Display analysis results in a beautiful format"""
    
    st.markdown("---")
    st.markdown('<div class="main-header"><h1>📊 Analysis Results</h1></div>', unsafe_allow_html=True)
    
    # Key metrics row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="🎯 Match Score",
            value=f"{results['match_score']}%",
            delta=f"{results['match_score'] - 70}% vs target" if results['match_score'] != 70 else None
        )
    
    with col2:
        st.metric(
            label="🔍 Confidence Score",
            value=f"{results['confidence_score']}%"
        )
    
    with col3:
        analysis_date = datetime.fromisoformat(results['analysis_timestamp'].replace('Z', '+00:00'))
        st.metric(
            label="📅 Analysis Date",
            value=analysis_date.strftime("%Y-%m-%d")
        )
    
    # Match score visualization
    st.markdown("### 📈 Match Score Breakdown")
    
    # Create a more detailed progress visualization
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.progress(results['match_score'] / 100)
    
    with col2:
        if results['match_score'] >= 80:
            st.success("Excellent Match!")
        elif results['match_score'] >= 60:
            st.warning("Good Match")
        else:
            st.error("Needs Improvement")
    
    # Missing skills section
    if results['missing_skills']:
        st.markdown("### 🔧 Skills Gap Analysis")
        
        # Create skill tags with better styling
        skills_html = '<div style="margin: 1rem 0;">'
        for skill in results['missing_skills']:
            skills_html += f'<span class="skill-tag">{skill}</span> '
        skills_html += '</div>'
        
        st.markdown(skills_html, unsafe_allow_html=True)
        
        # Skill priority analysis
        st.markdown("**Priority Level:**")
        if len(results['missing_skills']) <= 2:
            st.info("🟢 Low Priority - Minor skill gaps identified")
        elif len(results['missing_skills']) <= 4:
            st.warning("🟡 Medium Priority - Several skills to develop")
        else:
            st.error("🔴 High Priority - Significant skill gaps to address")
    else:
        st.success("✅ No critical missing skills identified!")
    
    # Recommendations section
    if results['recommendations']:
        st.markdown("### 💡 Personalized Recommendations")
        
        for i, recommendation in enumerate(results['recommendations'], 1):
            st.markdown(f"""
            <div class="recommendation-item">
                <strong>{i}.</strong> {recommendation}
            </div>
            """, unsafe_allow_html=True)
    
    # Action items
    st.markdown("### 🎯 Next Steps")
    
    action_items = [
        "Review and address the identified missing skills",
        "Update your resume to better highlight relevant experience",
        "Practice explaining your experience in relation to job requirements",
        "Consider obtaining certifications for missing technical skills",
        "Network with professionals in your target role"
    ]
    
    for item in action_items:
        st.markdown(f"- {item}")
    
    # Export section
    st.markdown("### 📥 Export Your Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # JSON download
        results_json = json.dumps(results, indent=2)
        st.download_button(
            label="📄 Download JSON",
            data=results_json,
            file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # Text report download
        report = generate_text_report(results)
        st.download_button(
            label="📝 Download Report",
            data=report,
            file_name=f"resume_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col3:
        # Share results (placeholder)
        if st.button("🔗 Share Results", use_container_width=True):
            st.info("Share functionality coming soon!")

def analyze_resume(resume_text, job_description):
    """Handle the complete analysis workflow"""
    
    # Submit analysis
    with st.spinner("🚀 Submitting analysis..."):
        result = submit_analysis(resume_text, job_description)
    
    if not result["success"]:
        st.error(f"❌ Failed to submit analysis: {result['error']}")
        return
    
    analysis_id = result["data"]["analysis_id"]
    st.success(f"✅ Analysis submitted successfully!")
    st.info(f"📋 Analysis ID: `{analysis_id}`")
    
    # Store in session state for persistence
    st.session_state.current_analysis_id = analysis_id
    
    # Poll for results
    st.markdown("### 🔄 Processing Your Analysis")
    st.markdown("Please wait while our AI analyzes your resume against the job requirements...")
    
    with st.container():
        result = poll_for_results(analysis_id)
    
    if result["success"]:
        # Save to history
        save_analysis_to_history(analysis_id, result["data"]["results"])
        display_results(result["data"]["results"])
    else:
        st.error(f"❌ Analysis failed: {result['error']}")
        st.info("💡 Please try again or contact support if the issue persists.")

def save_analysis_to_history(analysis_id, results):
    """Save analysis to session state history"""
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    
    analysis_record = {
        "id": analysis_id,
        "timestamp": datetime.now().isoformat(),
        "results": results
    }
    
    st.session_state.analysis_history.append(analysis_record)
    
    # Keep only last 10 analyses
    if len(st.session_state.analysis_history) > 10:
        st.session_state.analysis_history = st.session_state.analysis_history[-10:]

def show_analysis_history():
    """Display analysis history"""
    if 'analysis_history' in st.session_state and st.session_state.analysis_history:
        st.header("📚 Analysis History")
        
        for analysis in reversed(st.session_state.analysis_history):
            with st.expander(f"Analysis {analysis['id'][:8]}... - {analysis['timestamp'][:10]}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Match Score", f"{analysis['results']['match_score']}%")
                    st.metric("Confidence", f"{analysis['results']['confidence_score']}%")
                
                with col2:
                    st.write("**Missing Skills:**")
                    for skill in analysis['results']['missing_skills']:
                        st.write(f"• {skill}")
                
                if st.button(f"View Full Results", key=f"view_{analysis['id']}"):
                    display_results(analysis['results'])
    else:
        st.info("No analysis history available. Complete an analysis to see your history here.")

def main():
    """Main application function"""
    
    # Header
    st.markdown('<div class="main-header"><h1>🎯 NextFitAI Resume Analyzer</h1><p>AI-powered resume analysis to optimize your job applications</p></div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🔍 System Status")
        
        if st.button("🔄 Check Health", type="secondary"):
            with st.spinner("Checking system health..."):
                health = check_system_health()
            
            if health.get("status") == "healthy":
                st.success("✅ System Healthy")
                with st.expander("System Details"):
                    st.json(health["checks"])
            else:
                st.error("❌ System Issues")
                st.json(health)
        
        st.markdown("---")
        
        # Sample data loader
        st.header("📝 Quick Start")
        if st.button("📋 Load Sample Data", type="secondary"):
            sample_data = get_sample_data()
            st.session_state.sample_resume = sample_data["sample_resume"]
            st.session_state.sample_job = sample_data["sample_job"]
            st.success("✅ Sample data loaded!")
            st.rerun()
        
        st.markdown("---")
        
        # Analysis history
        st.header("📚 History")
        if st.button("📊 View History", type="secondary"):
            st.session_state.show_history = True
            st.rerun()
    
    # Show history if requested
    if st.session_state.get('show_history', False):
        show_analysis_history()
        if st.button("🔙 Back to Analyzer"):
            st.session_state.show_history = False
            st.rerun()
        return
    
    # Main content area
    st.markdown("### 📄 Input Your Information")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### Resume Content")
        resume_text = st.text_area(
            "Paste your resume content here:",
            height=400,
            placeholder="John Doe\nSoftware Engineer\n\nExperience:\n• 5+ years in Python development...",
            help="Copy and paste your complete resume text. Include all sections: experience, skills, education, etc.",
            value=st.session_state.get('sample_resume', '')
        )
    
    with col2:
        st.markdown("#### Job Description")
        job_description = st.text_area(
            "Paste the job description here:",
            height=400,
            placeholder="Senior Software Engineer\n\nWe are seeking...\n\nRequirements:\n• 5+ years experience...",
            help="Copy and paste the complete job description you want to match against.",
            value=st.session_state.get('sample_job', '')
        )
    
    # Input validation
    resume_valid = len(resume_text.strip()) > 50
    job_valid = len(job_description.strip()) > 50
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")
        
        # Show validation status
        if resume_text.strip() and not resume_valid:
            st.warning("⚠️ Resume text seems too short. Please provide more details.")
        
        if job_description.strip() and not job_valid:
            st.warning("⚠️ Job description seems too short. Please provide more details.")
        
        # Analysis button
        if st.button("🚀 Analyze Resume", type="primary", use_container_width=True, disabled=not (resume_valid and job_valid)):
            analyze_resume(resume_text, job_description)
        
        if not resume_text.strip() or not job_description.strip():
            st.info("💡 Fill in both fields above to start your analysis")
        elif not (resume_valid and job_valid):
            st.info("💡 Please provide more detailed content for accurate analysis")

# Initialize session state
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

if 'current_analysis_id' not in st.session_state:
    st.session_state.current_analysis_id = None

if 'show_history' not in st.session_state:
    st.session_state.show_history = False

# Run the app
if __name__ == "__main__":
    main()
