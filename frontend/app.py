"""
frontend/app.py
-----------------
The Streamlit website. Unlike the simple version, this one does NOT
run the AI logic itself -- it just calls the FastAPI backend over HTTP
and displays the results.
"""

import streamlit as st
import requests
import uuid

# Locally this falls back to localhost. On Streamlit Community Cloud,
# set BACKEND_URL in your app's "Secrets" to your deployed Render URL.
BACKEND_URL = st.secrets.get("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="VeritasPrep AI", page_icon="🧭")
st.title("🧭 VeritasPrep AI")
st.caption("A resume-grounded interview coach that shows its work.")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "resume_ready" not in st.session_state:
    st.session_state.resume_ready = False
if "messages" not in st.session_state:
    st.session_state.messages = []

uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")

if uploaded_file and not st.session_state.resume_ready:
    with st.spinner("Waking up the backend and indexing your resume (can take up to a minute on first use)..."):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}

        response = None
        last_error = None
        for attempt in range(3):
            try:
                response = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=70)
                break
            except requests.exceptions.RequestException as e:
                last_error = e
                response = None

    if response is None:
        st.error(
            f"Could not reach the backend after several tries. "
            f"Last error: {last_error}. "
            f"Double-check BACKEND_URL in your app's Secrets, and that "
            f"{BACKEND_URL}/docs loads in a browser."
        )
    elif response.status_code == 200:
        data = response.json()
        st.session_state.resume_ready = True
        st.success(f"Resume indexed into {data['chunks']} chunks. Ask away!")
    else:
        st.error("Upload failed. Is the backend running?")

if st.session_state.resume_ready:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    question = st.chat_input("Ask an interview prep question about your resume...")

    if question:
        with st.chat_message("user"):
            st.write(question)
        st.session_state.messages.append({"role": "user", "content": question})

        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={"session_id": st.session_state.session_id, "question": question},
                    timeout=70,
                )
            except requests.exceptions.RequestException as e:
                response = None
                st.error(f"Could not reach the backend: {e}")

        if response is not None and response.status_code == 200:
            data = response.json()
            answer = data["answer"]
            scores = data["scores"]

            with st.chat_message("assistant"):
                st.write(answer)
                st.progress(min(scores["groundedness"], 1.0))
                st.caption(
                    f"Groundedness: {scores['groundedness']} | "
                    f"Answer relevance: {scores['answer_relevance']}"
                )
                with st.expander("Retrieved resume chunks used for this answer"):
                    for i, chunk in enumerate(data["retrieved_chunks"], 1):
                        st.markdown(f"**Chunk {i}:** {chunk}")

            st.session_state.messages.append({"role": "assistant", "content": answer})
        else:
            st.error("Something went wrong calling the backend.")
else:
    st.info("Upload a resume to get started. Make sure the backend is running at " + BACKEND_URL)