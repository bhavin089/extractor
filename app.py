import os, json, tempfile
from pathlib import Path
import pandas as pd
import streamlit as st
from agent import process_file

st.set_page_config(page_title="Engineering Document Intelligence Agent", layout="wide")
st.title("Engineering Document Intelligence Agent")
st.caption("GOH-UC-007 prototype: classify, extract, score and review engineering document attributes")

uploaded = st.file_uploader(
    "Upload engineering documents",
    type=["pdf","png","jpg","jpeg","tif","tiff","docx","xlsx","xlsm","txt","csv"],
    accept_multiple_files=True,
)
threshold = st.slider("Human review threshold", 0.0, 1.0, 0.70, 0.05)

if uploaded:
    rows = []
    full = []
    for file in uploaded:
        suffix = Path(file.name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file.read())
            tmp_path = tmp.name
        result = process_file(tmp_path).to_dict()
        result["source_file"] = file.name
        result["needs_review"] = result["confidence_overall"] < threshold or result["needs_review"]
        full.append(result)
        flat = {
            "source_file": result["source_file"],
            "document_type": result["document_type"],
            "classification_confidence": result["classification_confidence"],
            "confidence_overall": result["confidence_overall"],
            "needs_review": result["needs_review"],
        }
        for k,v in result["attributes"].items():
            flat[k] = v["value"]
            flat[f"{k}_confidence"] = v["confidence"]
        rows.append(flat)

    df = pd.DataFrame(rows)
    search = st.text_input("Search extracted records")
    view = df.copy()
    if search:
        mask = view.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
        view = view[mask]

    st.subheader("Review dashboard")
    st.dataframe(view, use_container_width=True)

    st.subheader("Human review queue")
    st.dataframe(df[df["needs_review"] == True], use_container_width=True)

    st.download_button("Download JSON", json.dumps(full, indent=2), file_name="engineering_doc_extractions.json")
    st.download_button("Download CSV", df.to_csv(index=False), file_name="engineering_doc_extractions.csv")

    with st.expander("Full machine-readable output"):
        st.json(full)
else:
    st.info("Upload at least one document to start.")
