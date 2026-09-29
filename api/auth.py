"""Basic Authentication helpers for the MoMo Lens API."""

import base64
import os


def check_auth(headers):
    """Check the Authorization header and validate credentials."""

    authorization = headers.get("Authorization")

    if not authorization:
        return False

    if not authorization.startswith("Basic "):
        return False

    try:
        encoded_credentials = authorization.split(" ", 1)[1]
        decoded_credentials = base64.b64decode(
            encoded_credentials
        ).decode("utf-8")

        username, password = decoded_credentials.split(":", 1)

    except (ValueError, UnicodeDecodeError):
        return False

    expected_username = os.getenv("API_USERNAME", "admin")
    expected_password = os.getenv("API_PASSWORD", "password")

    return (
        username == expected_username
        and password == expected_password
    )
