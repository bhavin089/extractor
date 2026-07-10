# Engineering Document Intelligence Agent Prototype

This package gives you a ready-to-run prototype agent for **GOH-UC-007: Intelligent Classification and Attribute Extraction from Unstructured Engineering Technical Documents**.

## What the agent does
- Ingests PDFs, images, DOCX, XLSX, TXT and CSV engineering document files.
- Classifies at least 3 document types: engineering drawing, material datasheet, inspection report, change notice, test certificate and specification.
- Extracts common engineering attributes: part number, revision, material, dimensions, tolerances, surface finish, standards, certificate/inspection identifiers and dates.
- Generates confidence scores and flags low-confidence attributes for human review.
- Provides a searchable Streamlit review dashboard.
- Exports structured machine-readable JSON and CSV.

## Quick start
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Recommended enterprise architecture
1. Upload documents into SharePoint, PLM, ERP, DMS, Windchill, Teamcenter, SAP DMS, or local folder.
2. Power Automate or an API sends files to this agent service.
3. The agent performs OCR/text extraction, classification, attribute extraction and confidence scoring.
4. Extracted records are stored in Dataverse, SQL, SharePoint Lists or a PLM staging table.
5. Low-confidence records are routed to engineering/quality reviewers.
6. Approved attributes are synchronized back to PLM/ERP using controlled APIs.

## Notes
This prototype uses lightweight local rules and optional OCR hooks. For production, replace regex extraction with Azure AI Document Intelligence custom extraction, Azure AI Search, Azure OpenAI function calling, and a governed human-in-the-loop workflow.
