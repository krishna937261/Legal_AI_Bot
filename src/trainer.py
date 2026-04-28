"""
trainer.py — Training pipeline for LexAI v4

Usage:
    python trainer.py --model tfidf          # Train TF-IDF baseline
    python trainer.py --model bert           # Fine-tune InLegalBERT
    python trainer.py --model both           # Train both + compare
    python trainer.py --model tfidf --max_train 5000   # Quick run
"""

import os, sys, json, logging, argparse, time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config      import MODEL_DIR, EVAL_DIR, LOG_DIR, EVAL_RESULTS_PATH
from data_loader import load_all_splits

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(LOG_DIR, "training.log")),
    ],
)
logger = logging.getLogger("lexai.trainer")


def train_tfidf(data: dict, max_train: int = None) -> dict:
    from tfidf_model import TFIDFClassifier

    X_train = data["X_train"][:max_train] if max_train else data["X_train"]
    y_train = data["y_train"][:max_train] if max_train else data["y_train"]

    model = TFIDFClassifier()
    train_metrics = model.train(X_train, y_train)

    logger.info("Evaluating TF-IDF on dev set...")
    dev_metrics  = model.evaluate(data["X_dev"],  data["y_dev"])

    logger.info("Evaluating TF-IDF on test set...")
    test_metrics = model.evaluate(data["X_test"], data["y_test"])

    model.save()

    return {
        "model":        "TF-IDF + LinearSVC",
        "train":        train_metrics,
        "dev":          dev_metrics,
        "test":         test_metrics,
        "trained_on":   datetime.now().isoformat(),
    }


def train_bert(data: dict, max_train: int = None) -> dict:
    from bert_model  import LegalBERTClassifier
    from sklearn.preprocessing import MultiLabelBinarizer
    import numpy as np
    import joblib
    from config import LABEL_BINARIZER_PATH

    X_train = data["X_train"][:max_train] if max_train else data["X_train"]
    y_train = data["y_train"][:max_train] if max_train else data["y_train"]

    # Binarize labels
    mlb = MultiLabelBinarizer()
    y_train_bin = mlb.fit_transform(y_train)
    y_dev_bin   = mlb.transform(data["y_dev"])
    y_test_bin  = mlb.transform(data["y_test"])
    joblib.dump(mlb, LABEL_BINARIZER_PATH)

    n_labels = len(mlb.classes_)
    logger.info(f"Training BERT with {n_labels} labels on {len(X_train)} samples")

    model   = LegalBERTClassifier(num_labels=n_labels)
    history = model.train(X_train, y_train_bin, data["X_dev"], y_dev_bin)
    model.save()

    # Evaluate on test
    from sklearn.metrics import f1_score, precision_score, recall_score, hamming_loss
    y_pred_bin = model.predict_binary(data["X_test"])

    test_metrics = {
        "f1_micro":    round(f1_score(y_test_bin,    y_pred_bin, average="micro",    zero_division=0), 4),
        "f1_macro":    round(f1_score(y_test_bin,    y_pred_bin, average="macro",    zero_division=0), 4),
        "f1_weighted": round(f1_score(y_test_bin,    y_pred_bin, average="weighted", zero_division=0), 4),
        "precision":   round(precision_score(y_test_bin, y_pred_bin, average="micro", zero_division=0), 4),
        "recall":      round(recall_score(y_test_bin,    y_pred_bin, average="micro", zero_division=0), 4),
        "hamming_loss":round(hamming_loss(y_test_bin, y_pred_bin), 4),
    }

    return {
        "model":      "InLegalBERT (Fine-tuned)",
        "history":    history,
        "test":       test_metrics,
        "trained_on": datetime.now().isoformat(),
    }


def save_evaluation_report(results: dict, stats: dict):
    """Save full evaluation report as JSON."""
    report = {
        "project":      "LexAI — AI Legal Statute Identification System",
        "dataset":      "LeSICiN (Zenodo 6053791) — IIT Kharagpur / AAAI-22",
        "generated_at": datetime.now().isoformat(),
        "dataset_stats": stats,
        "results":       results,
    }
    with open(EVAL_RESULTS_PATH, "w") as f:
        json.dump(report, f, indent=2)
    logger.info(f"Evaluation report saved to {EVAL_RESULTS_PATH}")
    return report


def main():
    parser = argparse.ArgumentParser(description="LexAI Trainer")
    parser.add_argument("--model",     choices=["tfidf", "bert", "both"], default="tfidf")
    parser.add_argument("--max_train", type=int, default=None, help="Limit training samples")
    parser.add_argument("--max_dev",   type=int, default=500)
    parser.add_argument("--max_test",  type=int, default=1000)
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("LexAI v4 — Training Pipeline")
    logger.info(f"Model: {args.model} | Max train: {args.max_train}")
    logger.info("=" * 60)

    logger.info("Loading dataset...")
    data = load_all_splits(args.max_train, args.max_dev, args.max_test)
    logger.info(f"Train: {len(data['X_train'])} | Dev: {len(data['X_dev'])} | Test: {len(data['X_test'])}")

    results = {}

    if args.model in ("tfidf", "both"):
        logger.info("\n--- Training TF-IDF Baseline ---")
        results["tfidf"] = train_tfidf(data)
        logger.info(f"TF-IDF Test F1 (micro): {results['tfidf']['test']['f1_micro']}")

    if args.model in ("bert", "both"):
        logger.info("\n--- Fine-tuning InLegalBERT ---")
        results["bert"] = train_bert(data, args.max_train)
        logger.info(f"BERT Test F1 (micro): {results['bert']['test']['f1_micro']}")

    report = save_evaluation_report(results, data["train_stats"])

    # Print summary table
    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    print(f"{'Model':<30} {'F1-micro':>10} {'F1-macro':>10} {'Precision':>10} {'Recall':>10}")
    print("-" * 60)
    for key, res in results.items():
        m = res.get("test", {})
        print(f"{res['model']:<30} {m.get('f1_micro',0):>10.4f} {m.get('f1_macro',0):>10.4f} {m.get('precision',0):>10.4f} {m.get('recall',0):>10.4f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
