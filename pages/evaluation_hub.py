
import streamlit as st
import pandas as pd
import io
from datetime import datetime

# -------------------------------
# Page configuration
# -------------------------------
st.set_page_config(
    page_title="Evaluation Hub",
    page_icon="🧪",
    layout="wide"
)

# -------------------------------
# Custom styling
# -------------------------------
st.markdown("""
<style>
.stApp {
    background-color: #f5f7fb;
}

[data-testid="stSidebar"] {
    background-color: #101a33;
}

[data-testid="stSidebar"] * {
    color: #eef2ff;
}

.page-title {
    font-size: 2.1rem;
    font-weight: 800;
    color: #172554;
    margin-bottom: 0.25rem;
}

.page-subtitle {
    color: #64748b;
    margin-bottom: 1.5rem;
}

.panel {
    background: white;
    border: 1px solid #e2e8f0;
    padding: 1.2rem;
    border-radius: 14px;
}

.status-ready {
    background: #dcfce7;
    color: #166534;
    padding: 0.7rem;
    border-radius: 10px;
    font-weight: 600;
}

div.stButton > button {
    border-radius: 10px;
    font-weight: 600;
    min-height: 2.7rem;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Page header
# -------------------------------
st.markdown(
    '<div class="page-title">Evaluation Hub</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="page-subtitle">'
    'Evaluate one AI response or process an entire CSV dataset.'
    '</div>',
    unsafe_allow_html=True
)

# -------------------------------
# Evaluation status
# -------------------------------
if "single_result" not in st.session_state:
    st.session_state.single_result = None

if "batch_results" not in st.session_state:
    st.session_state.batch_results = None

# -------------------------------
# Evaluation mode tabs
# -------------------------------
single_tab, batch_tab = st.tabs([
    "📝 Single Evaluation",
    "📁 Batch Evaluation"
])

# ==================================================
# SINGLE EVALUATION
# ==================================================
with single_tab:
    left, right = st.columns([2.2, 1], gap="large")

    with left:
        st.subheader("Evaluate a response")
        st.write(
            "Enter the question and AI-generated response. "
            "A reference answer or source document is optional."
        )

        with st.form("single_evaluation_form"):
            question = st.text_area(
                "Question",
                placeholder="Example: What is retrieval-augmented generation?",
                height=110
            )

            ai_response = st.text_area(
                "AI Response",
                placeholder="Paste the AI-generated answer here...",
                height=180
            )

            reference_answer = st.text_area(
                "Reference Answer (optional)",
                placeholder="Enter the expected answer, if available...",
                height=110
            )

            reference_file = st.file_uploader(
                "Reference Source (optional)",
                type=["pdf", "txt", "docx"],
                help="Upload a reference document if your backend supports it."
            )

            submitted = st.form_submit_button(
                "🚀 Run Evaluation",
                type="primary",
                width="stretch"
            )

        if submitted:
            if not question.strip():
                st.error("Please enter a question.")
            elif not ai_response.strip():
                st.error("Please enter an AI response.")
            else:
                # Store the submission for backend integration.
                st.session_state.single_result = {
                    "id": datetime.now().strftime("EV-%Y%m%d-%H%M%S"),
                    "question": question.strip(),
                    "ai_response": ai_response.strip(),
                    "reference_answer": reference_answer.strip(),
                    "reference_filename": (
                        reference_file.name if reference_file else None
                    ),
                    "submitted_at": datetime.now().isoformat(timespec="seconds"),
                    "status": "Pending backend evaluation"
                }

                st.success(
                    "Submission validated! Connect your evaluation API "
                    "to run the four Judge Agents."
                )

    with right:
        st.subheader("Evaluation workflow")

        st.markdown("""
        <div class="panel">
            <p>① <b>Submit response</b><br>
            <small>Enter the question and AI answer.</small></p>
            <hr>
            <p>② <b>Four Judge Agents</b><br>
            <small>Evaluate the response using your backend.</small></p>
            <hr>
            <p>③ <b>Review results</b><br>
            <small>Inspect scores, evidence, and recommendations.</small></p>
        </div>
        """, unsafe_allow_html=True)

        st.write("")
        st.markdown(
            '<div class="status-ready">● Ready to evaluate</div>',
            unsafe_allow_html=True
        )

        st.caption(
            "Status changes to completed only after the backend "
            "returns a successful result."
        )

    # Display most recent submission
    if st.session_state.single_result:
        result = st.session_state.single_result

        st.divider()
        st.subheader("Latest submission")

        c1, c2 = st.columns(2)
        c1.metric("Submission ID", result["id"])
        c2.metric("Status", result["status"])

        with st.expander("View submitted content"):
            st.markdown("**Question**")
            st.write(result["question"])

            st.markdown("**AI Response**")
            st.write(result["ai_response"])

            st.markdown("**Reference Answer**")
            st.write(result["reference_answer"] or "Not provided")

            if result["reference_filename"]:
                st.write("Reference file:", result["reference_filename"])

# ==================================================
# BATCH EVALUATION
# ==================================================
with batch_tab:
    st.subheader("Batch evaluation")
    st.write(
        "Upload a CSV containing questions and AI responses. "
        "Preview and validate the records before processing."
    )

    uploaded_csv = st.file_uploader(
        "Upload CSV dataset",
        type=["csv"],
        key="batch_csv",
        help=(
            "Required columns: question, ai_response. "
            "Optional column: reference_answer."
        )
    )

    if uploaded_csv is not None:
        try:
            df = pd.read_csv(uploaded_csv)

            # Normalize column names for validation.
            df.columns = [
                str(column).strip().lower()
                for column in df.columns
            ]

            required_columns = {"question", "ai_response"}
            missing_columns = required_columns - set(df.columns)

            if missing_columns:
                st.error(
                    "Missing required columns: "
                    + ", ".join(sorted(missing_columns))
                )
                st.info(
                    "Required CSV headers: question, ai_response. "
                    "reference_answer is optional."
                )
            elif df.empty:
                st.warning("The CSV file contains no records.")
            else:
                st.success(
                    f"Loaded {len(df)} records from {uploaded_csv.name}."
                )

                # Normalize empty cells and validate records.
                for column in required_columns:
                    df[column] = df[column].fillna("").astype(str)

                df["question"] = df["question"].str.strip()
                df["ai_response"] = df["ai_response"].str.strip()

                df["validation_status"] = df.apply(
                    lambda row: (
                        "Valid"
                        if row["question"] and row["ai_response"]
                        else "Invalid: missing question or AI response"
                    ),
                    axis=1
                )

                valid_count = int(
                    (df["validation_status"] == "Valid").sum()
                )
                invalid_count = len(df) - valid_count

                m1, m2, m3 = st.columns(3)
                m1.metric("Total records", len(df))
                m2.metric("Valid records", valid_count)
                m3.metric("Invalid records", invalid_count)

                st.markdown("#### Dataset preview")
                st.dataframe(
                    df.head(100),
                    width="stretch",
                    hide_index=True
                )

                if invalid_count:
                    st.warning(
                        f"{invalid_count} record(s) need correction "
                        "before they can be evaluated."
                    )

                st.download_button(
                    "⬇️ Download validated preview",
                    data=df.to_csv(index=False).encode("utf-8"),
                    file_name="validated_evaluation_dataset.csv",
                    mime="text/csv"
                )

                if st.button(
                    "🚀 Run Batch Evaluation",
                    type="primary",
                    width="stretch",
                    disabled=(valid_count == 0)
                ):
                    valid_df = df[
                        df["validation_status"] == "Valid"
                    ].copy()

                    # Save validated records for API integration.
                    st.session_state.batch_results = valid_df

                    st.info(
                        f"{len(valid_df)} valid records are ready. "
                        "Connect your batch evaluation API to process them."
                    )

        except (pd.errors.ParserError, UnicodeDecodeError, ValueError) as e:
            st.error(f"Unable to read the CSV file: {e}")

        except Exception as e:
            st.error(f"Unexpected error while processing CSV: {e}")

    else:
        st.info(
            "Upload a CSV file to preview and validate your dataset."
        )

        example_df = pd.DataFrame({
            "question": [
                "What is AI?",
                "What is RAG?"
            ],
            "ai_response": [
                "AI is a field of computer science.",
                "RAG combines retrieval with generation."
            ],
            "reference_answer": [
                "Optional reference answer",
                "Optional reference answer"
            ]
        })

        st.markdown("#### Expected CSV format")
        st.dataframe(example_df, width="stretch", hide_index=True)

        st.download_button(
            "⬇️ Download sample CSV",
            data=example_df.to_csv(index=False).encode("utf-8"),
            file_name="sample_evaluation_dataset.csv",
            mime="text/csv"
        )

# -------------------------------
# Footer
# -------------------------------
st.divider()
st.caption(
    "AI Response Evaluator • Team 5 • Evaluation Hub prototype"
)
