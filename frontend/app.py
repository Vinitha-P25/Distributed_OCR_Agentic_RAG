import os
import html
import time

import requests
import streamlit as st


# =========================================================
# 1. CONFIGURATION
# =========================================================

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8001"
).rstrip("/")

st.set_page_config(
    page_title="DocuMind AI | Document Intelligence",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# 2. CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>
    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
    );

    :root {
        --primary: #4F70F5;
        --primary-dark: #3454D1;
        --background: #F4F6FC;
        --text: #17233C;
        --muted: #73809A;
        --border: #E5EAF3;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: var(--background);
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.7rem;
        padding-bottom: 2.5rem;
    }

    [data-testid="stSidebar"] {
        background: #121D35;
        border-right: 1px solid #26334E;
    }

    [data-testid="stSidebar"] * {
        color: #E8EEFF;
    }

    [data-testid="stSidebar"] hr {
        border-color: #34415D;
    }

    .brand {
        font-size: 26px;
        font-weight: 800;
        letter-spacing: -0.8px;
        color: white;
        margin-bottom: 3px;
    }

    .brand span {
        color: #86A4FF;
    }

    .sidebar-description {
        color: #A8B5D0;
        font-size: 11px;
        line-height: 1.8;
        margin-bottom: 25px;
        letter-spacing: 1px;
    }

    .hero {
        background: linear-gradient(
            120deg,
            #172B59 0%,
            #254A91 58%,
            #4269CB 100%
        );
        padding: 34px;
        border-radius: 22px;
        color: white;
        margin-bottom: 26px;
        box-shadow: 0 12px 30px rgba(30, 55, 110, 0.12);
    }

    .hero-eyebrow {
        color: #C5D4FF;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 13px;
    }

    .hero h1 {
        color: white;
        font-size: 36px;
        line-height: 1.25;
        font-weight: 800;
        letter-spacing: -1px;
        margin: 0 0 13px 0;
    }

    .hero p {
        color: #E1E9FF;
        font-size: 14px;
        line-height: 1.9;
        max-width: 740px;
        margin: 0;
    }

    .section-title {
        font-size: 21px;
        font-weight: 750;
        color: var(--text);
        letter-spacing: -0.5px;
        margin: 5px 0;
    }

    .section-description {
        color: var(--muted);
        font-size: 12px;
        line-height: 1.8;
        margin-bottom: 17px;
    }

    .metric-card {
        background: white;
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 19px;
        min-height: 112px;
        box-shadow: 0 4px 18px rgba(29, 47, 83, 0.035);
    }

    .metric-label {
        color: var(--muted);
        font-size: 11px;
        font-weight: 700;
        margin-bottom: 12px;
        letter-spacing: 0.4px;
    }

    .metric-value {
        color: var(--text);
        font-size: 23px;
        font-weight: 800;
        letter-spacing: -0.5px;
        overflow-wrap: anywhere;
    }

    .metric-note {
        color: var(--muted);
        font-size: 10px;
        margin-top: 7px;
    }

    .panel-heading {
        font-size: 16px;
        font-weight: 750;
        color: var(--text);
        margin-bottom: 6px;
    }

    .panel-description {
        color: var(--muted);
        font-size: 12px;
        line-height: 1.8;
        margin-bottom: 16px;
    }

    .chat-question {
        background: #EAF0FF;
        border: 1px solid #D9E4FF;
        border-radius: 16px 16px 4px 16px;
        padding: 16px 19px;
        margin: 18px 0 13px 8%;
        color: #213E80;
        line-height: 1.9;
        overflow-wrap: anywhere;
    }

    .chat-answer {
        background: white;
        border: 1px solid var(--border);
        border-radius: 4px 16px 16px 16px;
        padding: 19px;
        margin: 0 8% 12px 0;
        color: #26334B;
        line-height: 1.9;
        box-shadow: 0 3px 12px rgba(29, 47, 83, 0.035);
        overflow-wrap: anywhere;
    }

    .chat-label {
        font-size: 10px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
        color: #6B7DA5;
    }

    .source-card {
        background: #F8FAFF;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 10px;
        color: #34415A;
        font-size: 12px;
        line-height: 1.9;
        overflow-wrap: anywhere;
    }

    .source-title {
        font-weight: 750;
        color: #284A99;
        margin-bottom: 5px;
    }

    .footer {
        text-align: center;
        color: #8490A6;
        font-size: 11px;
        line-height: 2;
        padding: 25px 0 5px 0;
        border-top: 1px solid var(--border);
        margin-top: 35px;
    }

    div.stButton > button,
    div.stFormSubmitButton > button {
        border-radius: 10px;
        min-height: 43px;
        font-weight: 650;
    }

    div.stButton > button[kind="primary"],
    div.stFormSubmitButton > button[kind="primary"] {
        background: var(--primary);
        border-color: var(--primary);
        color: white;
    }

    div.stButton > button[kind="primary"]:hover,
    div.stFormSubmitButton > button[kind="primary"]:hover {
        background: var(--primary-dark);
        border-color: var(--primary-dark);
    }

    [data-testid="stFileUploader"] {
        background: #F8FAFF;
        border: 1px dashed #AABCF5;
        border-radius: 12px;
        padding: 10px;
    }

    @media (max-width: 768px) {
        .hero {
            padding: 23px;
        }

        .hero h1 {
            font-size: 27px;
        }

        .chat-question {
            margin-left: 2%;
        }

        .chat-answer {
            margin-right: 2%;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 3. SESSION STATE
# =========================================================

DEFAULT_STATE = {
    "chat_history": [],
    "upload_result": None,
    "processed_file": None,
    "task_result": None,
    "backend_status": "Not checked",
}

for key, default_value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = default_value


# =========================================================
# 4. HELPER FUNCTIONS
# =========================================================

def check_backend():
    """Check whether the FastAPI backend is available."""

    try:
        response = requests.get(
            f"{API_URL}/health",
            timeout=5,
        )

        if response.ok:
            return True, response.json()

        return False, {
            "error": f"HTTP {response.status_code}"
        }

    except requests.RequestException as error:
        return False, {"error": str(error)}


def get_task_status(task_id):
    """Retrieve the status of a Celery task."""

    response = requests.get(
        f"{API_URL}/tasks/{task_id}",
        timeout=15,
    )

    response.raise_for_status()

    return response.json()


def extract_task_result(task_data):
    """Extract the result from the task-status response."""

    result = task_data.get("result")

    if isinstance(result, dict):
        return result

    task_result = task_data.get("task_result")

    if isinstance(task_result, dict):
        return task_result

    return {}


def format_status(value):
    """Convert a status into readable text."""

    if value is None:
        return "Unknown"

    return str(value).replace("_", " ").title()


def show_metric(label, value, note=""):
    """Display a dashboard metric card."""

    safe_label = html.escape(str(label))
    safe_value = html.escape(str(value))
    safe_note = html.escape(str(note))

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{safe_label}</div>
            <div class="metric-value">{safe_value}</div>
            <div class="metric-note">{safe_note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sources(sources):
    """Display sources returned by the backend."""

    if not sources:
        st.caption(
            "No source metadata was returned by the backend."
        )
        return

    for index, source in enumerate(sources, start=1):

        if not isinstance(source, dict):
            st.write(f"Source {index}: {source}")
            continue

        document_name = (
            source.get("document_name")
            or source.get("filename")
            or source.get("source")
            or "Document name not provided"
        )

        chunk_index = source.get(
            "chunk_index",
            "Not provided",
        )

        distance = source.get("distance")

        safe_document = html.escape(str(document_name))
        safe_chunk = html.escape(str(chunk_index))

        details = (
            f"<b>Document:</b> {safe_document}<br>"
            f"<b>Chunk:</b> {safe_chunk}"
        )

        if distance is not None:
            safe_distance = html.escape(str(distance))
            details += f"<br><b>Distance:</b> {safe_distance}"

        st.markdown(
            f"""
            <div class="source-card">
                <div class="source-title">📚 Source {index}</div>
                {details}
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# 5. SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div class="brand">DocuMind <span>AI</span></div>
        <div class="sidebar-description">
            DOCUMENT INTELLIGENCE PLATFORM<br>
            EXTRACT · UNDERSTAND · DISCOVER
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### ⚙️ System Status")

    if st.button(
        "Check Backend Connection",
        use_container_width=True,
    ):

        connected, details = check_backend()

        if connected:
            st.session_state.backend_status = "Connected"
            st.success("FastAPI is connected.")
        else:
            st.session_state.backend_status = "Disconnected"
            st.error("Cannot connect to FastAPI.")
            st.caption(details.get("error", "Unknown error"))

    if st.session_state.backend_status == "Connected":
        st.success("● Backend connected")
    elif st.session_state.backend_status == "Disconnected":
        st.error("● Backend disconnected")
    else:
        st.info("● Connection not checked")

    st.caption(f"API endpoint: {API_URL}")

    st.divider()

    st.markdown("### 🧠 AI Pipeline")

    pipeline = [
        ("01", "PDF Upload"),
        ("02", "OCR Extraction"),
        ("03", "Text Chunking"),
        ("04", "Vector Embeddings"),
        ("05", "ChromaDB Retrieval"),
        ("06", "Agentic RAG"),
        ("07", "LLM Answer"),
    ]

    for number, name in pipeline:
        st.markdown(
            f"""
            <div style="
                display:flex;
                align-items:center;
                gap:12px;
                margin:12px 0;
                font-size:12px;
            ">
                <div style="
                    background:#263B63;
                    color:#AFC5FF;
                    border-radius:8px;
                    padding:6px 8px;
                    font-weight:700;
                ">{number}</div>
                <div>{name}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    st.markdown("### 🛠 Technology Stack")

    st.caption("Frontend · Streamlit")
    st.caption("API · FastAPI")
    st.caption("Background tasks · Celery + Redis")
    st.caption("Metadata · PostgreSQL")
    st.caption("OCR · Pytesseract")
    st.caption("Vector database · ChromaDB")
    st.caption("LLM · Ollama")

    st.divider()

    if st.button(
        "Clear Conversation",
        use_container_width=True,
    ):
        st.session_state.chat_history = []
        st.rerun()


# =========================================================
# 6. HERO SECTION
# =========================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-eyebrow">
            AI-POWERED DOCUMENT INTELLIGENCE
        </div>
        <h1>Your documents.<br>Understood intelligently.</h1>
        <p>
            Upload a PDF, extract its contents, and ask natural-language
            questions. Explore document information using retrieval,
            language models, and agentic reasoning.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 7. DASHBOARD METRICS
# =========================================================

upload_result = st.session_state.upload_result or {}
task_result = st.session_state.task_result or {}
task_payload = extract_task_result(task_result)

filename = (
    upload_result.get("filename")
    or upload_result.get("original_filename")
    or st.session_state.processed_file
    or "No document"
)

# Use a single, consistently defined status variable.
latest_status = str(
    task_result.get("status")
    or upload_result.get("status")
    or "Not uploaded"
).upper()

indexed_chunks = (
    task_payload.get("chunks_created")
    or task_payload.get("indexed_chunks")
    or upload_result.get("chunks_created")
    or upload_result.get("indexed_chunks")
    or 0
)

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

with metric_col1:
    display_filename = (
        filename
        if len(str(filename)) <= 22
        else str(filename)[:19] + "..."
    )

    show_metric(
        "📄 CURRENT DOCUMENT",
        display_filename,
        "Selected document",
    )

with metric_col2:
    show_metric(
        "🧩 INDEXED CHUNKS",
        indexed_chunks,
        "Chunks reported by processing",
    )

with metric_col3:
    show_metric(
        "⚙️ PROCESSING STATUS",
        format_status(latest_status),
        "Latest available status",
    )

with metric_col4:
    show_metric(
        "💬 CONVERSATION",
        len(st.session_state.chat_history),
        "Questions in this session",
    )


st.markdown("<br>", unsafe_allow_html=True)


# =========================================================
# 8. MAIN LAYOUT
# =========================================================

upload_column, assistant_column = st.columns(
    [0.85, 1.5],
    gap="large",
)


# =========================================================
# 9. DOCUMENT WORKSPACE
# =========================================================

with upload_column:

    st.markdown(
        """
        <div class="section-title">Document Workspace</div>
        <div class="section-description">
            Upload a PDF to begin analysing its contents.
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):

        st.markdown(
            """
            <div class="panel-heading">📤 Upload your document</div>
            <div class="panel-description">
                Select a PDF. OCR and indexing will run in the background.
            </div>
            """,
            unsafe_allow_html=True,
        )

        uploaded_file = st.file_uploader(
            "Choose a PDF",
            type=["pdf"],
            help="Select a readable PDF document.",
            key="document_uploader",
        )

        if uploaded_file is not None:

            file_size_kb = uploaded_file.size / 1024

            st.info(
                f"**Selected:** {uploaded_file.name}  \n"
                f"**Size:** {file_size_kb:.1f} KB"
            )

            if st.button(
                "Upload and Process",
                type="primary",
                use_container_width=True,
                key="upload_pdf_button",
            ):

                try:
                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "application/pdf",
                        )
                    }

                    with st.spinner(
                        "Submitting your document to the backend..."
                    ):
                        response = requests.post(
                            f"{API_URL}/upload",
                            files=files,
                            timeout=120,
                        )

                    if response.status_code not in (200, 201, 202):
                        st.error(
                            f"Upload failed ({response.status_code}): "
                            f"{response.text}"
                        )

                    else:
                        result = response.json()

                        st.session_state.upload_result = result
                        st.session_state.processed_file = (
                            result.get("filename")
                            or result.get("original_filename")
                            or uploaded_file.name
                        )

                        st.session_state.task_result = None

                        task_id = result.get("task_id")

                        if task_id:
                            st.success(
                                "Document accepted. Background processing "
                                "has been requested."
                            )
                        else:
                            st.warning(
                                "The API did not return a task ID. "
                                "Review the upload response."
                            )

                        st.rerun()

                except requests.RequestException as error:
                    st.error(f"Upload request failed: {error}")

        # -------------------------------------------------
        # BACKGROUND PROCESSING
        # -------------------------------------------------

        current_upload = st.session_state.upload_result or {}
        current_task_id = current_upload.get("task_id")

        if current_task_id:

            st.divider()
            st.markdown("**⚙️ Background Processing**")

            st.caption(f"Task ID: `{current_task_id}`")

            if st.button(
                "🔄 Refresh Processing Status",
                use_container_width=True,
                key="refresh_task_status",
            ):

                try:
                    task_data = get_task_status(current_task_id)

                    st.session_state.task_result = task_data

                    # Extract status from common response formats.
                    raw_status = task_data.get("status")

                    if not raw_status:
                        raw_status = task_data.get("state")

                    if not raw_status:
                        raw_status = task_data.get("task_status")

                    normalized_status = str(
                        raw_status or "UNKNOWN"
                    ).upper()

                    if normalized_status in (
                        "SUCCESS",
                        "COMPLETED",
                    ):
                        st.success(
                            "Document processing completed."
                        )

                    elif normalized_status in (
                        "FAILURE",
                        "FAILED",
                    ):
                        st.error(
                            task_data.get("error")
                            or task_data.get("message")
                            or "The background task failed."
                        )

                    elif normalized_status in (
                        "PENDING",
                        "RECEIVED",
                        "STARTED",
                        "RETRY",
                        "PROCESSING",
                    ):
                        st.info(
                            "Processing is still in progress: "
                            f"{format_status(normalized_status)}"
                        )

                    else:
                        st.info(
                            "Task response received. "
                            f"Status: {format_status(normalized_status)}"
                        )

                    st.rerun()

                except requests.RequestException as error:
                    st.error(
                        f"Could not retrieve task status: {error}"
                    )

            # Recalculate the task result after every Streamlit rerun.
            current_task = st.session_state.task_result or {}

            current_task_status = str(
                current_task.get("status")
                or current_task.get("state")
                or current_task.get("task_status")
                or ""
            ).upper()

            if current_task_status in ("SUCCESS", "COMPLETED"):
                st.success("Last reported status: Completed")

            elif current_task_status in ("FAILURE", "FAILED"):
                st.error("Last reported status: Failed")

            elif current_task_status:
                st.info(
                    "Last reported status: "
                    f"{format_status(current_task_status)}"
                )

        # -------------------------------------------------
        # DOCUMENT INFORMATION
        # -------------------------------------------------

        if st.session_state.upload_result:

            st.divider()
            st.markdown("**📊 Document Information**")

            current_upload = st.session_state.upload_result
            current_task = st.session_state.task_result or {}
            current_payload = extract_task_result(current_task)

            st.write(
                "**Filename:**",
                current_upload.get("filename")
                or current_upload.get("original_filename")
                or st.session_state.processed_file
                or "Unknown",
            )

            document_id = current_upload.get("document_id")

            if document_id:
                st.caption(f"Document ID: {document_id}")

            actual_chunks = (
                current_payload.get("chunks_created")
                or current_payload.get("indexed_chunks")
                or current_upload.get("chunks_created")
                or current_upload.get("indexed_chunks")
                or 0
            )

            st.metric(
                "Indexed Chunks",
                actual_chunks,
            )

            extracted_text = (
                current_payload.get("extracted_text_preview")
                or current_payload.get("extracted_text")
                or current_upload.get("extracted_text_preview")
            )

            if extracted_text:
                with st.expander("📖 View Extracted Text"):
                    st.text(str(extracted_text))

            # latest_status is defined globally above and refreshed here.
            latest_status = str(
                current_task.get("status")
                or current_task.get("state")
                or current_task.get("task_status")
                or current_upload.get("status")
                or "UNKNOWN"
            ).upper()

            if (
                latest_status in ("SUCCESS", "COMPLETED")
                and not extracted_text
            ):
                st.caption(
                    "Processing completed. The task response does not "
                    "currently include an extracted-text preview."
                )


# =========================================================
# 10. AI QUESTION-ANSWER PANEL
# =========================================================

with assistant_column:

    st.markdown(
        """
        <div class="section-title">AI Research Assistant</div>
        <div class="section-description">
            Ask questions and explore answers with the available sources.
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):

        st.markdown(
            """
            <div class="panel-heading">💬 Ask your documents</div>
            <div class="panel-description">
                Ask questions in natural language and explore the answers
                generated by your Agentic RAG pipeline.
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form(
            "question_form",
            clear_on_submit=True,
        ):

            question = st.text_area(
                "Your question",
                placeholder=(
                    "Example: What is the main topic of this document?"
                ),
                height=95,
            )

            ask_button = st.form_submit_button(
                "✨ Generate Answer",
                type="primary",
                use_container_width=True,
            )

        if ask_button:

            if not question.strip():
                st.warning("Please enter a question.")

            elif not st.session_state.upload_result:
                st.warning(
                    "Upload a document before asking a question."
                )

            else:

                current_task = st.session_state.task_result or {}

                current_task_status = str(
                    current_task.get("status")
                    or current_task.get("state")
                    or current_task.get("task_status")
                    or ""
                ).upper()

                if current_task_status in ("FAILURE", "FAILED"):

                    st.warning(
                        "The latest document-processing task failed. "
                        "Refresh the status and review the error."
                    )

                else:

                    try:
                        with st.spinner(
                            "Searching documents and generating an answer..."
                        ):
                            response = requests.post(
                                f"{API_URL}/ask",
                                json={
                                    "question": question.strip()
                                },
                                timeout=600,
                            )

                        if response.ok:

                            result = response.json()
                            answer_data = result.get("answer")

                            if isinstance(answer_data, dict):

                                answer = answer_data.get(
                                    "answer",
                                    "No answer was returned.",
                                )

                                sources = answer_data.get(
                                    "sources",
                                    [],
                                )

                            else:

                                answer = (
                                    answer_data
                                    or "No answer was returned."
                                )

                                sources = result.get(
                                    "sources",
                                    [],
                                )

                            st.session_state.chat_history.append(
                                {
                                    "question": question.strip(),
                                    "answer": str(answer),
                                    "sources": sources,
                                    "agent_decision": result.get(
                                        "agent_decision"
                                    ),
                                }
                            )

                            st.rerun()

                        else:
                            st.error(
                                f"Question failed "
                                f"({response.status_code}): "
                                f"{response.text}"
                            )

                    except requests.RequestException as error:
                        st.error(
                            f"Question request failed: {error}"
                        )

        st.divider()

        st.markdown("**📝 Conversation**")

        if not st.session_state.chat_history:
            st.info(
                "Your conversation will appear here after your first question."
            )

        for index, chat in enumerate(
            st.session_state.chat_history,
            start=1,
        ):

            safe_question = html.escape(
                str(chat["question"])
            )

            safe_answer = html.escape(
                str(chat["answer"])
            ).replace("\n", "<br>")

            st.markdown(
                f"""
                <div class="chat-question">
                    <div class="chat-label">
                        You · Question {index}
                    </div>
                    {safe_question}
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div class="chat-answer">
                    <div class="chat-label">
                        ✨ DocuMind AI
                    </div>
                    {safe_answer}
                </div>
                """,
                unsafe_allow_html=True,
            )

            if chat.get("agent_decision"):
                st.caption(
                    "Agent decision: "
                    + str(chat["agent_decision"])
                )

            sources = chat.get("sources", [])

            if sources:
                with st.expander(
                    f"📚 View Sources for Answer {index}"
                ):
                    render_sources(sources)

            st.markdown("---")


# =========================================================
# 11. FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        DOCUMIND AI · DOCUMENT INTELLIGENCE PLATFORM<br><br>
        Streamlit · FastAPI · PostgreSQL · Celery · Redis ·
        Tesseract OCR · Sentence Transformers · ChromaDB · Ollama
    </div>
    """,
    unsafe_allow_html=True,
)