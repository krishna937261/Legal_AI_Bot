"""
tfidf_model.py — TF-IDF + LinearSVC Multi-Label Classifier (Fallback / Baseline)

Used when:
  1. Dataset is not downloaded yet (uses built-in legal KB)
  2. BERT model is not trained yet
  3. User explicitly requests fast inference

Also serves as the BASELINE for comparison in evaluation reports.
"""

import os, sys, logging, joblib
import numpy as np
from typing import List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    TFIDF_MODEL_PATH, LABEL_BINARIZER_PATH,
    TFIDF_MAX_FEATURES, TFIDF_NGRAM_RANGE, TOP_K_LABELS,
)

logger = logging.getLogger("lexai.tfidf_model")


class TFIDFClassifier:
    """
    Multi-label TF-IDF + LinearSVC using OneVsRestClassifier.
    Trained on LeSICiN dataset or built-in KB.
    """

    def __init__(self):
        self.vectorizer = None
        self.classifier = None
        self.binarizer  = None
        self.is_trained = False

    def train(self, X_train: List[str], y_train: List[List[str]]) -> dict:
        """Train TF-IDF + LinearSVC on training data."""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.svm import LinearSVC
        from sklearn.multiclass import OneVsRestClassifier
        from sklearn.preprocessing import MultiLabelBinarizer
        from sklearn.pipeline import Pipeline
        from sklearn.metrics import f1_score

        logger.info(f"Training TF-IDF model on {len(X_train)} samples...")

        # Binarize labels
        self.binarizer = MultiLabelBinarizer()
        y_bin = self.binarizer.fit_transform(y_train)
        logger.info(f"Label space: {len(self.binarizer.classes_)} unique labels")

        # Build pipeline
        self.vectorizer = TfidfVectorizer(
            max_features=TFIDF_MAX_FEATURES,
            ngram_range=TFIDF_NGRAM_RANGE,
            sublinear_tf=True,
            min_df=2,
            strip_accents="unicode",
            analyzer="word",
        )
        X_vec = self.vectorizer.fit_transform(X_train)

        self.classifier = OneVsRestClassifier(
            LinearSVC(C=1.0, max_iter=2000, dual=True),
            n_jobs=-1,
        )
        self.classifier.fit(X_vec, y_bin)
        self.is_trained = True

        # Training score
        y_pred = self.classifier.predict(X_vec)
        f1 = f1_score(y_bin, y_pred, average="micro", zero_division=0)
        logger.info(f"TF-IDF training F1 (micro): {f1:.4f}")
        return {"train_f1_micro": round(f1, 4), "num_labels": len(self.binarizer.classes_)}

    def predict(self, texts: List[str]) -> List[List[str]]:
        """Predict labels for a list of texts."""
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call train() first.")
        X_vec  = self.vectorizer.transform(texts)
        y_bin  = self.classifier.predict(X_vec)
        return self.binarizer.inverse_transform(y_bin)

    def predict_with_scores(self, text: str, top_k: int = TOP_K_LABELS) -> List[Tuple[str, float]]:
        """
        Returns list of (label, confidence_score) tuples.
        Uses decision function scores as proxy confidence.
        """
        if not self.is_trained:
            return []
        X_vec = self.vectorizer.transform([text])

        # Get decision scores per label
        try:
            scores = self.classifier.decision_function(X_vec)[0]
            # Normalize to 0-1 using sigmoid
            def sigmoid(x): return 1 / (1 + np.exp(-x))
            probs = sigmoid(scores)
        except Exception:
            probs = np.zeros(len(self.binarizer.classes_))

        top_idxs = np.argsort(probs)[::-1][:top_k]
        results  = []
        for idx in top_idxs:
            if idx < len(self.binarizer.classes_) and probs[idx] > 0.3:
                results.append((self.binarizer.classes_[idx], round(float(probs[idx]), 4)))
        return results

    def evaluate(self, X_test: List[str], y_test: List[List[str]]) -> dict:
        """Full evaluation on test set."""
        from sklearn.metrics import (
            f1_score, precision_score, recall_score,
            hamming_loss, classification_report,
        )
        y_true = self.binarizer.transform(y_test)
        X_vec  = self.vectorizer.transform(X_test)
        y_pred = self.classifier.predict(X_vec)

        return {
            "f1_micro":      round(f1_score(y_true, y_pred, average="micro",    zero_division=0), 4),
            "f1_macro":      round(f1_score(y_true, y_pred, average="macro",    zero_division=0), 4),
            "f1_weighted":   round(f1_score(y_true, y_pred, average="weighted", zero_division=0), 4),
            "precision":     round(precision_score(y_true, y_pred, average="micro", zero_division=0), 4),
            "recall":        round(recall_score(y_true, y_pred, average="micro",    zero_division=0), 4),
            "hamming_loss":  round(hamming_loss(y_true, y_pred), 4),
            "num_test":      len(X_test),
            "num_labels":    len(self.binarizer.classes_),
        }

    def save(self):
        joblib.dump({"vectorizer": self.vectorizer, "classifier": self.classifier}, TFIDF_MODEL_PATH)
        joblib.dump(self.binarizer, LABEL_BINARIZER_PATH)
        logger.info(f"TF-IDF model saved")

    def load(self) -> bool:
        if not (os.path.exists(TFIDF_MODEL_PATH) and os.path.exists(LABEL_BINARIZER_PATH)):
            return False
        try:
            data = joblib.load(TFIDF_MODEL_PATH)
            self.vectorizer = data["vectorizer"]
            self.classifier = data["classifier"]
            self.binarizer  = joblib.load(LABEL_BINARIZER_PATH)
            self.is_trained = True
            logger.info("TF-IDF model loaded from disk")
            return True
        except Exception as e:
            logger.error(f"Failed to load TF-IDF model: {e}")
            return False
