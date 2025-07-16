# 🤖 TalentScout AI – Intelligent Hiring Assistant Chatbot

TalentScout AI is a Streamlit-based chatbot designed to conduct the initial screening of candidates applying for technology roles. It leverages **LLaMA via Together AI** to intelligently gather candidate information and generate tailored technical questions based on their declared tech stack.

---

## 📌 Project Overview

TalentScout AI acts as a virtual recruiter that:

- Greets the candidate
- Collects essential details like name, email, phone number, experience, and desired position
- Extracts and validates the candidate's tech stack
- Uses LLaMA (via Together AI) to generate **real-world technical questions**
- Tracks responses and progress
- Ends conversations gracefully or handles unknown input with fallback prompts

This chatbot simulates a **human-like technical screening conversation**, reducing recruiter workload during the early stages of hiring.

---

## 💻 Installation Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/kbhanuteja226/TalentScout.git
cd TalentScout
```

### 2. (Optional) Create Virtual Environment

```bash
python -m venv venv
# Activate (Windows)
venv\Scripts\activate
# Activate (macOS/Linux)
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up API Key

Create a `.env` file in the root directory with your Together AI key:

```env
TOGETHER_API_KEY=your_real_key_here
```

---

## ▶️ Usage Guide

To launch the chatbot locally:

```bash
python -m streamlit run app.py
```

Open your browser at: `http://localhost:8501`

### What the Chatbot Does:
- Initiates conversation with a greeting
- Interactively collects candidate info (name, email, experience, etc.)
- Extracts technologies using keyword matching
- Uses LLaMA to generate custom questions
- Presents one question at a time and records answers
- Tracks progress through a sidebar panel
- Ends when the candidate types "bye", "exit", etc.

---

## ⚙️ Technical Details

**Language & Frameworks**
- Python 3.10+
- Streamlit for frontend UI
- Together AI API (LLaMA-3-8B-chat-hf)

**Libraries Used**
- `requests` – for API interaction  
- `dotenv` – to securely load environment variables  
- `re`, `datetime`, `hashlib` – for validations and session tracking  
- `streamlit` – UI interface and session management  

**Architecture Decisions**
- Stateless chatbot logic built using `st.session_state`
- Separate handlers for each stage of the conversation
- Sidebar component tracks user input and technical progress
- Custom CSS styling improves user experience

---

## 🧠 Prompt Design

### 1. **System Prompt**
```text
You are an expert technical interviewer. Generate practical, professional-level interview questions.
```

### 2. **User Prompt for Question Generation**
```text
Generate 1 technical interview question for [technology].

Requirements:
- Assess practical knowledge and problem-solving skills
- Not too basic or too advanced
- Answerable in 2–3 paragraphs
```

Prompts are optimized to be **minimal**, **focused**, and **aligned with real interview standards**. For question generation, we avoid conversational chatter and request raw, clean questions directly.

Information collection is **not handled by LLM**, but by deterministic Python logic to ensure structure and validation.

---

## 🧗 Challenges & Solutions

| Challenge | Solution |
|----------|----------|
| **1. Chatbot vs Form Logic** | Redesigned `app.py` from form-based to a real conversational chatbot using `st.chat_message()` and `session_state`. |
| **2. Model Errors or API Failures** | Added error handling for authentication, rate limits, and timeouts from Together AI API. |
| **3. Extracting Reliable Tech Stack** | Created a dictionary-based keyword matcher to accurately extract technologies from free-form input. |
| **4. UI Styling Issues** | Injected scoped CSS styles to fix dark mode/Streamlit sidebar text issues and to make layout clean and professional. |
| **5. Maintaining Context & Progress** | Used session-based logic to manage state across greeting → info → questions → conclusion stages. |
| **6. Ensuring Relevance of LLM Questions** | Crafted precise prompts focused on intermediate, real-world, role-relevant technical scenarios. |

---



## 📂 Project Structure

```
.
├── app.py
├── .env
├── requirements.txt
└── README.md
```

---

## 🙌 Acknowledgements

- Built as part of an AI/ML Internship Assignment  
- LLaMA model access provided via [Together AI](https://www.together.ai/)

---

## 📄 License

This project is for demonstration/educational use only.  
Do not use in production without security, logging, and data privacy compliance.


## 🌐 Live Demo (Deployed Versions)

- 🔵 [Streamlit Cloud Deployment](https://talentscout-smartai.streamlit.app/)
- 🟣 [Render Deployment](https://talentscoutai.onrender.com/)


