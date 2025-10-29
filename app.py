# app.py
import os
from dotenv import load_dotenv

# Load .env before anything else so services see the key
load_dotenv(override=True)

import pandas as pd
import streamlit as st
from core.schemas import Ticket, ClassificationRequest, ClassificationResult
from core.constants import DEFAULT_CATEGORIES
from services.classifier import classify
from services.crm import push_to_crm, log_path

st.set_page_config(page_title="Vonazon – Ticket Classifier", page_icon="🎫", layout="centered")
st.title("🎫 Ticket Classifier")
st.caption("Classify support tickets using DeepSeek when available; fall back to deterministic rules if not.")

with st.expander("🔧 Configuration", expanded=False):
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    st.write("**DeepSeek API key present:**", "✅" if api_key else "❌ (not set)")
    model = st.text_input("Model", os.getenv("DEEPSEEK_MODEL", "deepseek-chat"))
    temperature = st.slider("Temperature", 0.0, 1.0, 0.0, 0.1)
    categories_text = st.text_input("Categories (comma separated)", ", ".join(DEFAULT_CATEGORIES))

st.subheader("Enter tickets (one per line)")
sample = """My invoice shows an extra charge that I didn’t authorize.
I can’t log in to my account — the system says my password is invalid.
I’d like to learn more about your premium service plans.
When will my refund be processed?
"""
text = st.text_area("Tickets", value=sample, height=160)

# Keep results in session to enable "Push to CRM"
if "results_df" not in st.session_state:
    st.session_state.results_df = None

# Classify button with spinner
classify_clicked = st.button("Classify", key="classify_btn", type="primary")

if classify_clicked:
    try:
        with st.spinner("Classifying tickets…"):
            tickets = [t.strip() for t in text.split("\n") if t.strip()]
            categories = [c.strip() for c in (categories_text or "").split(",") if c.strip()]
            req = ClassificationRequest(
                tickets=[Ticket(id=f"T{i+1}", text=t) for i, t in enumerate(tickets)],
                categories=categories,
                model=model,
                temperature=temperature,
            )
            results = classify(req)

            df = pd.DataFrame([{
                "ticket_id": r.ticket_id,
                "ticket_text": r.ticket_text,
                "category": r.category,
                "confidence": round(r.confidence, 3),
                "explanation": r.explanation or ""
            } for r in results])

        # Status message depends on API key presence
        if os.getenv("DEEPSEEK_API_KEY"):
            st.success("✅ Classified using DeepSeek AI model.")
        else:
            st.warning("⚙️ Classified using rule-based fallback.")

        st.session_state.results_df = df
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Classification failed: {e}")

st.divider()

# Push-to-CRM section
st.subheader("Push results to CRM (mock)")
disabled_push = st.session_state.results_df is None
col1, col2 = st.columns([1,1])

with col1:
    push_clicked = st.button("Push to CRM", disabled=disabled_push)
with col2:
    # Offer last log for download even before pushing (if exists)
    log_file = log_path()
    if os.path.exists(log_file):
        with open(log_file, "rb") as f:
            st.download_button("Download CRM Log (JSONL)", f, file_name="push_log.jsonl", mime="application/jsonl")

if push_clicked and not disabled_push:
    try:
        with st.spinner("Pushing to CRM…"):
            # Convert df back into result objects
            rows = list(st.session_state.results_df.itertuples(index=False))
            batch = [
                ClassificationResult(
                    ticket_id=row.ticket_id,
                    ticket_text=row.ticket_text,
                    category=row.category,
                    confidence=float(row.confidence)
                )
                for row in rows
            ]
            written = push_to_crm(batch)

        st.success(f"✅ Pushed {written} record(s) to CRM log.")
    except Exception as e:
        st.error(f"Push failed: {e}")

st.caption("CRM is simulated via JSON Lines at:  `data/push_log.jsonl`")
