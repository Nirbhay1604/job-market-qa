import streamlit as st
import requests
import json
from retriever import retrieve
from answerer import build_prompt, post_process_answer

st.set_page_config(
    page_title="Job Market Q&A",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if 'history' not in st.session_state:
    st.session_state.history = []
if 'submitted_empty' not in st.session_state:
    st.session_state.submitted_empty = False

st.markdown("""
<style>
    .stApp { background-color: #0d0f16; color: #e0e0e0; }
    .block-container { padding: 1.5rem 1.5rem 6rem 1.5rem; }
    #MainMenu, footer, header { visibility: hidden; }
    section[data-testid="stSidebar"] { display: none; }

    .panel-title {
        color: #ffffff;
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 1rem;
        letter-spacing: 0.02em;
    }
    .panel-section {
        color: #6b7280;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin: 1rem 0 0.5rem 0;
    }
    .stat-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-bottom: 0.5rem;
    }
    .stat-card {
        background-color: #0d0f16;
        border: 1px solid #1f2130;
        border-radius: 8px;
        padding: 0.7rem;
        text-align: center;
    }
    .stat-number { color: #2563eb; font-size: 1.3rem; font-weight: 700; }
    .stat-label { color: #6b7280; font-size: 0.72rem; margin-top: 2px; }

    .chat-user { display: flex; justify-content: flex-end; margin: 0.8rem 0 0.3rem 0; }
    .chat-user-bubble {
        background-color: #2563eb;
        color: white;
        padding: 0.65rem 1rem;
        border-radius: 16px 16px 4px 16px;
        max-width: 75%;
        font-size: 0.93rem;
        line-height: 1.5;
    }
    .chat-ai { display: flex; justify-content: flex-start; margin: 0.3rem 0 0.8rem 0; }
    .chat-ai-label { color: #4b5563; font-size: 0.72rem; margin-bottom: 0.3rem; }
    .chat-ai-bubble {
        background-color: #151821;
        border: 1px solid #1f2130;
        color: #e0e0e0;
        padding: 0.9rem 1.1rem;
        border-radius: 4px 16px 16px 16px;
        max-width: 85%;
        font-size: 0.93rem;
        line-height: 1.7;
    }
    .job-card {
        background-color: #0d0f16;
        border: 1px solid #1f2130;
        border-left: 3px solid #10b981;
        padding: 0.7rem 0.9rem;
        border-radius: 6px;
        margin: 0.4rem 0;
        font-size: 0.85rem;
    }
    .job-card strong { color: #ffffff; }
    .badge {
        display: inline-block;
        background-color: #052e16;
        color: #6ee7b7;
        padding: 1px 7px;
        border-radius: 10px;
        font-size: 0.72rem;
        margin-left: 5px;
    }
    .stTextInput > div > div > input {
        background-color: #151821 !important;
        color: #e0e0e0 !important;
        border: 1px solid #1f2130 !important;
        border-radius: 10px !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.93rem !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 2px rgba(37,99,235,0.15) !important;
    }
    .stFormSubmitButton > button {
        background-color: #2563eb !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 1.2rem !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    .stFormSubmitButton > button:hover { background-color: #1d4ed8 !important; }
    .stButton > button {
        background-color: #0d0f16 !important;
        color: #9ca3af !important;
        border: 1px solid #1f2130 !important;
        border-radius: 6px !important;
        font-size: 0.8rem !important;
        font-weight: 400 !important;
        text-align: left !important;
        padding: 0.4rem 0.6rem !important;
        margin-bottom: 3px !important;
    }
    .stButton > button:hover {
        background-color: #1e2235 !important;
        color: #e0e0e0 !important;
        border-color: #2563eb !important;
    }
    hr { border-color: #1f2130; margin: 0.8rem 0; }
    h2 { color: #ffffff; margin-bottom: 0; }
</style>
""", unsafe_allow_html=True)

# ── LAYOUT ────────────────────────────────────────────────────────────────────
left, right = st.columns([1, 3], gap="medium")

# ── LEFT PANEL ────────────────────────────────────────────────────────────────
with left:
    st.markdown("<div class='panel-title'>🔍 Job Market Q&A</div>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("<div class='panel-section'>Data</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='stat-row'>
        <div class='stat-card'>
            <div class='stat-number'>161</div>
            <div class='stat-label'>Job Listings</div>
        </div>
        <div class='stat-card'>
            <div class='stat-number'>40+</div>
            <div class='stat-label'>Skills Tracked</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div class='panel-section'>Try asking</div>", unsafe_allow_html=True)

    examples = [
        "What skills do Python backend jobs need?",
        "Which companies hire for ML roles?",
        "What do DevOps engineers need?",
        "Common requirements for remote jobs?",
        "Which roles need TypeScript?",
    ]

    for ex in examples:
        if st.button(ex, key=f"ex_{ex}", use_container_width=True):
            with st.spinner("🔎 Searching..."):
                retrieved = retrieve(ex)
            st.session_state.history.append({
                'query': ex,
                'answer': "",
                'retrieved': retrieved,
                'streaming': True
            })
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div class='panel-section'>How it works</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='color:#4b5563; font-size:0.78rem; line-height:1.9;'>
    ① Question → vector embedding<br>
    ② FAISS retrieves relevant jobs<br>
    ③ Llama 3.2 generates answer<br><br>
    <span style='color:#6b7280;'>Embeddings:</span> all-MiniLM-L6-v2<br>
    <span style='color:#6b7280;'>LLM:</span> Llama 3.2 (local, Ollama)<br>
    <span style='color:#6b7280;'>Data:</span> WeWorkRemotely
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.history = []
        st.session_state.submitted_empty = False
        st.rerun()

# ── RIGHT PANEL ────────────────────────────────────────────────────────────────
with right:
    st.markdown("<h2 style='margin-bottom:4px;'>Job Market Q&A</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6b7280; margin-top:0; margin-bottom:1.5rem; font-size:0.9rem;'>Ask anything about remote job market trends, required skills, and hiring companies. <span style='color:#374151;'>· Answers are based on 161 job listings scraped from WeWorkRemotely — not the entire job market.</span></p>", unsafe_allow_html=True)

    if not st.session_state.history:
        st.markdown("""
        <div style='text-align:center; padding:5rem 2rem;'>
            <div style='font-size:2.5rem; margin-bottom:1rem;'>🔍</div>
            <div style='font-size:1rem; color:#4b5563; margin-bottom:0.4rem;'>Ask a question to get started</div>
            <div style='font-size:0.85rem; color:#374151;'>Try one of the examples on the left or type below</div>
        </div>
        """, unsafe_allow_html=True)

    for idx, item in enumerate(st.session_state.history):
        st.markdown(f"""
        <div class='chat-user'>
            <div class='chat-user-bubble'>{item['query']}</div>
        </div>
        """, unsafe_allow_html=True)

        if item.get('streaming') and not item['answer']:
            st.markdown("<div class='chat-ai-label'>🤖 Llama 3.2 · generating...</div>", unsafe_allow_html=True)
            placeholder = st.empty()
            full_answer = ""

            try:
                history = st.session_state.history[:idx]
                prompt, closing_response = build_prompt(item['query'], item['retrieved'], history)

                if closing_response:
                    full_answer = closing_response
                    placeholder.markdown(f"<div class='chat-ai-bubble'>{full_answer.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
                else:
                    response = requests.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": "llama3.2",
                            "prompt": prompt,
                            "stream": True,
                            "options": {
                                "temperature": 0.4,
                                "top_p": 0.9,
                                "num_predict": 500,
                            }
                        },
                        stream=True,
                        timeout=120
                    )
                    for line in response.iter_lines():
                        if line:
                            data = json.loads(line)
                            token = data.get("response", "")
                            full_answer += token
                            placeholder.markdown(f"<div class='chat-ai-bubble'>{full_answer.replace(chr(10), '<br>')}▌</div>", unsafe_allow_html=True)
                            if data.get("done"):
                                break

                    full_answer = post_process_answer(full_answer)
                    placeholder.markdown(f"<div class='chat-ai-bubble'>{full_answer.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

            except Exception as e:
                full_answer = f"❌ Error: {str(e)}"
                placeholder.markdown(f"<div class='chat-ai-bubble'>{full_answer}</div>", unsafe_allow_html=True)

            st.session_state.history[idx]['answer'] = full_answer
            st.session_state.history[idx]['streaming'] = False

        else:
            st.markdown(f"""
            <div class='chat-ai'>
                <div>
                    <div class='chat-ai-label'>🤖 Llama 3.2 · based on {len(item['retrieved'])} job listings</div>
                    <div class='chat-ai-bubble'>{item['answer'].replace(chr(10), '<br>')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with st.expander(f"📄 View {len(item['retrieved'])} source job listings"):
            for i, job in enumerate(item['retrieved'], 1):
                st.markdown(f"""
                <div class='job-card'>
                    <strong>{i}. {job['title']}</strong> @ {job['company']}
                    <span class='badge'>{job['relevance_score']:.2f}</span><br>
                    <span style='color:#6b7280; font-size:0.82rem;'>📍 {job['location']}</span><br><br>
                    <span style='color:#9ca3af;'>{job['description'][:350]}...</span>
                </div>
                """, unsafe_allow_html=True)

    if st.session_state.submitted_empty:
        st.error("Please enter a question")

    with st.form(key="chat_form", clear_on_submit=True):
        cols = st.columns([8, 1])
        with cols[0]:
            query = st.text_input(
                "query",
                placeholder="Ask about job market trends, skills, companies... (Press Enter)",
                label_visibility="collapsed"
            )
        with cols[1]:
            submitted = st.form_submit_button("Send →", use_container_width=True)

    if submitted:
        if query.strip():
            st.session_state.submitted_empty = False
            with st.spinner("🔎 Searching job data..."):
                retrieved = retrieve(query)
            st.session_state.history.append({
                'query': query,
                'answer': "",
                'retrieved': retrieved,
                'streaming': True
            })
            st.rerun()
        else:
            st.session_state.submitted_empty = True
            st.rerun()