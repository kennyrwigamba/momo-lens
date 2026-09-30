"""In-memory transaction store backed by a list and an id index"""

from datetime import datetime
from pathlib import Path

from dsa.parse_xml import parse_sms_xml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_XML = PROJECT_ROOT / "modified_sms_v2.xml"

UPDATABLE_FIELDS = (
    "transaction_type",
    "amount",
    "currency",
    "fee",
    "balance_after",
    "sender",
    "receiver",
    "timestamp",
    "raw_sms_body",
)
FLOAT_FIELDS = {"amount", "fee", "balance_after"}


class TransactionStore:
    def __init__(self):
        self.transaction_list = []
        self.transaction_dict = {}

    def _save(self, record):
        self.transaction_list.append(record)
        self.transaction_dict[record["id"]] = record

    def load_from_xml(self, xml_path):
        self.transaction_list.clear()
        self.transaction_dict.clear()
        for record in parse_sms_xml(xml_path):
            self._save(record)
        return len(self.transaction_list)

    def load_records(self, records):
        self.transaction_list.clear()
        self.transaction_dict.clear()
        for record in records:
            self._save(record)
        return len(self.transaction_list)

    def get_all(self, limit=None, offset=0):
        if limit is not None:
            return self.transaction_list[offset : offset + limit]
        return list(self.transaction_list)

    def get_by_id(self, transaction_id):
        return self.transaction_dict.get(str(transaction_id))

    def add(self, transaction_data):
        transaction_id = str(transaction_data.get("id") or f"tx_{len(self.transaction_dict) + 1}")
        if transaction_id in self.transaction_dict:
            raise ValueError(f"Transaction with ID '{transaction_id}' already exists.")

        record = {
            "id": transaction_id,
            "transaction_type": transaction_data.get("transaction_type", "Other"),
            "amount": float(transaction_data.get("amount", 0.0)),
            "currency": transaction_data.get("currency", "RWF"),
            "fee": float(transaction_data.get("fee", 0.0)),
            "balance_after": transaction_data.get("balance_after"),
            "sender": transaction_data.get("sender", "Self"),
            "receiver": transaction_data.get("receiver", "Unknown"),
            "timestamp": transaction_data.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "raw_sms_body": transaction_data.get("raw_sms_body", f"Manual transaction: {transaction_id}"),
        }
        self._save(record)
        return record

    def update(self, transaction_id, update_data):
        record = self.transaction_dict.get(str(transaction_id))
        if record is None:
            return None

        for field in UPDATABLE_FIELDS:
            if field not in update_data:
                continue
            value = update_data[field]
            if field in FLOAT_FIELDS and value is not None:
                record[field] = float(value)
            else:
                record[field] = value
        return record

    def delete(self, transaction_id):
        record = self.transaction_dict.pop(str(transaction_id), None)
        if record is None:
            return False
        self.transaction_list.remove(record)
        return True

    def count(self):
        return len(self.transaction_dict)


_default_store = None


def get_default_store(xml_path=None):
    global _default_store
    if _default_store is None:
        _default_store = TransactionStore()
        _default_store.load_from_xml(xml_path or DEFAULT_XML)
    return _default_store


if __name__ == "__main__":
    store = TransactionStore()
    print(f"Loading {DEFAULT_XML}...")
    print(f"Loaded {store.load_from_xml(DEFAULT_XML)} transactions.")

    first_id = store.get_all(limit=1)[0]["id"]
    found = store.get_by_id(first_id)
    print(f"Read {first_id}: {found['amount']} {found['currency']}")

    store.add({"id": "DEMO_TEST_01", "transaction_type": "Payment", "amount": 500.0, "receiver": "Coffee Shop"})
    store.update("DEMO_TEST_01", {"amount": 750.0})
    store.delete("DEMO_TEST_01")
    print(f"Count after CRUD demo: {store.count()}")
