"""Generate deterministic, imbalanced card transactions with realistic fraud signals."""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

FIELDS = [
    "transaction_id", "event_time", "customer_id", "merchant_category", "country",
    "amount", "hour", "account_age_days", "transactions_24h", "distance_from_home_km",
    "card_present", "is_foreign", "is_fraud",
]


def sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-max(-30.0, min(30.0, value))))


def generate_transactions(count: int = 6000, seed: int = 42) -> list[dict[str, object]]:
    rng = random.Random(seed)
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    categories = ["grocery", "fuel", "restaurant", "electronics", "travel", "gaming"]
    rows: list[dict[str, object]] = []
    for index in range(count):
        hour = rng.randrange(24)
        category = rng.choices(categories, weights=[28, 15, 25, 8, 9, 15])[0]
        amount = round(min(rng.lognormvariate(3.4, 1.0), 5000), 2)
        foreign = int(rng.random() < 0.07)
        card_present = int(rng.random() > (0.52 if category in {"gaming", "travel"} else 0.22))
        velocity = max(1, int(rng.expovariate(1 / 3.2)))
        distance = round(rng.expovariate(1 / 18) + foreign * rng.uniform(120, 1800), 1)
        account_age = rng.randint(5, 3200)
        risk = (
            -6.4
            + 1.45 * foreign
            + 1.1 * (1 - card_present)
            + 1.25 * (hour < 5)
            + 1.2 * (amount > 600)
            + 1.0 * (velocity >= 8)
            + 0.9 * (distance > 300)
            + 0.8 * (account_age < 30)
            + 0.65 * (category in {"electronics", "gaming"})
        )
        fraud = int(rng.random() < sigmoid(risk))
        event_time = start + timedelta(minutes=index * 8 + rng.randrange(8))
        rows.append({
            "transaction_id": f"tx-{index + 1:07d}",
            "event_time": event_time.isoformat().replace("+00:00", "Z"),
            "customer_id": f"cus-{rng.randint(1, 1800):05d}",
            "merchant_category": category,
            "country": "INT" if foreign else "BR",
            "amount": amount,
            "hour": hour,
            "account_age_days": account_age,
            "transactions_24h": velocity,
            "distance_from_home_km": distance,
            "card_present": card_present,
            "is_foreign": foreign,
            "is_fraud": fraud,
        })
    return rows


def write_dataset(rows: list[dict[str, object]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    frauds = sum(int(row["is_fraud"]) for row in rows)
    manifest = {"rows": len(rows), "frauds": frauds, "fraud_rate": round(frauds / len(rows), 6), "seed": 42}
    output.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=6000)
    parser.add_argument("--output", type=Path, default=Path("data/sample/transactions.csv"))
    args = parser.parse_args()
    write_dataset(generate_transactions(args.rows), args.output)
    print(f"Dataset written to {args.output}")


if __name__ == "__main__":
    main()

