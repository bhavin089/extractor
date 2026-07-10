import json
import statistics
from pathlib import Path
from ingest import read_document
from classifier import classify
from extractor import extract_attributes
from backend_schema import ExtractionResult

REVIEW_THRESHOLD = 0.70

def process_file(path: str):
    text, meta = read_document(path)
    doc_type, cls_conf, _ = classify(text)
    attrs = extract_attributes(text)
    confidences = [v.confidence for v in attrs.values() if v.confidence > 0]
    overall = round((cls_conf + (statistics.mean(confidences) if confidences else 0)) / 2, 2)
    needs_review = overall < REVIEW_THRESHOLD or any(v.needs_review for v in attrs.values())
    return ExtractionResult(
        source_file=Path(path).name,
        document_type=doc_type,
        classification_confidence=cls_conf,
        attributes=attrs,
        confidence_overall=overall,
        needs_review=needs_review,
    )

def process_folder(folder: str):
    results = []
    for path in Path(folder).glob("**/*"):
        if path.is_file() and path.name not in ["results.json", "results.csv"]:
            try:
                results.append(process_file(str(path)).to_dict())
            except Exception as e:
                results.append({"source_file": path.name, "error": str(e)})
    return results

def save_results(results, out_json="results.json"):
    Path(out_json).write_text(json.dumps(results, indent=2))
    return out_json
