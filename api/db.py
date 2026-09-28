"""JSON-file-backed transaction store; requires no third-party database driver."""

import json
from pathlib import Path
from threading import RLock


class TransactionStore:
    def __init__(self, path):
        self.path = Path(path)
        self._lock = RLock()

    def _read(self):
        if not self.path.exists():
            return []
        try:
            with self.path.open("r", encoding="utf-8") as source:
                transactions = json.load(source)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Transaction data file contains invalid JSON") from exc
        if not isinstance(transactions, list):
            raise RuntimeError("Transaction data file must contain a JSON array")
        return transactions

    def _write(self, transactions):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        with temporary.open("w", encoding="utf-8") as destination:
            json.dump(transactions, destination, ensure_ascii=False, indent=2)
            destination.write("\n")
        temporary.replace(self.path)

    def list_all(self):
        with self._lock:
            return self._read()

    def get(self, transaction_id):
        with self._lock:
            return next((item for item in self._read() if item["transaction_id"] == transaction_id), None)

    def create(self, transaction):
        with self._lock:
            transactions = self._read()
            transactions.append(transaction)
            self._write(transactions)

    def update(self, transaction_id, transaction):
        with self._lock:
            transactions = self._read()
            for index, current in enumerate(transactions):
                if current["transaction_id"] == transaction_id:
                    transactions[index] = transaction
                    self._write(transactions)
                    return
            raise KeyError(transaction_id)

    def delete(self, transaction_id):
        with self._lock:
            transactions = self._read()
            remaining = [item for item in transactions if item["transaction_id"] != transaction_id]
            if len(remaining) == len(transactions):
                return False
            self._write(remaining)
            return True
