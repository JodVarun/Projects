"""
AI Chat Tab: Natural language Q&A with conversation history.
"""

import streamlit as st
import pandas as pd
from core.chat import chat_with_data, get_suggested_questions


def render_chat_tab(df: pd.DataFrame):
    """Render the AI chat interface."""

    # ── Init chat history ───────────────────────────────────────────
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    api_key = st.session_state.get('groq_api_key', '')

    if not api_key:
        st.markdown("""
        <div style='text-align:center; padding:60px 20px;'>
            <div style='width:48px; height:48px; border-radius:12px; margin:0 auto 16px;
                        background: linear-gradient(135deg, #7C3AED20, #7C3AED08);
                        border: 1px solid #7C3AED30; display:flex; align-items:center;
                        justify-content:center;'>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7C3AED" stroke-width="2">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0110 0v4"/>
                </svg>
            </div>
            <h3 style='color:#E2E8F0; margin-top:0;'>API Key Required</h3>
            <p style='color:#94A3B8;'>Enter your Groq API key in the sidebar to start chatting with your data.</p>
            <p style='color:#64748B; font-size:0.85rem;'>Get a free key at
            <a href='https://console.groq.com/' style='color:#7C3AED;'>console.groq.com</a></p>
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Header ──────────────────────────────────────────────────────
    st.markdown("""
    <div style='text-align:center; margin-bottom:24px;'>
        <h3 style='color:#E2E8F0; margin:0 0 4px;'>Chat with Your Data</h3>
        <p style='color:#94A3B8; font-size:0.88rem;'>Ask questions in plain English. Powered by Groq AI.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Suggested Questions ─────────────────────────────────────────
    suggestions = get_suggested_questions(df)
    if suggestions and not st.session_state['chat_history']:
        st.markdown("**Suggested questions:**")
        cols = st.columns(min(len(suggestions), 3))
        for i, q in enumerate(suggestions[:3]):
            with cols[i]:
                if st.button(q, key=f"suggest_{i}", use_container_width=True):
                    _process_question(df, q, api_key)
                    st.rerun()

        if len(suggestions) > 3:
            cols2 = st.columns(min(len(suggestions) - 3, 3))
            for i, q in enumerate(suggestions[3:6]):
                with cols2[i]:
                    if st.button(q, key=f"suggest2_{i}", use_container_width=True):
                        _process_question(df, q, api_key)
                        st.rerun()

    st.markdown("---")

    # ── Chat History ────────────────────────────────────────────────
    chat_container = st.container(height=400)
    with chat_container:
        for msg in st.session_state['chat_history']:
            if msg['role'] == 'user':
                st.markdown(f"""
                <div style='background:#7C3AED15; border-radius:10px; padding:12px 16px;
                            margin:8px 0; border:1px solid #7C3AED20;'>
                    <span style='color:#A78BFA; font-size:0.72rem; font-weight:500;
                                text-transform:uppercase; letter-spacing:0.04em;'>You</span><br>
                    <span style='color:#E2E8F0; font-size:0.9rem;'>{msg['content']}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='background:#06B6D408; border-radius:10px; padding:12px 16px;
                            margin:8px 0; border:1px solid #06B6D415;'>
                    <span style='color:#06B6D4; font-size:0.72rem; font-weight:500;
                                text-transform:uppercase; letter-spacing:0.04em;'>AI Analyst</span><br>
                    <span style='color:#E2E8F0; font-size:0.9rem;'>{msg['content']}</span>
                </div>
                """, unsafe_allow_html=True)

        if not st.session_state['chat_history']:
            st.markdown("""
            <div style='text-align:center; padding:40px; color:#64748B;'>
                <p>No messages yet. Ask a question about your data.</p>
            </div>
            """, unsafe_allow_html=True)

    # ── Input ───────────────────────────────────────────────────────
    input_cols = st.columns([5, 1])
    with input_cols[0]:
        user_input = st.text_input(
            "Ask a question",
            placeholder="e.g., What's the average revenue by category?",
            label_visibility="collapsed",
            key="chat_input"
        )
    with input_cols[1]:
        send_btn = st.button("Send", type="primary", use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state['chat_history'] = []
            st.rerun()
    with col_b:
        reasoning = st.toggle("Show reasoning", value=True, key="chat_reasoning")

    if send_btn and user_input:
        _process_question(df, user_input, api_key)
        st.rerun()


def _process_question(df: pd.DataFrame, question: str, api_key: str):
    """Process a question and add to chat history."""
    st.session_state['chat_history'].append({
        'role': 'user',
        'content': question
    })

    history = [
        {'question': h['content'], 'answer': h.get('content', '')}
        for h in st.session_state['chat_history']
        if h['role'] == 'user'
    ]

    result = chat_with_data(df, question, api_key, history[:-1])

    st.session_state['chat_history'].append({
        'role': 'assistant',
        'content': result['content']
    })
