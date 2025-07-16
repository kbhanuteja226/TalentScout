import streamlit as st
import os
import requests
import json
import re
from datetime import datetime
from dotenv import load_dotenv
import hashlib

# ==================== CONFIGURATION ====================
load_dotenv()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
MODEL_NAME = "meta-llama/Llama-3-8b-chat-hf"
TOGETHER_URL = "https://api.together.xyz/v1/chat/completions"

# ==================== SESSION STATE ====================
def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        "messages": [],
        "conversation_stage": "greeting",
        "candidate_info": {"name": "", "email": "", "phone": "", "experience": "", "position": "", "location": "", "tech_stack": []},
        "technical_questions": [],
        "technical_answers": [],
        "current_question_index": 0,
        "conversation_ended": False,
        "session_id": hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8],
        "start_time": datetime.now().strftime('%H:%M')
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ==================== API UTILITIES ====================
def ask_llama(prompt, max_tokens=512, temperature=0.7, context_messages=None):
    """Enhanced LLaMA API call with context support"""
    if not TOGETHER_API_KEY:
        return "❌ API key not configured. Please set TOGETHER_API_KEY in your .env file."
    
    headers = {"Authorization": f"Bearer {TOGETHER_API_KEY}", "Content-Type": "application/json"}
    messages = (context_messages or []) + [{"role": "user", "content": prompt}]
    payload = {"model": MODEL_NAME, "max_tokens": max_tokens, "temperature": temperature, "messages": messages}
    
    try:
        response = requests.post(TOGETHER_URL, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        elif response.status_code == 401:
            return "❌ Authentication failed. Please check your API key."
        elif response.status_code == 429:
            return "❌ Rate limit exceeded. Please wait and try again."
        else:
            return f"❌ API Error: {response.status_code}"
    except requests.exceptions.Timeout:
        return "❌ Request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return "❌ Connection error. Please check your internet connection."
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

# ==================== VALIDATION FUNCTIONS ====================
def validate_email(email):
    """Enhanced email validation"""
    if not email or len(email) < 5 or len(email) > 254:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Enhanced phone validation"""
    if not phone:
        return False
    clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
    pattern = r'^(\+[1-9]\d{1,14}|[1-9]\d{9})$'
    return re.match(pattern, clean_phone) is not None

def validate_experience(experience):
    """Validate experience input"""
    if not experience:
        return False
    numbers = re.findall(r'\d+', experience)
    if numbers:
        years = int(numbers[0])
        return 0 <= years <= 50
    return False

def extract_tech_stack(text):
    """Enhanced tech stack extraction"""
    tech_categories = {
        'languages': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'php', 'ruby', 'swift', 'kotlin'],
        'frameworks': ['react', 'angular', 'vue', 'nodejs', 'express', 'django', 'flask', 'spring', 'laravel', 'rails', 'fastapi'],
        'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'oracle', 'cassandra', 'elasticsearch'],
        'cloud': ['aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'jenkins', 'git', 'linux'],
        'web': ['html', 'css', 'bootstrap', 'tailwind', 'sass', 'jquery', 'webpack'],
        'ml': ['tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'keras', 'opencv']
    }
    
    found_tech = []
    text_lower = text.lower()
    
    for category, techs in tech_categories.items():
        for tech in techs:
            if tech in text_lower:
                found_tech.append(tech.title())
    
    return list(dict.fromkeys(found_tech))

# ==================== TECHNICAL QUESTIONS ====================
def generate_technical_questions(tech_stack, num_questions=3):
    """Generate technical questions based on tech stack"""
    questions = []
    selected_techs = tech_stack[:num_questions] if len(tech_stack) >= num_questions else tech_stack
    
    for tech in selected_techs:
        context_messages = [{"role": "system", "content": "You are an expert technical interviewer. Generate practical, professional-level interview questions."}]
        
        prompt = f"""Generate 1 technical interview question for {tech} technology.

Requirements:
- Assess practical knowledge and problem-solving skills
- Appropriate for professional experience level
- Not too basic or extremely advanced
- Answerable in 2-3 paragraphs
- Focus on real-world scenarios

Return only the question without additional formatting."""
        
        question = ask_llama(prompt, max_tokens=200, temperature=0.8, context_messages=context_messages)
        if question and not question.startswith("❌"):
            clean_question = question.strip().replace('"', '').replace("'", "")
            questions.append(f"**{tech}**: {clean_question}")
    
    return questions

# ==================== CONVERSATION HANDLERS ====================
def handle_greeting():
    """Initial greeting message"""
    return """🤖 **Welcome to TalentScout AI!**

I'm your intelligent hiring assistant, designed to streamline the initial screening process for technology positions.

**What I'll do:**
✅ Gather your essential information  
✅ Understand your technical expertise  
✅ Ask relevant technical questions  
✅ Provide a smooth screening experience  

Let's begin! Could you please tell me your **full name**?"""

def handle_information_gathering(user_input):
    """Handle information collection phase"""
    info = st.session_state.candidate_info
    
    # Name collection
    if not info["name"]:
        if len(user_input.strip()) >= 2:
            info["name"] = user_input.strip().title()
            return f"Nice to meet you, **{info['name']}**! 📧\n\nCould you please provide your **email address**?"
        else:
            return "Please provide your full name (at least 2 characters):"
    
    # Email collection
    elif not info["email"]:
        if validate_email(user_input.strip()):
            info["email"] = user_input.strip().lower()
            return "📱 Perfect! Now, could you please provide your **phone number**?"
        else:
            return "❌ Please provide a valid email address (e.g., name@company.com):"
    
    # Phone collection
    elif not info["phone"]:
        if validate_phone(user_input.strip()):
            info["phone"] = user_input.strip()
            return "💼 Great! How many **years of professional experience** do you have?\n\n*Please provide a number (e.g., '3 years' or '5')*"
        else:
            return "❌ Please provide a valid phone number:"
    
    # Experience collection
    elif not info["experience"]:
        if validate_experience(user_input.strip()):
            info["experience"] = user_input.strip()
            return "🎯 Excellent! What **position(s)** are you interested in?\n\n*Examples: Software Engineer, Data Scientist, Full Stack Developer*"
        else:
            return "❌ Please provide your years of experience as a number:"
    
    # Position collection
    elif not info["position"]:
        if len(user_input.strip()) >= 3:
            info["position"] = user_input.strip().title()
            return "📍 Perfect! Could you please tell me your **current location**?"
        else:
            return "Please provide a valid position title (at least 3 characters):"
    
    # Location collection
    elif not info["location"]:
        if len(user_input.strip()) >= 2:
            info["location"] = user_input.strip().title()
            return """🛠️ Finally, let's discuss your technical expertise!

Please list your **technical skills and tech stack**:

**Example:** "Python, Django, React, PostgreSQL, AWS, Docker"

*This helps me generate relevant technical questions.*"""
        else:
            return "Please provide your location (at least 2 characters):"
    
    # Tech stack collection
    elif not info["tech_stack"]:
        tech_stack = extract_tech_stack(user_input)
        if len(tech_stack) >= 2:
            info["tech_stack"] = tech_stack
            st.session_state.conversation_stage = "generating_questions"
            return f"""✅ **Information Collection Complete!**

**Summary:**
- **Name:** {info['name']}
- **Email:** {info['email']}
- **Position:** {info['position']}
- **Experience:** {info['experience']}
- **Tech Stack:** {', '.join(info['tech_stack'])}

🧠 **Generating Technical Questions...please type "continue"**"""
        else:
            return "❌ I need at least 2 technologies to generate relevant questions. Please provide more technical skills."

def handle_technical_questions(user_input):
    """Handle technical question phase"""
    # Store current answer
    if st.session_state.current_question_index < len(st.session_state.technical_questions):
        current_question = st.session_state.technical_questions[st.session_state.current_question_index]
        st.session_state.technical_answers.append({
            "question": current_question,
            "answer": user_input.strip(),
            "timestamp": datetime.now().isoformat()
        })
        
        st.session_state.current_question_index += 1
        
        # Check if more questions remain
        if st.session_state.current_question_index < len(st.session_state.technical_questions):
            next_question = st.session_state.technical_questions[st.session_state.current_question_index]
            progress = st.session_state.current_question_index + 1
            total = len(st.session_state.technical_questions)
            
            return f"""✅ **Thank you for your answer!**

**Question {progress} of {total}:**
{next_question}

*Please provide your answer based on your experience.*"""
        else:
            st.session_state.conversation_stage = "conclusion"
            return """🎉 **Technical Questions Complete!**

You've successfully answered all technical questions. Thank you for completing the screening process.

**Next Steps:**
- Our team will review your responses within 2-3 business days
- You'll receive an email update about the next phase
- If selected, we'll schedule a detailed technical interview

*You can say 'bye' or 'exit' when ready to end our conversation.*"""

def detect_conversation_ending(user_input):
    """Detect conversation ending patterns"""
    ending_patterns = [
        r'\b(bye|goodbye|exit|quit|stop|end|finish)\b',
        r'\b(thank you|thanks).*(bye|goodbye|done)\b',
        r'\b(done|finished|complete)\b',
        r'\b(no more|nothing else|that\'s all)\b'
    ]
    
    return any(re.search(pattern, user_input.lower()) for pattern in ending_patterns)

def handle_conversation(user_input):
    """Main conversation handler"""
    if st.session_state.conversation_ended:
        return "This conversation has ended. Please refresh the page to start a new session."
    
    # Check for exit intent
    if detect_conversation_ending(user_input):
        st.session_state.conversation_ended = True
        return """👋 **Thank you for using TalentScout AI!**

We appreciate your time and interest. Our team will be in touch soon!

**Have a great day!** 🌟

*This conversation has ended. Refresh the page to start a new session.*"""
    
    # Handle conversation stages
    try:
        if st.session_state.conversation_stage == "greeting":
            st.session_state.conversation_stage = "info_gathering"
            return handle_information_gathering(user_input)
        
        elif st.session_state.conversation_stage == "info_gathering":
            return handle_information_gathering(user_input)
        
        elif st.session_state.conversation_stage == "generating_questions":
            # Generate technical questions
            tech_stack = st.session_state.candidate_info["tech_stack"]
            questions = generate_technical_questions(tech_stack, num_questions=min(3, len(tech_stack)))
            
            if questions and not any(q.startswith("❌") for q in questions):
                st.session_state.technical_questions = questions
                st.session_state.current_question_index = 0
                st.session_state.conversation_stage = "technical_questions"
                
                first_question = questions[0]
                return f"""🧠 **Technical Assessment Ready!**

**Question 1 of {len(questions)}:**
{first_question}

*Please provide your answer based on your experience. If you can't answer the question type "Continue" *"""
            else:
                return "❌ I encountered an issue generating questions. Please try again."
        
        elif st.session_state.conversation_stage == "technical_questions":
            return handle_technical_questions(user_input)
        
        elif st.session_state.conversation_stage == "conclusion":
            return """Thank you for your question! Our team will provide comprehensive information during the next phase.

Is there anything else about the screening process, or are you ready to conclude?

*Say 'bye' or 'exit' when ready to end.*"""
        
        else:
            return "I didn't understand that. Could you please rephrase your response?"
    
    except Exception as e:
        return f"❌ An error occurred. Please try again.\n\nError: {str(e)}"

# ==================== UI COMPONENTS ====================
def render_custom_css():
    """Render optimized CSS for clean UI"""
    st.markdown("""
    <style>
    /* Global reset and text color fix */
    .main .block-container {
        padding: 1rem;
        max-width: 1200px;
    }
    
    /* Ensure all text is visible */
    .stApp, .main, .sidebar .sidebar-content {
        color: #333 !important;
    }
    
    /* Fix Streamlit sidebar text color issues */
    .sidebar .sidebar-content * {
        color: #333 !important;
    }
    
    /* Fix any white text issues */
    div[data-testid="stSidebar"] * {
        color: #333 !important;
    }
    
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1.1rem;
    }
    
    /* Sidebar cards */
    .sidebar-card {
        background: white;
        border: 1px solid #e1e8ed;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        color: #333 !important;
    }
    
    .sidebar-card h3 {
        color: #1a1a1a !important;
        margin: 0 0 1rem 0;
        font-size: 1.1rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .sidebar-card * {
        color: #333 !important;
    }
    
    .progress-bar {
        background: #f0f0f0;
        border-radius: 10px;
        height: 8px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .progress-fill {
        background: linear-gradient(90deg, #667eea, #764ba2);
        height: 100%;
        transition: width 0.3s ease;
    }
    
    .info-item {
        margin: 0.8rem 0;
        padding: 0.5rem 0;
        border-bottom: 1px solid #f0f0f0;
        color: #333 !important;
    }
    
    .info-item:last-child {
        border-bottom: none;
    }
    
    .info-item strong {
        color: #1a1a1a !important;
        font-weight: 600;
    }
    
    .tech-stack {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }
    
    .tech-item {
        background: #667eea;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    /* Chat interface */
    .chat-section {
        background: white;
        border: 1px solid #e1e8ed;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    .chat-header {
        background: #f8f9fa;
        padding: 1rem 1.5rem;
        border-bottom: 1px solid #e1e8ed;
        font-weight: 600;
        color: #333;
    }
    
    /* Remove default streamlit styling */
    .element-container {
        margin: 0 !important;
    }
    
    /* Status indicators */
    .status-active {
        color: #28a745 !important;
        font-weight: 600;
    }
    
    .status-pending {
        color: #ffc107 !important;
        font-weight: 600;
    }
    
    .status-complete {
        color: #17a2b8 !important;
        font-weight: 600;
    }
    
    /* Help section */
    .help-section {
        background: #f8f9fa;
        border: 1px solid #e1e8ed;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
    }
    
    .help-section h4 {
        margin: 0 0 0.5rem 0;
        color: #495057 !important;
        font-size: 0.9rem;
    }
    
    .help-section ul {
        margin: 0;
        padding-left: 1.2rem;
        font-size: 0.85rem;
        color: #666 !important;
    }
    
    .help-section li {
        margin: 0.3rem 0;
        color: #666 !important;
    }
    
    .help-section strong {
        color: #333 !important;
    }
    </style>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render enhanced sidebar with proper styling"""
    with st.sidebar:
        # Candidate Profile
        st.markdown("""
        <div class="sidebar-card">
            <h3>👤 Candidate Profile</h3>
        </div>
        """, unsafe_allow_html=True)
        
        info = st.session_state.candidate_info
        
        # Progress tracking
        total_fields = 7
        filled_fields = sum(1 for key, value in info.items() if value and key != 'tech_stack') + (1 if info['tech_stack'] else 0)
        progress_percent = (filled_fields / total_fields) * 100
        
        st.markdown(f"""
        <div class="sidebar-card">
            <div class="progress-bar">
                <div class="progress-fill" style="width: {progress_percent}%"></div>
            </div>
            <div style="text-align: center; margin-top: 0.5rem;">
                <strong>{filled_fields}/{total_fields} fields completed</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Information display
        info_html = '<div class="sidebar-card">'
        if info["name"]:
            info_html += f'<div class="info-item"><strong>👤 Name:</strong> {info["name"]}</div>'
        if info["email"]:
            info_html += f'<div class="info-item"><strong>📧 Email:</strong> {info["email"]}</div>'
        if info["phone"]:
            info_html += f'<div class="info-item"><strong>📱 Phone:</strong> {info["phone"]}</div>'
        if info["experience"]:
            info_html += f'<div class="info-item"><strong>💼 Experience:</strong> {info["experience"]}</div>'
        if info["position"]:
            info_html += f'<div class="info-item"><strong>🎯 Position:</strong> {info["position"]}</div>'
        if info["location"]:
            info_html += f'<div class="info-item"><strong>📍 Location:</strong> {info["location"]}</div>'
        if info["tech_stack"]:
            tech_items = ''.join([f'<span class="tech-item">{tech}</span>' for tech in info["tech_stack"]])
            info_html += f'<div class="info-item"><strong>🛠️ Tech Stack:</strong><div class="tech-stack">{tech_items}</div></div>'
        info_html += '</div>'
        
        if filled_fields > 0:
            st.markdown(info_html, unsafe_allow_html=True)
        
        # Technical Assessment Progress
        if st.session_state.technical_questions:
            total_questions = len(st.session_state.technical_questions)
            answered_questions = len(st.session_state.technical_answers)
            tech_progress = (answered_questions / total_questions) * 100
            
            st.markdown(f"""
            <div class="sidebar-card">
                <h3>🧠 Technical Assessment</h3>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {tech_progress}%"></div>
                </div>
                <div style="text-align: center; margin-top: 0.5rem;">
                    <strong>{answered_questions}/{total_questions} questions answered</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Session Info
        stage_display = st.session_state.conversation_stage.replace('_', ' ').title()
        stage_class = "status-active" if not st.session_state.conversation_ended else "status-complete"
        
        st.markdown(f"""
        <div class="sidebar-card">
            <h3>ℹ️ Session Details</h3>
            <div class="info-item"><strong>Session ID:</strong> {st.session_state.session_id}</div>
            <div class="info-item"><strong>Status:</strong> <span class="{stage_class}">{stage_display}</span></div>
            <div class="info-item"><strong>Started:</strong> {st.session_state.start_time}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick Help
        st.markdown("""
        <div class="help-section">
            <h4>🆘 Quick Commands</h4>
            <ul>
                <li><strong>'bye'</strong> or <strong>'exit'</strong> - End conversation</li>
                <li>Provide clear, direct answers</li>
                <li>Ask for clarification if needed</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ==================== MAIN APPLICATION ====================
def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="TalentScout AI - Hiring Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    initialize_session_state()
    render_custom_css()
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 TalentScout AI</h1>
        <p>Intelligent recruitment screening powered by advanced AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    render_sidebar()
    
    # Main chat interface
    st.markdown("""
    <div class="chat-section">
        <div class="chat-header">
            💬 Interview Chat
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize conversation
    if not st.session_state.messages:
        initial_message = handle_greeting()
        st.session_state.messages.append({"role": "assistant", "content": initial_message})
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # User input
    if not st.session_state.conversation_ended:
        user_input = st.chat_input("Type your message here...")
        
        if user_input:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Generate response
            with st.spinner("🤔 Processing..."):
                response = handle_conversation(user_input)
            
            # Add assistant response
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Rerun to update display
            st.rerun()
    else:
        st.info("💬 Conversation ended. Refresh the page to start a new session.")

if __name__ == "__main__":
    main()