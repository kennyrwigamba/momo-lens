"""Parse modified_sms_v2.xml into a list of transaction dictionaries"""

import json
import re
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

RWF = r"(?:RWF|Rwf|FRW|Frw)"


def clean_amount(text):
    if not text:
        return 0.0
    try:
        return float(text.replace(",", "").strip())
    except ValueError:
        return 0.0


def first_amount(body, pattern):
    match = re.search(pattern, body, re.IGNORECASE)
    return clean_amount(match.group(1)) if match else 0.0


def first_name(body, pattern, default):
    match = re.search(pattern, body, re.IGNORECASE)
    return match.group(1).strip() if match else default


def classify_sms(body):
    # MoMo texts use different templates. So,we read keywords in the body, then regex for amount and names
    lower = body.lower()
    amount = 0.0
    sender = "Unknown"
    receiver = "Unknown"
    transaction_type = "Other"

    if "one-time password" in lower or "otp" in lower:
        return "OTP", amount, "MTN MoMo", "Self"

    if "withdrawn" in lower:
        return (
            "Cash-Out",
            first_amount(body, r"withdrawn\s+([\d,]+)"),
            "Self",
            first_name(body, r"via agent:\s*([A-Za-z\s]+)(?:\([^\)]+\))?", "Agent"),
        )

    if "received" in lower and "from" in lower:
        return (
            "Received",
            first_amount(body, r"received\s+([\d,]+)"),
            first_name(body, r"from\s+([A-Za-z\s]+)(?:\([^\)]+\))?", "Sender"),
            "Self",
        )

    if "transferred to" in lower or "transferred" in lower:
        amount = first_amount(body, rf"([\d,]+)\s*{RWF}\s+transferred")
        if not amount:
            amount = first_amount(body, r"transferred\s+([\d,]+)")
        return (
            "Transfer",
            amount,
            "Self",
            first_name(body, r"transferred to\s+([A-Za-z\s]+)(?:\([^\)]+\))?", "Recipient"),
        )

    if "bank deposit" in lower or "cash deposit" in lower or "deposited" in lower:
        return (
            "Deposit",
            first_amount(body, r"(?:deposit of|deposited)\s+([\d,]+)"),
            "Bank / Agent",
            "Self",
        )

    if "airtime" in lower or "umaze kugura" in lower:
        return (
            "Airtime",
            first_amount(body, rf"([\d,]+)\s*{RWF}"),
            "Self",
            "MTN Airtime / Bundle",
        )

    if "reversed" in lower or "reversal" in lower:
        return (
            "Reversal",
            first_amount(body, rf"([\d,]+)\s*{RWF}"),
            "MTN MoMo",
            "Self",
        )

    if "payment of" in lower:
        return (
            "Payment",
            first_amount(body, r"payment of\s+([\d,]+)"),
            "Self",
            first_name(body, r"to\s+([A-Za-z\s]+)(?:\s+\d+)?\s+has been completed", "Merchant"),
        )

    if "transaction of" in lower:
        return (
            "Payment",
            first_amount(body, r"transaction of\s+([\d,]+)"),
            "Self",
            first_name(body, r"by\s+([A-Z0-9\s]+?)\s+on your", "Merchant"),
        )

    amount = first_amount(body, rf"([\d,]+)\s*{RWF}")
    return transaction_type, amount, sender, receiver


def parse_sms_record(sms_node, index):
    body = sms_node.get("body", "").strip()
    transaction_type, amount, sender, receiver = classify_sms(body)

    tx_id = re.search(r"(?:TxId|Financial Transaction Id)\s*[:.]?\s*(\d+)", body, re.IGNORECASE)
    record_id = tx_id.group(1) if tx_id else f"sms_{index}"

    time_match = re.search(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})", body)
    if time_match:
        timestamp = time_match.group(1)
    elif sms_node.get("date", "").isdigit():
        try:
            timestamp = datetime.fromtimestamp(int(sms_node.get("date")) / 1000).strftime("%Y-%m-%d %H:%M:%S")
        except (OSError, ValueError):
            timestamp = sms_node.get("readable_date", "")
    else:
        timestamp = sms_node.get("readable_date", "")

    fee_match = re.search(r"Fee\s+(?:was|is|paid)?\s*[:.]?\s*([\d,]+)", body, re.IGNORECASE)
    balance_match = re.search(
        r"(?:new balance|NEW BALANCE|balance is)\s*[:.]?\s*([\d,]+)", body, re.IGNORECASE
    )

    return {
        "id": record_id,
        "transaction_type": transaction_type,
        "amount": amount,
        "currency": "RWF",
        "fee": clean_amount(fee_match.group(1)) if fee_match else 0.0,
        "balance_after": clean_amount(balance_match.group(1)) if balance_match else None,
        "sender": sender,
        "receiver": receiver,
        "timestamp": timestamp,
        "raw_sms_body": body,
    }


def parse_sms_xml(file_path, include_otp=False):
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"SMS XML file not found: {path}")

    records = []
    for index, sms_node in enumerate(ET.parse(path).getroot(), start=1):
        record = parse_sms_record(sms_node, index)
        if include_otp or record["transaction_type"] != "OTP":
            records.append(record)
    return records


def write_transactions_json(records, out_path):
    """Save parsed records to JSON"""
    payload = []
    for record in records:
        row = dict(record)
        row["transaction_id"] = row["id"]
        payload.append(row)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return len(payload), out_path


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    xml_file = project_root / "modified_sms_v2.xml"
    out_file = project_root / "data" / "transactions.json"

    transactions = parse_sms_xml(xml_file)
    count, path = write_transactions_json(transactions, out_file)

    print(f"Parsed {count} transactions from {xml_file.name}")
    print(f"Wrote {path}")
    if transactions:
        print("Sample:", transactions[0])
