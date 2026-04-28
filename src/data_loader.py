"""
data_loader.py — Dataset loader for LeSICiN (Zenodo 6053791)

Dataset format (each line in .jsonl):
  {"id": "...", "sentences": ["sent1", "sent2", ...], "labels": ["IPC_302", "IPC_420", ...]}

secs.jsonl format:
  {"id": "IPC_302", "sentences": ["Section 302: Whoever commits murder..."]}
"""

import os, sys, json, logging
import jsonlines
import numpy as np
from typing import List, Dict, Tuple, Optional
from tqdm import tqdm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import TRAIN_FILE, DEV_FILE, TEST_FILE, SECS_FILE, LABEL_VOCAB_FILE

logger = logging.getLogger("lexai.data_loader")


# ── Load raw JSONL ────────────────────────────────────────────────────────────
def load_jsonl(filepath: str, max_samples: Optional[int] = None) -> List[Dict]:
    """Load a .jsonl file and return list of dicts."""
    records = []
    if not os.path.exists(filepath):
        logger.warning(f"File not found: {filepath}")
        return records
    with jsonlines.open(filepath) as reader:
        for i, obj in enumerate(tqdm(reader, desc=f"Loading {os.path.basename(filepath)}")):
            records.append(obj)
            if max_samples and i + 1 >= max_samples:
                break
    logger.info(f"Loaded {len(records)} records from {filepath}")
    return records


# ── Flatten sentences → single document ──────────────────────────────────────
def flatten_document(record: Dict) -> str:
    """Join all sentences of a case into a single string."""
    sentences = record.get("sentences", [])
    return " ".join(sentences[:50])  # cap at 50 sentences to control length


# ── Load label vocabulary ─────────────────────────────────────────────────────
def load_label_vocab() -> Dict[str, int]:
    """Load label_vocab.json → {label_str: index}"""
    if not os.path.exists(LABEL_VOCAB_FILE):
        logger.warning("label_vocab.json not found. Using empty vocab.")
        return {}
    with open(LABEL_VOCAB_FILE, "r", encoding="utf-8") as f:
        vocab = json.load(f)
    logger.info(f"Loaded {len(vocab)} labels from label_vocab.json")
    return vocab


# ── Load statute texts ────────────────────────────────────────────────────────
def load_statute_texts() -> Dict[str, str]:
    """Load secs.jsonl → {section_id: full_text}"""
    if not os.path.exists(SECS_FILE):
        logger.warning("secs.jsonl not found.")
        return {}
    statutes = {}
    with jsonlines.open(SECS_FILE) as reader:
        for obj in reader:
            sec_id   = obj.get("id", "")
            sec_text = " ".join(obj.get("sentences", []))
            statutes[sec_id] = sec_text
    logger.info(f"Loaded {len(statutes)} statute texts")
    return statutes


# ── Prepare (X, y) for training ───────────────────────────────────────────────
def prepare_dataset(
    records: List[Dict],
    label_vocab: Dict[str, int],
    max_samples: Optional[int] = None,
) -> Tuple[List[str], List[List[str]]]:
    """
    Returns:
        texts  : list of document strings
        labels : list of label lists (multi-label)
    """
    texts, labels = [], []
    records = records[:max_samples] if max_samples else records

    for rec in records:
        text = flatten_document(rec)
        lbls = rec.get("labels", [])
        if text.strip() and lbls:
            # Filter labels to those in vocab
            valid = [l for l in lbls if l in label_vocab] if label_vocab else lbls
            if valid:
                texts.append(text)
                labels.append(valid)

    logger.info(f"Prepared {len(texts)} samples with valid labels")
    return texts, labels


# ── Dataset statistics ────────────────────────────────────────────────────────
def dataset_stats(records: List[Dict], label_vocab: Dict) -> Dict:
    """Compute dataset statistics for reporting."""
    all_labels = []
    doc_lengths = []
    for rec in records:
        all_labels.extend(rec.get("labels", []))
        doc_lengths.append(len(rec.get("sentences", [])))

    label_counts = {}
    for l in all_labels:
        label_counts[l] = label_counts.get(l, 0) + 1

    top_labels = sorted(label_counts.items(), key=lambda x: -x[1])[:20]

    return {
        "total_cases":        len(records),
        "total_labels":       len(label_vocab),
        "avg_labels_per_case": round(len(all_labels) / max(len(records), 1), 2),
        "avg_sentences":      round(np.mean(doc_lengths), 1) if doc_lengths else 0,
        "max_sentences":      max(doc_lengths) if doc_lengths else 0,
        "top_20_labels":      [{"label": l, "count": c} for l, c in top_labels],
    }


# ── Full pipeline loader ──────────────────────────────────────────────────────
def load_all_splits(max_train: int = None, max_dev: int = None, max_test: int = None):
    """Load train/dev/test splits + vocab + statutes."""
    label_vocab = load_label_vocab()
    statutes    = load_statute_texts()

    train_records = load_jsonl(TRAIN_FILE, max_train)
    dev_records   = load_jsonl(DEV_FILE,   max_dev)
    test_records  = load_jsonl(TEST_FILE,  max_test)

    X_train, y_train = prepare_dataset(train_records, label_vocab)
    X_dev,   y_dev   = prepare_dataset(dev_records,   label_vocab)
    X_test,  y_test  = prepare_dataset(test_records,  label_vocab)

    return {
        "X_train": X_train, "y_train": y_train,
        "X_dev":   X_dev,   "y_dev":   y_dev,
        "X_test":  X_test,  "y_test":  y_test,
        "label_vocab": label_vocab,
        "statutes":    statutes,
        "train_stats": dataset_stats(train_records, label_vocab),
    }
