import re

KEYWORDS = {
    "engineering_drawing": ["drawing", "scale", "projection", "title block", "dimension", "tolerance", "rev", "sheet"],
    "material_datasheet": ["material", "datasheet", "chemical composition", "mechanical properties", "grade", "density"],
    "inspection_report": ["inspection", "inspector", "acceptance", "rejection", "measured", "result", "nonconformance"],
    "change_notice": ["change notice", "ecn", "eco", "change order", "effective date", "reason for change"],
    "test_certificate": ["certificate", "mill test", "test report", "heat number", "batch", "lot"],
    "specification": ["specification", "requirements", "shall", "standard", "procedure"],
}

def classify(text: str):
    lower = text.lower()
    scores = {}
    for label, words in KEYWORDS.items():
        hits = sum(1 for w in words if w in lower)
        scores[label] = hits / max(len(words), 1)
    best = max(scores, key=scores.get) if scores else "unknown"
    conf = scores.get(best, 0)
    if conf == 0:
        return "unknown", 0.25, scores
    return best, round(min(0.95, 0.35 + conf), 2), scores
