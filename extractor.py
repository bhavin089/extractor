import re
from backend_schema import AttributeValue

PATTERNS = {
    "part_number": [r"\b(?:part\s*(?:no|number|#)|pn|p/n)\s*[:\-]?\s*([A-Z0-9][A-Z0-9_\-\.\/]{2,})"],
    "revision": [r"\b(?:revision|rev)\s*[:\-]?\s*([A-Z0-9]{1,4})\b"],
    "material": [r"\b(?:material|matl|grade)\s*[:\-]?\s*([A-Za-z0-9\-\/ ]{3,60})"],
    "surface_finish": [r"\b(?:surface finish|finish|roughness|ra)\s*[:\-]?\s*([0-9\.]+\s*(?:um|µm|microinch|uin|RA)?)"],
    "inspection_or_certificate_id": [r"\b(?:certificate|cert|inspection report|report|id)\s*(?:no|number|#)?\s*[:\-]?\s*([A-Z0-9\-\/]{3,})"],
    "effective_date": [r"\b(?:effective date|date)\s*[:\-]?\s*([0-3]?\d[\-/][01]?\d[\-/][12]\d{3}|[12]\d{3}[\-/][01]?\d[\-/][0-3]?\d)"],
}
DIMENSION_PATTERN = r"\b(\d+(?:\.\d+)?)\s*(mm|cm|m|in|inch|\")\b"
TOL_PATTERN = r"(?:±|\+/-|\+\s*/\s*-)\s*(\d+(?:\.\d+)?)\s*(mm|in|inch|\")?"
STD_PATTERN = r"\b(?:ASTM|ASME|ISO|DIN|EN|IEC|ANSI|AWS|NACE|FDA|USP)\s*[A-Z0-9\-\.\/]*\b"

def first_match(text, patterns):
    for pat in patterns:
        m = re.search(pat, text, flags=re.I)
        if m:
            return m.group(1).strip(), m.group(0).strip()
    return None, ""

def extract_attributes(text: str):
    attrs = {}
    for name, pats in PATTERNS.items():
        value, evidence = first_match(text, pats)
        conf = 0.82 if value else 0.0
        attrs[name] = AttributeValue(value=value, confidence=conf, evidence=evidence, needs_review=conf < 0.70)

    dims = [f"{a} {b}" for a,b in re.findall(DIMENSION_PATTERN, text, flags=re.I)]
    attrs["dimensions"] = AttributeValue(value=dims[:25], confidence=0.78 if dims else 0.0, evidence="; ".join(dims[:5]), needs_review=not bool(dims))

    tols = [f"±{a} {b or ''}".strip() for a,b in re.findall(TOL_PATTERN, text, flags=re.I)]
    attrs["tolerances"] = AttributeValue(value=tols[:25], confidence=0.80 if tols else 0.0, evidence="; ".join(tols[:5]), needs_review=not bool(tols))

    standards = sorted(set(re.findall(STD_PATTERN, text, flags=re.I)))
    attrs["standards"] = AttributeValue(value=standards, confidence=0.84 if standards else 0.0, evidence="; ".join(standards[:8]), needs_review=False if standards else True)

    compliance = [s for s in standards if s.upper().startswith(("FDA", "USP", "ISO"))]
    attrs["compliance"] = AttributeValue(value=compliance, confidence=0.75 if compliance else 0.0, evidence="; ".join(compliance), needs_review=False if compliance else True)
    return attrs
