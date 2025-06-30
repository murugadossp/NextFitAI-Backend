# NextFitAI Streamlit Integration Guide

## 🚀 Quick Start

**Base URL**: `https://febwc3ocqb.execute-api.us-east-1.amazonaws.com/prod`

**Complete Streamlit Workflow**:
1. Submit resume analysis → `POST /analyze`
2. Poll for results → `GET /results/{analysis_id}`
3. Monitor system health → `GET /health`

## 📋 Installation & Setup

### Required Dependencies

```bash
pip install streamlit requests uuid
```

### Basic App Structure

```python
import streamlit as st
import requests
import uuid
import time
import json
from datetime import datetime

# Configure Streamlit page
st.set_page_config(
    page_title="NextFitAI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "https://febwc3ocqb.execute-api.us-east-1.amazonaws.com/prod"
```

## 🔧 API Integration Functions

### Core API Functions

```python
import streamlit as st
import requests
import uuid
import time

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
        status_text.text(f"Analyzing... Attempt {attempt + 1}/{max_attempts}")
        
        result = get_analysis_results(analysis_id)
        
        if result["success"]:
            data = result["data"]
            
            if data["status"] == "completed":
                progress_bar.progress(1.0)
                status_text.text("✅ Analysis completed!")
                return {"success": True, "data": data}
            elif data["status"] == "failed":
                return {"success": False, "error": data.get("error", "Analysis failed")}
            # Continue polling if status is "processing"
        else:
            return result
        
        if attempt < max_attempts - 1:
            time.sleep(interval)
    
    return {"success": False, "error": "Analysis timeout - please try again"}
```

## 🎨 Complete Streamlit Application

### Main Application

```python
import streamlit as st
import requests
import uuid
import time
import json
from datetime import datetime

# API Configuration
API_BASE_URL = "https://febwc3ocqb.execute-api.us-east-1.amazonaws.com/prod"

def main():
    st.title("🎯 NextFitAI Resume Analyzer")
    st.markdown("AI-powered resume analysis to match your skills with job requirements")
    
    # Sidebar for system health
    with st.sidebar:
        st.header("🔍 System Status")
        if st.button("Check Health", type="secondary"):
            health = check_system_health()
            if health.get("status") == "healthy":
                st.success("✅ System Healthy")
                st.json(health["checks"])
            else:
                st.error("❌ System Issues")
                st.json(health)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📄 Resume Input")
        resume_text = st.text_area(
            "Paste your resume content here:",
            height=300,
            placeholder="John Doe\nSoftware Engineer\n\nExperience:\n• 5+ years in Python development...",
            help="Copy and paste your complete resume text"
        )
    
    with col2:
        st.header("💼 Job Description")
        job_description = st.text_area(
            "Paste the job description here:",
            height=300,
            placeholder="Senior Software Engineer\n\nWe are seeking...\n\nRequirements:\n• 5+ years experience...",
            help="Copy and paste the job description you want to match against"
        )
    
    # Analysis submission
    st.markdown("---")
    
    if st.button("🚀 Analyze Resume", type="primary", use_container_width=True):
        if not resume_text.strip() or not job_description.strip():
            st.error("❌ Please fill in both resume and job description")
        else:
            analyze_resume(resume_text, job_description)

def analyze_resume(resume_text, job_description):
    """Handle the complete analysis workflow"""
    
    # Submit analysis
    with st.spinner("Submitting analysis..."):
        result = submit_analysis(resume_text, job_description)
    
    if not result["success"]:
        st.error(f"❌ Failed to submit analysis: {result['error']}")
        return
    
    analysis_id = result["data"]["analysis_id"]
    st.success(f"✅ Analysis submitted! ID: `{analysis_id}`")
    
    # Store in session state for persistence
    st.session_state.current_analysis_id = analysis_id
    
    # Poll for results
    st.markdown("### 🔄 Processing Analysis")
    
    with st.container():
        result = poll_for_results(analysis_id)
    
    if result["success"]:
        display_results(result["data"]["results"])
    else:
        st.error(f"❌ Analysis failed: {result['error']}")

def display_results(results):
    """Display analysis results in a beautiful format"""
    
    st.markdown("---")
    st.header("📊 Analysis Results")
    
    # Key metrics row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="🎯 Match Score",
            value=f"{results['match_score']}%",
            delta=f"{results['match_score'] - 50}% vs average" if results['match_score'] > 50 else None
        )
    
    with col2:
        st.metric(
            label="🔍 Confidence Score",
            value=f"{results['confidence_score']}%"
        )
    
    with col3:
        st.metric(
            label="📅 Analysis Date",
            value=datetime.fromisoformat(results['analysis_timestamp'].replace('Z', '+00:00')).strftime("%Y-%m-%d")
        )
    
    # Progress bar for match score
    st.markdown("### Match Score Breakdown")
    st.progress(results['match_score'] / 100)
    
    # Missing skills
    if results['missing_skills']:
        st.markdown("### 🔧 Missing Skills")
        
        # Create skill tags
        skills_html = ""
        for skill in results['missing_skills']:
            skills_html += f'<span style="background-color: #ff4b4b; color: white; padding: 4px 8px; margin: 2px; border-radius: 12px; font-size: 12px; display: inline-block;">{skill}</span> '
        
        st.markdown(skills_html, unsafe_allow_html=True)
    
    # Recommendations
    if results['recommendations']:
        st.markdown("### 💡 Recommendations")
        
        for i, recommendation in enumerate(results['recommendations'], 1):
            st.markdown(f"**{i}.** {recommendation}")
    
    # Download results
    st.markdown("### 📥 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # JSON download
        results_json = json.dumps(results, indent=2)
        st.download_button(
            label="📄 Download as JSON",
            data=results_json,
            file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    with col2:
        # Text report download
        report = generate_text_report(results)
        st.download_button(
            label="📝 Download Report",
            data=report,
            file_name=f"resume_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

def generate_text_report(results):
    """Generate a formatted text report"""
    report = f"""
NextFitAI Resume Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY
=======
Match Score: {results['match_score']}%
Confidence Score: {results['confidence_score']}%
Analysis Date: {results['analysis_timestamp']}

MISSING SKILLS
==============
"""
    
    if results['missing_skills']:
        for skill in results['missing_skills']:
            report += f"• {skill}\n"
    else:
        report += "No missing skills identified.\n"
    
    report += f"""
RECOMMENDATIONS
===============
"""
    
    if results['recommendations']:
        for i, rec in enumerate(results['recommendations'], 1):
            report += f"{i}. {rec}\n"
    else:
        report += "No specific recommendations available.\n"
    
    return report

# Include all the API functions from above here...
# (submit_analysis, get_analysis_results, poll_for_results, check_system_health)

if __name__ == "__main__":
    main()
```

## 🔄 Advanced Streamlit Patterns

### Session State Management

```python
# Initialize session state
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

if 'current_analysis_id' not in st.session_state:
    st.session_state.current_analysis_id = None

# Store analysis in history
def save_analysis_to_history(analysis_id, results):
    analysis_record = {
        "id": analysis_id,
        "timestamp": datetime.now().isoformat(),
        "results": results
    }
    st.session_state.analysis_history.append(analysis_record)
    
    # Keep only last 10 analyses
    if len(st.session_state.analysis_history) > 10:
        st.session_state.analysis_history = st.session_state.analysis_history[-10:]

# Display analysis history
def show_analysis_history():
    if st.session_state.analysis_history:
        st.header("📚 Analysis History")
        
        for analysis in reversed(st.session_state.analysis_history):
            with st.expander(f"Analysis {analysis['id'][:8]}... - {analysis['timestamp'][:10]}"):
                st.json(analysis['results'])
```

### Caching Strategies

```python
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_health_status():
    """Cached health check to avoid repeated API calls"""
    return check_system_health()

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_sample_data():
    """Cache sample resume and job description data"""
    return {
        "sample_resume": """John Doe
Software Engineer

Experience:
• 5+ years of experience in full-stack development
• Proficient in JavaScript, Python, and React
• Experience with AWS cloud services
• Led team of 3 developers on multiple projects
• Improved application performance by 40%

Skills:
• Programming: JavaScript, Python, Java, SQL
• Frameworks: React, Node.js, Express
• Cloud: AWS (EC2, S3, Lambda), Docker
• Databases: PostgreSQL, MongoDB
• Tools: Git, Jenkins, JIRA

Education:
• Bachelor's in Computer Science
• AWS Certified Solutions Architect""",
        
        "sample_job": """Senior Software Engineer

We are seeking a Senior Software Engineer to join our growing team.

Requirements:
• 5+ years of software development experience
• Strong proficiency in Python and JavaScript
• Experience with React and modern frontend frameworks
• Knowledge of AWS cloud services (EC2, S3, Lambda)
• Experience with containerization (Docker, Kubernetes)
• Strong problem-solving and communication skills
• Experience leading development teams
• Bachelor's degree in Computer Science or related field

Preferred:
• Experience with microservices architecture
• Knowledge of CI/CD pipelines
• AWS certifications
• Experience with agile development methodologies"""
    }
```

### Error Handling with Streamlit

```python
def safe_api_call(func, *args, **kwargs):
    """Wrapper for safe API calls with error handling"""
    try:
        return func(*args, **kwargs)
    except requests.exceptions.Timeout:
        st.error("⏰ Request timed out. Please try again.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("🌐 Connection error. Please check your internet connection.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API Error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"💥 Unexpected error: {str(e)}")
        return None

# Usage
result = safe_api_call(submit_analysis, resume_text, job_description)
if result:
    # Process successful result
    pass
```

## 📱 Multi-Page Streamlit App

### App Structure

```python
# pages/1_🏠_Home.py
import streamlit as st

st.set_page_config(page_title="NextFitAI - Home", page_icon="🏠")

st.title("🏠 NextFitAI Home")
st.markdown("Welcome to NextFitAI Resume Analyzer")

# Main analysis interface here...
```

```python
# pages/2_📊_Analytics.py
import streamlit as st

st.set_page_config(page_title="NextFitAI - Analytics", page_icon="📊")

st.title("📊 Analysis Dashboard")

# Show analysis history and statistics
if 'analysis_history' in st.session_state:
    analyses = st.session_state.analysis_history
    
    if analyses:
        # Create charts and metrics
        scores = [a['results']['match_score'] for a in analyses]
        
        st.line_chart(scores)
        st.metric("Average Match Score", f"{sum(scores)/len(scores):.1f}%")
```

```python
# pages/3_⚙️_Settings.py
import streamlit as st

st.set_page_config(page_title="NextFitAI - Settings", page_icon="⚙️")

st.title("⚙️ Settings")

# API configuration
st.header("API Configuration")
api_url = st.text_input("API Base URL", value=API_BASE_URL)
timeout = st.slider("Request Timeout (seconds)", 5, 60, 30)

# Save settings to session state
if st.button("Save Settings"):
    st.session_state.api_url = api_url
    st.session_state.timeout = timeout
    st.success("Settings saved!")
```

## 🚀 Deployment Options

### Streamlit Cloud

```bash
# requirements.txt
streamlit>=1.28.0
requests>=2.31.0
```

```toml
# .streamlit/config.toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501
```

### Local Development

```bash
# Run the app
streamlit run streamlit_app.py

# Run with custom port
streamlit run streamlit_app.py --server.port 8502
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.headless", "true", "--server.address", "0.0.0.0"]
```

## 🧪 Testing Strategies

### Unit Testing

```python
# test_api_functions.py
import pytest
import requests_mock
from streamlit_app import submit_analysis, get_analysis_results

def test_submit_analysis_success():
    with requests_mock.Mocker() as m:
        m.post(
            "https://febwc3ocqb.execute-api.us-east-1.amazonaws.com/prod/analyze",
            json={"status": "submitted", "analysis_id": "test-id"},
            status_code=202
        )
        
        result = submit_analysis("resume", "job description")
        assert result["success"] == True
        assert result["data"]["analysis_id"] == "test-id"

def test_get_analysis_results_completed():
    with requests_mock.Mocker() as m:
        m.get(
            "https://febwc3ocqb.execute-api.us-east-1.amazonaws.com/prod/results/test-id",
            json={
                "status": "completed",
                "results": {
                    "match_score": 85,
                    "missing_skills": ["Python"],
                    "recommendations": ["Add Python skills"],
                    "confidence_score": 90,
                    "analysis_timestamp": "2025-06-30T10:00:00Z"
                }
            }
        )
        
        result = get_analysis_results("test-id")
        assert result["success"] == True
        assert result["data"]["status"] == "completed"
```

### Integration Testing

```python
# test_integration.py
import streamlit as st
from streamlit.testing.v1 import AppTest

def test_app_loads():
    """Test that the app loads without errors"""
    at = AppTest.from_file("streamlit_app.py")
    at.run()
    assert not at.exception

def test_form_submission():
    """Test form submission with sample data"""
    at = AppTest.from_file("streamlit_app.py")
    at.run()
    
    # Fill in form data
    at.text_area[0].input("Sample resume text")
    at.text_area[1].input("Sample job description")
    
    # Submit form
    at.button[0].click()
    at.run()
    
    # Check for expected elements
    assert len(at.error) == 0  # No errors
```

## 🎯 Best Practices

### 1. Performance Optimization

```python
# Use caching for expensive operations
@st.cache_data
def expensive_computation(data):
    # Heavy processing here
    return processed_data

# Use session state for user data
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}

# Minimize API calls
if 'last_health_check' not in st.session_state:
    st.session_state.last_health_check = None
    st.session_state.health_status = None

# Check health only if needed
now = time.time()
if (st.session_state.last_health_check is None or 
    now - st.session_state.last_health_check > 300):  # 5 minutes
    st.session_state.health_status = check_system_health()
    st.session_state.last_health_check = now
```

### 2. User Experience

```python
# Show loading states
with st.spinner("Processing..."):
    result = long_running_operation()

# Use progress bars for long operations
progress_bar = st.progress(0)
for i in range(100):
    progress_bar.progress(i + 1)
    time.sleep(0.01)

# Provide helpful error messages
try:
    result = api_call()
except Exception as e:
    st.error(f"Something went wrong: {e}")
    st.info("💡 Try refreshing the page or contact support if the issue persists.")
```

### 3. Security

```python
# Validate inputs
def validate_input(text, max_length=10000):
    if not text or not text.strip():
        return False, "Text cannot be empty"
    if len(text) > max_length:
        return False, f"Text too long (max {max_length} characters)"
    return True, ""

# Sanitize data before API calls
import html

def sanitize_text(text):
    return html.escape(text.strip())

# Use environment variables for sensitive data
import os
API_KEY = os.getenv("NEXTFITAI_API_KEY", "")
```

## 🔗 Additional Resources

- **Streamlit Documentation**: https://docs.streamlit.io/
- **API Testing**: Use the test files in `tests/` directory
- **Monitoring**: Check `utilities/monitor_analysis_status.py` for CLI monitoring
- **Architecture**: Review `design_docs/` for system architecture

## 🆘 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install streamlit requests
   ```

2. **API Connection Issues**
   ```python
   # Test API connectivity
   import requests
   response = requests.get("https://febwc3ocqb.execute-api.us-east-1.amazonaws.com/prod/health")
   print(response.status_code, response.json())
   ```

3. **Session State Issues**
   ```python
   # Clear session state if needed
   for key in st.session_state.keys():
       del st.session_state[key]
   st.rerun()
   ```

4. **Caching Issues**
   ```python
   # Clear cache
   st.cache_data.clear()
   ```

---

**Ready to build?** Use the complete Streamlit app example above or check out the demo file for a working implementation!
