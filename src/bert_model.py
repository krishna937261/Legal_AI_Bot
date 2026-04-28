"""
bert_model.py — Fine-tuned BERT for Multi-Label Legal Statute Identification

Uses InLegalBERT (law-ai/InLegalBERT) — BERT pre-trained on Indian legal corpus.
Falls back to legal-bert or bert-base-uncased if not available.

Architecture:
  InLegalBERT → [CLS] pooling → Dropout → Linear(hidden, num_labels) → Sigmoid
  Loss: Binary Cross Entropy (multi-label)
"""

import os, sys, json, logging, time
import numpy as np
import joblib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    BERT_MODEL_NAME, BERT_FALLBACK, BERT_FALLBACK_2,
    BERT_MODEL_DIR, LABEL_BINARIZER_PATH,
    MAX_SEQ_LENGTH, BERT_BATCH_SIZE, BERT_EPOCHS, BERT_LR,
    BERT_WARMUP_RATIO, TOP_K_LABELS, CONFIDENCE_THRESHOLD,
)

logger = logging.getLogger("lexai.bert_model")

# ── Lazy imports (only load when needed) ─────────────────────────────────────
def _import_torch():
    import torch
    return torch

def _import_transformers():
    from transformers import (
        AutoTokenizer, AutoModel,
        get_linear_schedule_with_warmup,
    )
    return AutoTokenizer, AutoModel, get_linear_schedule_with_warmup


# ═══════════════════════════════════════════════════════════════════════════════
# BERT Multi-Label Classifier
# ═══════════════════════════════════════════════════════════════════════════════
class LegalBERTClassifier:
    """
    Fine-tuned InLegalBERT for multi-label statute identification.
    Compatible with the LeSICiN dataset format.
    """

    def __init__(self, num_labels: int, model_name: str = None):
        self.torch       = _import_torch()
        AutoTokenizer, AutoModel, _ = _import_transformers()

        self.device    = self.torch.device("cuda" if self.torch.cuda.is_available() else "cpu")
        self.num_labels = num_labels
        self.tokenizer  = None
        self.model      = None

        # Try model variants in order
        candidates = [model_name or BERT_MODEL_NAME, BERT_FALLBACK, BERT_FALLBACK_2]
        for name in candidates:
            try:
                logger.info(f"Loading tokenizer: {name}")
                self.tokenizer = AutoTokenizer.from_pretrained(name)
                self.base_model_name = name
                logger.info(f"✓ Loaded tokenizer: {name}")
                break
            except Exception as e:
                logger.warning(f"Could not load {name}: {e}")

        if self.tokenizer is None:
            raise RuntimeError("Could not load any BERT tokenizer. Check internet connection.")

        self._build_model()

    def _build_model(self):
        """Build the classification head on top of BERT."""
        import torch.nn as nn
        AutoTokenizer, AutoModel, _ = _import_transformers()

        class _BERTClassifier(nn.Module):
            def __init__(self, base_model, num_labels, hidden_size):
                super().__init__()
                self.bert    = base_model
                self.dropout = nn.Dropout(0.3)
                self.classifier = nn.Linear(hidden_size, num_labels)

            def forward(self, input_ids, attention_mask, token_type_ids=None):
                outputs = self.bert(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    token_type_ids=token_type_ids,
                )
                # Use [CLS] token representation
                pooled = outputs.last_hidden_state[:, 0, :]
                pooled = self.dropout(pooled)
                logits = self.classifier(pooled)
                return logits

        base = AutoModel.from_pretrained(self.base_model_name)
        hidden_size = base.config.hidden_size
        self.model  = _BERTClassifier(base, self.num_labels, hidden_size).to(self.device)
        logger.info(f"Model built on {self.device} | labels={self.num_labels} | hidden={hidden_size}")

    def _tokenize_batch(self, texts):
        """Tokenize a batch of texts."""
        return self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=MAX_SEQ_LENGTH,
            return_tensors="pt",
        )

    def train(self, X_train, y_train_bin, X_dev=None, y_dev_bin=None):
        """
        Fine-tune BERT on training data.
        y_train_bin: binary matrix (n_samples, n_labels) from MultiLabelBinarizer
        """
        import torch
        import torch.nn as nn
        from torch.utils.data import DataLoader, TensorDataset
        from transformers import get_linear_schedule_with_warmup
        from torch.optim import AdamW

        logger.info(f"Starting BERT fine-tuning on {len(X_train)} samples...")
        train_start = time.time()

        # Tokenize in batches
        logger.info("Tokenizing training data...")
        all_input_ids, all_masks = [], []
        for i in range(0, len(X_train), 64):
            batch = X_train[i:i+64]
            enc = self.tokenizer(
                batch, padding="max_length", truncation=True,
                max_length=MAX_SEQ_LENGTH, return_tensors="pt",
            )
            all_input_ids.append(enc["input_ids"])
            all_masks.append(enc["attention_mask"])

        input_ids  = torch.cat(all_input_ids)
        attn_masks = torch.cat(all_masks)
        labels_t   = torch.tensor(y_train_bin, dtype=torch.float)

        dataset    = TensorDataset(input_ids, attn_masks, labels_t)
        loader     = DataLoader(dataset, batch_size=BERT_BATCH_SIZE, shuffle=True)

        optimizer  = AdamW(self.model.parameters(), lr=BERT_LR, weight_decay=0.01)
        total_steps= len(loader) * BERT_EPOCHS
        scheduler  = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=int(total_steps * BERT_WARMUP_RATIO),
            num_training_steps=total_steps,
        )
        criterion  = nn.BCEWithLogitsLoss()

        history = {"train_loss": [], "dev_f1": []}

        for epoch in range(BERT_EPOCHS):
            self.model.train()
            epoch_loss = 0.0
            for step, batch in enumerate(loader):
                b_input_ids, b_masks, b_labels = [x.to(self.device) for x in batch]
                optimizer.zero_grad()
                logits = self.model(b_input_ids, b_masks)
                loss   = criterion(logits, b_labels)
                loss.backward()
                nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
                epoch_loss += loss.item()

                if step % 50 == 0:
                    logger.info(f"  Epoch {epoch+1}/{BERT_EPOCHS} | Step {step}/{len(loader)} | Loss {loss.item():.4f}")

            avg_loss = epoch_loss / len(loader)
            history["train_loss"].append(avg_loss)
            logger.info(f"Epoch {epoch+1} complete | Avg Loss: {avg_loss:.4f}")

            # Validation
            if X_dev is not None and y_dev_bin is not None:
                f1 = self._evaluate_f1(X_dev, y_dev_bin)
                history["dev_f1"].append(f1)
                logger.info(f"  Dev F1 (micro): {f1:.4f}")

        elapsed = round(time.time() - train_start, 1)
        logger.info(f"Training complete in {elapsed}s")
        return history

    def _evaluate_f1(self, X, y_true_bin):
        """Quick F1 evaluation on a dataset."""
        from sklearn.metrics import f1_score
        y_pred = self.predict_binary(X)
        return f1_score(y_true_bin, y_pred, average="micro", zero_division=0)

    def predict_proba(self, texts) -> np.ndarray:
        """
        Returns sigmoid probability matrix (n_samples, n_labels).
        """
        import torch
        self.model.eval()
        all_probs = []

        with torch.no_grad():
            for i in range(0, len(texts), BERT_BATCH_SIZE):
                batch = texts[i:i+BERT_BATCH_SIZE]
                enc   = self.tokenizer(
                    batch, padding=True, truncation=True,
                    max_length=MAX_SEQ_LENGTH, return_tensors="pt",
                ).to(self.device)
                logits = self.model(enc["input_ids"], enc["attention_mask"])
                probs  = torch.sigmoid(logits).cpu().numpy()
                all_probs.append(probs)

        return np.vstack(all_probs)

    def predict_binary(self, texts, threshold=None) -> np.ndarray:
        """Returns binary prediction matrix."""
        thresh  = threshold or CONFIDENCE_THRESHOLD
        probs   = self.predict_proba(texts)
        return (probs >= thresh).astype(int)

    def predict_top_k(self, text: str, k: int = TOP_K_LABELS):
        """
        Returns top-k predicted labels with confidence scores for a single text.
        """
        probs    = self.predict_proba([text])[0]
        top_idxs = np.argsort(probs)[::-1][:k]
        return [(int(idx), float(probs[idx])) for idx in top_idxs if probs[idx] >= CONFIDENCE_THRESHOLD]

    def save(self, path: str = BERT_MODEL_DIR):
        """Save model + tokenizer."""
        import torch
        os.makedirs(path, exist_ok=True)
        self.tokenizer.save_pretrained(path)
        torch.save({
            "model_state_dict": self.model.state_dict(),
            "num_labels":       self.num_labels,
            "base_model":       self.base_model_name,
        }, os.path.join(path, "classifier.pt"))
        logger.info(f"BERT model saved to {path}")

    @classmethod
    def load(cls, path: str = BERT_MODEL_DIR, num_labels: int = None):
        """Load saved model."""
        import torch
        from transformers import AutoTokenizer
        ckpt = torch.load(os.path.join(path, "classifier.pt"), map_location="cpu")
        n_labels = num_labels or ckpt["num_labels"]
        instance = cls.__new__(cls)
        instance.torch       = torch
        instance.device      = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        instance.num_labels  = n_labels
        instance.base_model_name = ckpt["base_model"]
        instance.tokenizer   = AutoTokenizer.from_pretrained(path)
        instance._build_model()
        instance.model.load_state_dict(ckpt["model_state_dict"])
        instance.model.to(instance.device)
        instance.model.eval()
        logger.info(f"BERT model loaded from {path}")
        return instance

    def is_saved(self) -> bool:
        return os.path.exists(os.path.join(BERT_MODEL_DIR, "classifier.pt"))
