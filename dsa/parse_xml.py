# XML Parser for MoMo SMS dataset
# Extracts financial transactions from modified_sms_v2.xml into simple Python dictionaries.

import re
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET


# Helper function to convert amount strings with commas to a clean float
def clean_amount(amount_text):
    if not amount_text:
        return 0.0
    cleaned_text = amount_text.replace(",", "").strip()
    try:
        return float(cleaned_text)
    except ValueError:
        return 0.0


# Extract telecom transaction ID from SMS body, or fallback to sms_{index}
def extract_id(body, index):
    match = re.search(r"(?:TxId|Financial Transaction Id)\s*[:.]?\s*(\d+)", body, re.IGNORECASE)
    if match:
        return match.group(1)
    return f"sms_{index}"


# Extract timestamp from SMS body or fall back to XML attributes
def extract_timestamp(body, sms_node):
    # Try finding timestamp in body (format: YYYY-MM-DD HH:MM:SS)
    match = re.search(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})", body)
    if match:
        return match.group(1)

    # Fallback to XML date (epoch milliseconds)
    date_milliseconds = sms_node.get("date", "")
    if date_milliseconds and date_milliseconds.isdigit():
        try:
            return datetime.fromtimestamp(int(date_milliseconds) / 1000.0).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass

    # Fallback to readable_date attribute
    return sms_node.get("readable_date", "")


# Extract network transaction fee from SMS body
def extract_fee(body):
    match = re.search(r"Fee\s+(?:was|is|paid)?\s*[:.]?\s*([\d,]+)", body, re.IGNORECASE)
    if match:
        return clean_amount(match.group(1))
    return 0.0


# Extract account balance after the transaction
def extract_balance(body):
    match = re.search(r"(?:new balance|NEW BALANCE|balance is)\s*[:.]?\s*([\d,]+)", body, re.IGNORECASE)
    if match:
        return clean_amount(match.group(1))
    return None


# Parse an individual <sms> XML element into a transaction dictionary
def parse_sms_record(sms_node, index):
    body = sms_node.get("body", "").strip()
    body_lower = body.lower()

    # Extract common core fields
    transaction_id = extract_id(body, index)
    timestamp = extract_timestamp(body, sms_node)
    fee = extract_fee(body)
    balance_after = extract_balance(body)

    amount = 0.0
    currency = "RWF"
    sender = "Unknown"
    receiver = "Unknown"
    transaction_type = "Other"

    # 1. Non-financial OTP messages
    if "one-time password" in body_lower or "otp" in body_lower:
        transaction_type = "OTP"
        sender = "MTN MoMo"
        receiver = "Self"

    # 2. Agent Cash-Out (Withdrawal)
    elif "withdrawn" in body_lower:
        transaction_type = "Cash-Out"
        amount_match = re.search(r"withdrawn\s+([\d,]+)", body, re.IGNORECASE)
        if amount_match:
            amount = clean_amount(amount_match.group(1))
        sender = "Self"
        agent_match = re.search(r"via agent:\s*([A-Za-z\s]+)(?:\([^\)]+\))?", body)
        receiver = agent_match.group(1).strip() if agent_match else "Agent"

    # 3. Received Money from another user
    elif "received" in body_lower and "from" in body_lower:
        transaction_type = "Received"
        amount_match = re.search(r"received\s+([\d,]+)", body, re.IGNORECASE)
        if amount_match:
            amount = clean_amount(amount_match.group(1))
        sender_match = re.search(r"from\s+([A-Za-z\s]+)(?:\([^\)]+\))?", body)
        sender = sender_match.group(1).strip() if sender_match else "Sender"
        receiver = "Self"

    # 4. P2P Transfer (Transfer to someone else)
    elif "transferred to" in body_lower or "transferred" in body_lower:
        transaction_type = "Transfer"
        amount_match = re.search(r"([\d,]+)\s*(?:RWF|Rwf|FRW|Frw)\s+transferred", body, re.IGNORECASE)
        if not amount_match:
            amount_match = re.search(r"transferred\s+([\d,]+)", body, re.IGNORECASE)
        if amount_match:
            amount = clean_amount(amount_match.group(1))
        receiver_match = re.search(r"transferred to\s+([A-Za-z\s]+)(?:\(([^\)]+)\))?", body)
        receiver = receiver_match.group(1).strip() if receiver_match else "Recipient"
        sender = "Self"

    # 5. Bank Deposit or Agent Cash Deposit
    elif "bank deposit" in body_lower or "cash deposit" in body_lower or "deposited" in body_lower:
        transaction_type = "Deposit"
        amount_match = re.search(r"(?:deposit of|deposited)\s+([\d,]+)", body, re.IGNORECASE)
        if amount_match:
            amount = clean_amount(amount_match.group(1))
        sender = "Bank / Agent"
        receiver = "Self"

    # 6. Airtime or Internet Bundle Purchase
    elif "airtime" in body_lower or "umaze kugura" in body_lower:
        transaction_type = "Airtime"
        amount_match = re.search(r"([\d,]+)\s*(?:RWF|Rwf|FRW|Frw)", body, re.IGNORECASE)
        if amount_match:
            amount = clean_amount(amount_match.group(1))
        sender = "Self"
        receiver = "MTN Airtime / Bundle"

    # 7. Reversed Transaction
    elif "reversed" in body_lower or "reversal" in body_lower:
        transaction_type = "Reversal"
        amount_match = re.search(r"([\d,]+)\s*(?:RWF|Rwf|FRW|Frw)", body, re.IGNORECASE)
        if amount_match:
            amount = clean_amount(amount_match.group(1))
        sender = "MTN MoMo"
        receiver = "Self"

    # 8. Merchant / Utility Payment
    elif "payment of" in body_lower:
        transaction_type = "Payment"
        amount_match = re.search(r"payment of\s+([\d,]+)", body, re.IGNORECASE)
        if amount_match:
            amount = clean_amount(amount_match.group(1))
        receiver_match = re.search(r"to\s+([A-Za-z\s]+)(?:\s+\d+)?\s+has been completed", body)
        receiver = receiver_match.group(1).strip() if receiver_match else "Merchant"
        sender = "Self"

    # 9. Third-party direct payment
    elif "transaction of" in body_lower:
        transaction_type = "Payment"
        amount_match = re.search(r"transaction of\s+([\d,]+)", body, re.IGNORECASE)
        if amount_match:
            amount = clean_amount(amount_match.group(1))
        receiver_match = re.search(r"by\s+([A-Z0-9\s]+?)\s+on your", body)
        receiver = receiver_match.group(1).strip() if receiver_match else "Merchant"
        sender = "Self"

    # 10. General amount fallback for any other format
    else:
        amount_match = re.search(r"([\d,]+)\s*(?:RWF|Rwf|FRW|Frw)", body, re.IGNORECASE)
        if amount_match:
            amount = clean_amount(amount_match.group(1))

    return {
        "id": transaction_id,
        "transaction_type": transaction_type,
        "amount": amount,
        "currency": currency,
        "fee": fee,
        "balance_after": balance_after,
        "sender": sender,
        "receiver": receiver,
        "timestamp": timestamp,
        "raw_sms_body": body,
    }


# Parse the XML SMS file and return a list of transactions
def parse_sms_xml(file_path, include_otp=False):
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"SMS XML file not found at: {path}")

    tree = ET.parse(path)
    root = tree.getroot()

    transactions = []
    for index, sms_node in enumerate(root, start=1):
        record = parse_sms_record(sms_node, index)
        # Skip OTP messages if include_otp is False
        if not include_otp and record["transaction_type"] == "OTP":
            continue
        transactions.append(record)

    return transactions


if __name__ == "__main__":
    sample_file = Path(__file__).resolve().parent.parent / "modified_sms_v2.xml"
    print(f"Parsing {sample_file}...")
    transactions = parse_sms_xml(sample_file)
    print(f"Successfully parsed {len(transactions)} transactions.")

    if transactions:
        print("\nFirst transaction sample:")
        first_transaction = transactions[0]
        for key, value in first_transaction.items():
            print(f"  {key}: {value}")
