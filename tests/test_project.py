import json
import unittest
import uuid
from pathlib import Path
import shutil

from src.fraudml.generate import generate_transactions, write_dataset
from src.fraudml.model import FraudModel, train_pipeline
from src.fraudml.monitor import drift_status, population_stability_index


class FraudProjectTests(unittest.TestCase):
    def test_generation_is_deterministic_and_imbalanced(self):
        first = generate_transactions(1000, 42)
        second = generate_transactions(1000, 42)
        self.assertEqual(first, second)
        rate = sum(row["is_fraud"] for row in first) / len(first)
        self.assertGreaterEqual(rate, 0.005)
        self.assertLess(rate, 0.15)

    def test_temporal_pipeline_is_reproducible(self):
        root = Path("tests/.tmp") / str(uuid.uuid4())
        root.mkdir(parents=True)
        try:
            dataset, model_path, report = root / "data.csv", root / "model.json", root / "report.json"
            write_dataset(generate_transactions(1800), dataset)
            first = train_pipeline(dataset, model_path, report)
            second = train_pipeline(dataset, model_path, report)
            self.assertEqual(first, second)
            self.assertEqual(first["split_strategy"], "temporal_70_15_15")
            self.assertGreater(first["test"]["average_precision"], 0.05)
            self.assertGreater(first["test"]["recall"], 0.2)
            loaded = FraudModel.load(model_path)
            self.assertEqual(loaded.threshold, first["threshold"])
            self.assertIn("model_sha256", json.loads(model_path.read_text()))
        finally:
            shutil.rmtree(root)

    def test_drift_monitoring(self):
        stable = population_stability_index(list(range(100)), list(range(100)))
        shifted = population_stability_index(list(range(100)), list(range(100, 200)))
        self.assertEqual(drift_status(stable), "stable")
        self.assertEqual(drift_status(shifted), "critical")


if __name__ == "__main__":
    unittest.main()

