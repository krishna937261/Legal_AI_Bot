"""
config.py — Centralized configuration for LexAI v4
"""
import os

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR      = os.path.join(BASE_DIR, "src")
DATA_DIR     = os.path.join(BASE_DIR, "datasets")
MODEL_DIR    = os.path.join(BASE_DIR, "models")
LOG_DIR      = os.path.join(BASE_DIR, "logs")
EVAL_DIR     = os.path.join(BASE_DIR, "evaluation")

# ── Dataset files (place downloaded files here) ───────────────────────────────
TRAIN_FILE       = os.path.join(DATA_DIR, "train.jsonl")
DEV_FILE         = os.path.join(DATA_DIR, "dev.jsonl")
TEST_FILE        = os.path.join(DATA_DIR, "test.jsonl")
SECS_FILE        = os.path.join(DATA_DIR, "secs.jsonl")
LABEL_VOCAB_FILE = os.path.join(DATA_DIR, "label_vocab.json")

# ── Model paths ───────────────────────────────────────────────────────────────
BERT_MODEL_DIR        = os.path.join(MODEL_DIR, "bert_legal")
TFIDF_MODEL_PATH      = os.path.join(MODEL_DIR, "tfidf_classifier.pkl")
LABEL_ENCODER_PATH    = os.path.join(MODEL_DIR, "label_encoder.pkl")
LABEL_BINARIZER_PATH  = os.path.join(MODEL_DIR, "label_binarizer.pkl")
EVAL_RESULTS_PATH     = os.path.join(EVAL_DIR,  "evaluation_results.json")

# ── BERT Configuration ────────────────────────────────────────────────────────
BERT_MODEL_NAME    = "law-ai/InLegalBERT"   # Indian Legal BERT (primary)
BERT_FALLBACK      = "nlpaueb/legal-bert-base-uncased"  # fallback
BERT_FALLBACK_2    = "bert-base-uncased"     # final fallback

MAX_SEQ_LENGTH     = 512
BERT_BATCH_SIZE    = 8
BERT_EPOCHS        = 5
BERT_LR            = 2e-5
BERT_WARMUP_RATIO  = 0.1
TOP_K_LABELS       = 5       # Max sections to predict per case
CONFIDENCE_THRESHOLD = 0.3   # Min probability to include a label

# ── TF-IDF Fallback Configuration ────────────────────────────────────────────
TFIDF_MAX_FEATURES = 50000
TFIDF_NGRAM_RANGE  = (1, 3)
TOP_N_TFIDF        = 20000   # top features for training

# ── App Settings ──────────────────────────────────────────────────────────────
APP_TITLE   = "LexAI — AI Legal Statute Identification System"
APP_VERSION = "4.0.0"
APP_DESC    = "Real-world ML-powered Indian legal assistant using LeSICiN dataset (IIT Kharagpur / AAAI-22)"

for d in [DATA_DIR, MODEL_DIR, LOG_DIR, EVAL_DIR]:
    os.makedirs(d, exist_ok=True)
