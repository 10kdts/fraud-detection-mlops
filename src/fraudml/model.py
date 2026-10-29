"""Dependency-free logistic model with temporal validation and cost-based thresholding."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path

FEATURES = ["log_amount", "night", "young_account", "velocity", "far_from_home", "card_not_present", "is_foreign", "risky_category"]


def sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-max(-30.0, min(30.0, value))))


def vector(row: dict[str, str]) -> list[float]:
    return [
        math.log1p(float(row["amount"])),
        float(int(row["hour"]) < 5),
        float(int(row["account_age_days"]) < 30),
        min(int(row["transactions_24h"]), 15) / 15,
        float(float(row["distance_from_home_km"]) > 300),
        1.0 - float(row["card_present"]),
        float(row["is_foreign"]),
        float(row["merchant_category"] in {"electronics", "gaming"}),
    ]


@dataclass
class Standardizer:
    means: list[float]
    scales: list[float]

    @classmethod
    def fit(cls, rows: list[list[float]]) -> "Standardizer":
        means = [sum(column) / len(column) for column in zip(*rows)]
        scales = []
        for index, mean in enumerate(means):
            variance = sum((row[index] - mean) ** 2 for row in rows) / len(rows)
            scales.append(math.sqrt(variance) or 1.0)
        return cls(means, scales)

    def transform(self, row: list[float]) -> list[float]:
        return [(value - mean) / scale for value, mean, scale in zip(row, self.means, self.scales)]


@dataclass
class FraudModel:
    weights: list[float]
    bias: float
    standardizer: Standardizer
    threshold: float = 0.5

    def predict_score(self, row: dict[str, str]) -> float:
        features = self.standardizer.transform(vector(row))
        return sigmoid(self.bias + sum(w * x for w, x in zip(self.weights, features)))

    def save(self, path: Path, metrics: dict[str, object]) -> None:
        payload = {
            "model_type": "logistic_regression", "features": FEATURES, "weights": self.weights,
            "bias": self.bias, "means": self.standardizer.means, "scales": self.standardizer.scales,
            "threshold": self.threshold, "metrics": metrics,
        }
        canonical = json.dumps(payload, sort_keys=True)
        payload["model_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "FraudModel":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(data["weights"], data["bias"], Standardizer(data["means"], data["scales"]), data["threshold"])


def fit(rows: list[dict[str, str]], epochs: int = 450, learning_rate: float = 0.035) -> FraudModel:
    raw = [vector(row) for row in rows]
    scaler = Standardizer.fit(raw)
    x = [scaler.transform(item) for item in raw]
    y = [int(row["is_fraud"]) for row in rows]
    positive_weight = (len(y) - sum(y)) / max(sum(y), 1)
    weights = [0.0] * len(FEATURES)
    bias = 0.0
    for _ in range(epochs):
        gradient = [0.0] * len(weights)
        bias_gradient = 0.0
        for features, label in zip(x, y):
            prediction = sigmoid(bias + sum(w * value for w, value in zip(weights, features)))
            sample_weight = positive_weight if label else 1.0
            error = (prediction - label) * sample_weight
            bias_gradient += error
            for index, value in enumerate(features):
                gradient[index] += error * value
        normalizer = sum(positive_weight if label else 1.0 for label in y)
        bias -= learning_rate * bias_gradient / normalizer
        weights = [w - learning_rate * g / normalizer for w, g in zip(weights, gradient)]
    return FraudModel(weights, bias, scaler)


def confusion(labels: list[int], scores: list[float], threshold: float) -> dict[str, int]:
    result = {"tp": 0, "fp": 0, "tn": 0, "fn": 0}
    for label, score in zip(labels, scores):
        prediction = int(score >= threshold)
        result[{(1, 1): "tp", (0, 1): "fp", (0, 0): "tn", (1, 0): "fn"}[(label, prediction)]] += 1
    return result


def average_precision(labels: list[int], scores: list[float]) -> float:
    ranked = sorted(zip(scores, labels), reverse=True)
    positives = sum(labels)
    hits = 0
    total = 0.0
    for rank, (_, label) in enumerate(ranked, 1):
        if label:
            hits += 1
            total += hits / rank
    return total / positives if positives else 0.0


def select_threshold(labels: list[int], scores: list[float], false_negative_cost: int = 20, false_positive_cost: int = 1) -> tuple[float, int]:
    candidates = [index / 100 for index in range(5, 96)]
    costs = []
    for threshold in candidates:
        matrix = confusion(labels, scores, threshold)
        costs.append((matrix["fn"] * false_negative_cost + matrix["fp"] * false_positive_cost, threshold))
    cost, threshold = min(costs)
    return threshold, cost


def evaluate(model: FraudModel, rows: list[dict[str, str]]) -> dict[str, object]:
    labels = [int(row["is_fraud"]) for row in rows]
    scores = [model.predict_score(row) for row in rows]
    matrix = confusion(labels, scores, model.threshold)
    precision = matrix["tp"] / max(matrix["tp"] + matrix["fp"], 1)
    recall = matrix["tp"] / max(matrix["tp"] + matrix["fn"], 1)
    return {**matrix, "precision": round(precision, 4), "recall": round(recall, 4), "average_precision": round(average_precision(labels, scores), 4)}


def train_pipeline(dataset: Path, model_path: Path, report_path: Path) -> dict[str, object]:
    with dataset.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    cut = int(len(rows) * 0.7)
    validation_cut = int(len(rows) * 0.85)
    training, validation, testing = rows[:cut], rows[cut:validation_cut], rows[validation_cut:]
    model = fit(training)
    validation_labels = [int(row["is_fraud"]) for row in validation]
    validation_scores = [model.predict_score(row) for row in validation]
    model.threshold, validation_cost = select_threshold(validation_labels, validation_scores)
    metrics = {
        "split_strategy": "temporal_70_15_15", "train_rows": len(training),
        "validation_rows": len(validation), "test_rows": len(testing),
        "threshold": model.threshold, "validation_cost": validation_cost,
        "test": evaluate(model, testing),
    }
    model.save(model_path, metrics)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


if __name__ == "__main__":
    result = train_pipeline(Path("data/sample/transactions.csv"), Path("models/fraud_model.json"), Path("reports/metrics.json"))
    print(json.dumps(result, indent=2))

