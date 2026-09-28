"""Validation for the transaction JSON shape used by MoMo Lens."""

from datetime import datetime
import math
import re


STATUSES = {"COMPLETED", "PENDING", "FAILED", "REVERSED"}
USER_TYPES = {"INDIVIDUAL", "MERCHANT", "AGENT", "BANK", "SYSTEM"}


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _validate_user(user, field):
    _require(isinstance(user, dict), "%s must be an object" % field)
    _require(isinstance(user.get("user_id"), int) and not isinstance(user.get("user_id"), bool), "%s.user_id must be an integer" % field)
    phone = user.get("phone_number")
    _require(isinstance(phone, str) and re.fullmatch(r"[0-9]{10,15}", phone), "%s.phone_number must contain 10 to 15 digits" % field)
    name = user.get("full_name")
    _require(isinstance(name, str) and 2 <= len(name.strip()) <= 100, "%s.full_name must contain 2 to 100 characters" % field)
    _require(user.get("user_type") in USER_TYPES, "%s.user_type is invalid" % field)


def validate_transaction(transaction):
    _require(isinstance(transaction, dict), "Transaction must be a JSON object")
    required = ("transaction_id", "sender", "receiver", "amount", "currency", "fee", "balance_after", "tx_timestamp", "status", "categories")
    missing = [field for field in required if field not in transaction]
    _require(not missing, "Missing required fields: %s" % ", ".join(missing))
    transaction_id = transaction["transaction_id"]
    _require(isinstance(transaction_id, str) and 1 <= len(transaction_id) <= 64, "transaction_id must be a non-empty string of at most 64 characters")
    _validate_user(transaction["sender"], "sender")
    _validate_user(transaction["receiver"], "receiver")
    amount = transaction["amount"]
    fee = transaction["fee"]
    balance = transaction["balance_after"]
    _require(_is_number(amount) and amount > 0, "amount must be a positive number")
    _require(_is_number(fee) and fee >= 0, "fee must be a non-negative number")
    _require(_is_number(balance) and balance >= 0, "balance_after must be a non-negative number")
    currency = transaction["currency"]
    _require(isinstance(currency, str) and re.fullmatch(r"[A-Za-z]{3}", currency), "currency must be a three-letter code")
    _require(transaction["status"] in STATUSES, "status is invalid")
    timestamp = transaction["tx_timestamp"]
    _require(isinstance(timestamp, str), "tx_timestamp must be an ISO 8601 string")
    try:
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("tx_timestamp must be an ISO 8601 timestamp") from exc
    categories = transaction["categories"]
    _require(isinstance(categories, list), "categories must be an array")
    for category in categories:
        _require(isinstance(category, dict), "Each category must be an object")
        _require(isinstance(category.get("category_id"), int) and not isinstance(category.get("category_id"), bool), "category_id must be an integer")
        _require(isinstance(category.get("category_code"), str) and bool(category["category_code"]), "category_code must be a non-empty string")
        _require(isinstance(category.get("category_name"), str) and bool(category["category_name"]), "category_name must be a non-empty string")
        if "is_primary" in category:
            _require(isinstance(category["is_primary"], bool), "is_primary must be a boolean")
    if "raw_sms_body" in transaction:
        _require(transaction["raw_sms_body"] is None or isinstance(transaction["raw_sms_body"], str), "raw_sms_body must be a string or null")
