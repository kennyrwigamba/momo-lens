# In-Memory Transaction Store for MoMo Lens
# Stores transactions in both a list and a dictionary for fast CRUD operations

import sys
from datetime import datetime
from pathlib import Path

# Add project root to sys.path so imports work properly
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dsa.parse_xml import parse_sms_xml


class TransactionStore:
    def __init__(self):
        # A list to keep transactions in order
        self.transaction_list = []
        # A dictionary using transaction ID as key for fast O(1) lookup
        self.transaction_dict = {}

    # Load transactions from the XML file into memory
    def load_from_xml(self, xml_path):
        parsed_transactions = parse_sms_xml(xml_path)
        self.transaction_list.clear()
        self.transaction_dict.clear()

        for transaction in parsed_transactions:
            self.transaction_list.append(transaction)
            self.transaction_dict[transaction["id"]] = transaction

        return len(self.transaction_list)

    # Get all transactions, with optional limit and offset
    def get_all(self, limit=None, offset=0):
        if limit is not None:
            return self.transaction_list[offset : offset + limit]
        return list(self.transaction_list)

    # Find a single transaction by ID in O(1) time
    def get_by_id(self, transaction_id):
        return self.transaction_dict.get(str(transaction_id))

    # Add a new transaction to both list and dictionary
    def add(self, transaction_data):
        transaction_id = str(transaction_data.get("id") or f"tx_{len(self.transaction_dict) + 1}")
        
        # Check if ID already exists
        if transaction_id in self.transaction_dict:
            raise ValueError(f"Transaction with ID '{transaction_id}' already exists.")

        # Build clean transaction record with default values
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

        # Store in both list and dictionary
        self.transaction_list.append(record)
        self.transaction_dict[transaction_id] = record
        return record

    # Update an existing transaction
    def update(self, transaction_id, update_data):
        record = self.transaction_dict.get(str(transaction_id))
        if record is None:
            return None

        # Fields that are allowed to be updated
        allowed_fields = [
            "transaction_type",
            "amount",
            "currency",
            "fee",
            "balance_after",
            "sender",
            "receiver",
            "timestamp",
            "raw_sms_body",
        ]

        for field in allowed_fields:
            if field in update_data:
                # Convert numbers to float if needed
                if field in ("amount", "fee") and update_data[field] is not None:
                    record[field] = float(update_data[field])
                elif field == "balance_after" and update_data[field] is not None:
                    record[field] = float(update_data[field])
                else:
                    record[field] = update_data[field]

        return record

    # Delete a transaction by ID
    def delete(self, transaction_id):
        target_id = str(transaction_id)
        if target_id not in self.transaction_dict:
            return False

        # Remove from dictionary
        record = self.transaction_dict.pop(target_id)

        # Remove from list
        try:
            self.transaction_list.remove(record)
        except ValueError:
            self.transaction_list = [item for item in self.transaction_list if item["id"] != target_id]

        return True

    # Total number of transactions
    def count(self):
        return len(self.transaction_dict)

    # Clear all data
    def clear(self):
        self.transaction_list.clear()
        self.transaction_dict.clear()

    # Direct access to the list (used for linear search benchmark)
    @property
    def list(self):
        return self.transaction_list

    # Direct access to the dictionary (used for dict search benchmark)
    @property
    def dict(self):
        return self.transaction_dict


# Shared store instance
default_store = None


def get_default_store(xml_path=None):
    global default_store
    if default_store is None:
        default_store = TransactionStore()
        if xml_path is None:
            xml_path = Path(__file__).resolve().parent.parent / "modified_sms_v2.xml"
        default_store.load_from_xml(xml_path)
    return default_store


if __name__ == "__main__":
    store = TransactionStore()
    sample_xml = Path(__file__).resolve().parent.parent / "modified_sms_v2.xml"
    print(f"Loading {sample_xml} into store...")
    loaded_count = store.load_from_xml(sample_xml)
    print(f"Loaded {loaded_count} transactions.")

    # Test READ
    first_id = store.get_all(limit=1)[0]["id"]
    print(f"\n[READ] Searching for ID: {first_id}")
    found_transaction = store.get_by_id(first_id)
    print(f"Found: {found_transaction['sender']} -> {found_transaction['receiver']} ({found_transaction['amount']} {found_transaction['currency']})")

    # Test CREATE
    print("\n[CREATE] Adding a new transaction...")
    new_transaction = store.add({
        "id": "DEMO_TEST_01",
        "transaction_type": "Payment",
        "amount": 500.0,
        "receiver": "Coffee Shop",
        "sender": "Self",
    })
    print(f"Added ID: {new_transaction['id']}, total count: {store.count()}")

    # Test UPDATE
    print("\n[UPDATE] Changing amount to 750.0...")
    updated_transaction = store.update("DEMO_TEST_01", {"amount": 750.0})
    print(f"Updated amount: {updated_transaction['amount']}")

    # Test DELETE
    print("\n[DELETE] Deleting DEMO_TEST_01...")
    is_deleted = store.delete("DEMO_TEST_01")
    print(f"Deleted successfully: {is_deleted}, total count: {store.count()}")
