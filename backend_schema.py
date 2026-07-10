from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

@dataclass
class AttributeValue:
    value: Any
    confidence: float
    evidence: str = ""
    needs_review: bool = False

@dataclass
class ExtractionResult:
    source_file: str
    document_type: str
    classification_confidence: float
    attributes: Dict[str, AttributeValue]
    confidence_overall: float
    needs_review: bool

    def to_dict(self):
        return asdict(self)
