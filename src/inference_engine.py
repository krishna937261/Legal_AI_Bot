"""
inference_engine.py — Smart inference engine

Priority:
  1. BERT (if trained) — highest accuracy
  2. TF-IDF (if trained) — fast fallback
  3. Rule-based KB (always available) — baseline

Merges results from available models + rule-based matching.
Maps predicted label IDs back to human-readable section info.
"""

import os, sys, logging, json
import numpy as np
from typing import List, Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config        import BERT_MODEL_DIR, TFIDF_MODEL_PATH, LABEL_BINARIZER_PATH, TOP_K_LABELS, CONFIDENCE_THRESHOLD
from legal_kb      import IPC_SECTIONS, VICTIM_PHRASES, FAULT_PHRASES

logger = logging.getLogger("lexai.inference")


# ── Section lookup: map label ID (e.g. "IPC_302") → rich info dict ────────────
_SECTION_MAP: Dict[str, Dict] = {}
for s in IPC_SECTIONS:
    # e.g. "Section 302 IPC" → try multiple key formats
    _SECTION_MAP[s["section"].lower().replace(" ", "_")] = s
    _SECTION_MAP[s["section"]] = s
    # Also map by title keywords
    for kw in s.get("keywords", []):
        _SECTION_MAP[kw] = s


def _label_to_section(label: str) -> Optional[Dict]:
    """
    Maps a label string (from dataset vocab) to section info.
    Dataset labels look like: "IPC_302", "IPC_420", "IT_66" etc.
    """
    # Try direct lookup
    if label in _SECTION_MAP:
        return _SECTION_MAP[label]

    # Parse IPC / IT Act labels
    label_clean = label.replace("_", " ").upper()
    for s in IPC_SECTIONS:
        if any(part in s["section"].upper() for part in label_clean.split() if len(part) > 2):
            return s
        if any(part in s["title"].upper() for part in label_clean.split() if len(part) > 3):
            return s

    # Return a placeholder with the raw label
    return {
        "section":     label.replace("_", " "),
        "title":       label.replace("_", " "),
        "description": "Refer to official legal texts for this section.",
        "punishment":  "Refer to official legal texts.",
        "bailable":    None,
        "cognizable":  None,
        "category":    "Legal Statute",
        "court":       "Competent Court",
        "compoundable": None,
    }


# ═══════════════════════════════════════════════════════════════════════════════
class InferenceEngine:
    """
    Unified inference engine — loads available models and runs predictions.
    """

    def __init__(self):
        self.bert_model   = None
        self.tfidf_model  = None
        self.label_binarizer = None
        self._load_models()

    def _load_models(self):
        # Try BERT
        bert_ckpt = os.path.join(BERT_MODEL_DIR, "classifier.pt")
        if os.path.exists(bert_ckpt) and os.path.exists(LABEL_BINARIZER_PATH):
            try:
                import joblib
                from bert_model import LegalBERTClassifier
                self.label_binarizer = joblib.load(LABEL_BINARIZER_PATH)
                self.bert_model = LegalBERTClassifier.load(
                    BERT_MODEL_DIR,
                    num_labels=len(self.label_binarizer.classes_),
                )
                logger.info("✓ BERT model loaded")
            except Exception as e:
                logger.warning(f"BERT load failed: {e}")

        # Try TF-IDF
        if os.path.exists(TFIDF_MODEL_PATH):
            try:
                from tfidf_model import TFIDFClassifier
                self.tfidf_model = TFIDFClassifier()
                if self.tfidf_model.load():
                    logger.info("✓ TF-IDF model loaded")
                else:
                    self.tfidf_model = None
            except Exception as e:
                logger.warning(f"TF-IDF load failed: {e}")

        if not self.bert_model and not self.tfidf_model:
            logger.info("No trained models found — using rule-based engine only.")

    @property
    def mode(self) -> str:
        if self.bert_model:   return "BERT"
        if self.tfidf_model:  return "TF-IDF"
        return "RULE-BASED"

    def predict_sections(self, text: str) -> List[Dict]:
        """
        Run prediction and return list of enriched section dicts with confidence.
        Combines ML predictions with rule-based matching.
        """
        ml_results   = self._ml_predict(text)
        rule_results = self._rule_predict(text)

        # Merge: ML results take priority, rule-based fills gaps
        seen = set()
        combined = []
        for res in ml_results:
            key = res["section"]
            if key not in seen:
                seen.add(key)
                combined.append(res)
        for res in rule_results:
            key = res["section"]
            if key not in seen:
                seen.add(key)
                res["source"] = "rule-based"
                combined.append(res)

        return combined[:TOP_K_LABELS + 3]

    def _ml_predict(self, text: str) -> List[Dict]:
        results = []
        try:
            if self.bert_model and self.label_binarizer:
                top_k = self.bert_model.predict_top_k(text)
                for idx, conf in top_k:
                    if idx < len(self.label_binarizer.classes_):
                        label   = self.label_binarizer.classes_[idx]
                        sec_info = _label_to_section(label)
                        results.append({
                            **sec_info,
                            "confidence": round(conf * 100, 1),
                            "source":     "InLegalBERT",
                        })
            elif self.tfidf_model:
                preds = self.tfidf_model.predict_with_scores(text)
                for label, conf in preds:
                    sec_info = _label_to_section(label)
                    results.append({
                        **sec_info,
                        "confidence": round(conf * 100, 1),
                        "source":     "TF-IDF",
                    })
        except Exception as e:
            logger.error(f"ML prediction error: {e}")
        return results

    def _rule_predict(self, text: str) -> List[Dict]:
        text_lower = text.lower()
        matched, seen = [], set()
        for entry in IPC_SECTIONS:
            for kw in entry.get("keywords", []):
                if kw in text_lower and entry["section"] not in seen:
                    seen.add(entry["section"])
                    info = {k: v for k, v in entry.items() if k != "keywords"}
                    info["confidence"] = 70.0
                    info["source"]     = "rule-based"
                    matched.append(info)
                    break
        return matched

    def get_model_info(self) -> Dict:
        return {
            "active_model":  self.mode,
            "bert_loaded":   self.bert_model is not None,
            "tfidf_loaded":  self.tfidf_model is not None,
            "num_labels":    len(self.label_binarizer.classes_) if self.label_binarizer else "N/A",
        }


# Singleton
_engine: Optional[InferenceEngine] = None

def get_engine() -> InferenceEngine:
    global _engine
    if _engine is None:
        _engine = InferenceEngine()
    return _engine
