"""Minimal JSON scoring API using only Python's standard library."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .model import FEATURES, FraudModel

MODEL_PATH = Path("models/fraud_model.json")


class ScoringHandler(BaseHTTPRequestHandler):
    model: FraudModel

    def send_json(self, status: int, payload: dict[str, object]) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self.send_json(200, {"status": "ok", "model_loaded": True})
        else:
            self.send_json(404, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/score":
            self.send_json(404, {"error": "not_found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length))
            score = self.model.predict_score({key: str(value) for key, value in payload.items()})
            self.send_json(200, {"fraud_score": round(score, 6), "decision": "review" if score >= self.model.threshold else "approve", "threshold": self.model.threshold})
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            self.send_json(400, {"error": "invalid_payload", "detail": str(exc), "expected_features": FEATURES})

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    ScoringHandler.model = FraudModel.load(MODEL_PATH)
    print("Scoring API listening on http://127.0.0.1:8080")
    ThreadingHTTPServer(("127.0.0.1", 8080), ScoringHandler).serve_forever()


if __name__ == "__main__":
    main()

