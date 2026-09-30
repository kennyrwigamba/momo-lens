"""Small standard-library HTTP API for MoMo Lens transactions."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
from urllib.parse import urlsplit

from api.auth import check_auth
from api.db import TransactionStore
from api.schemas import validate_transaction

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA = PROJECT_ROOT / "data" / "transactions.json"


class TransactionHandler(BaseHTTPRequestHandler):
    """Serve CRUD operations for transactions as JSON."""

    store = TransactionStore(Path(os.environ.get("MOMO_LENS_DATA", DEFAULT_DATA)))

    def _require_auth(self):
        """Require valid Basic Authentication."""
        if check_auth(self.headers):
            return True

        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="MoMo Lens API"')
        self.send_header("Content-Type", "application/json; charset=utf-8")
        body = json.dumps({"error": "Authentication required"}).encode("utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        return False

    def _send_json(self, status, payload=None):
        body = b"" if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def _transaction_id(self):
        parts = [part for part in urlsplit(self.path).path.split("/") if part]
        if len(parts) == 1 and parts[0] == "transactions":
            return "collection"
        if len(parts) == 2 and parts[0] == "transactions":
            return parts[1]
        return None

    def _read_body(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0:
                raise ValueError("Request body is required")
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("Request body must contain valid JSON") from exc

    def do_GET(self):
        if not self._require_auth():
            return
        transaction_id = self._transaction_id()
        if transaction_id == "collection":
            return self._send_json(200, self.store.list_all())
        if transaction_id is None:
            return self._send_json(404, {"error": "Not found"})
        transaction = self.store.get(transaction_id)
        if transaction is None:
            return self._send_json(404, {"error": "Transaction not found"})
        self._send_json(200, transaction)

    def do_POST(self):
        if not self._require_auth():
            return
        if self._transaction_id() != "collection":
            return self._send_json(404, {"error": "Not found"})
        try:
            transaction = self._read_body()
            validate_transaction(transaction)
            if self.store.get(transaction["transaction_id"]) is not None:
                return self._send_json(409, {"error": "Transaction already exists"})
            self.store.create(transaction)
        except ValueError as exc:
            return self._send_json(400, {"error": str(exc)})
        self._send_json(201, transaction)

    def do_PUT(self):
        if not self._require_auth():
            return
        transaction_id = self._transaction_id()
        if not transaction_id or transaction_id == "collection":
            return self._send_json(404, {"error": "Not found"})
        try:
            transaction = self._read_body()
            validate_transaction(transaction)
            if transaction["transaction_id"] != transaction_id:
                return self._send_json(400, {"error": "Path ID must match transaction_id"})
            if self.store.get(transaction_id) is None:
                return self._send_json(404, {"error": "Transaction not found"})
            self.store.update(transaction_id, transaction)
        except ValueError as exc:
            return self._send_json(400, {"error": str(exc)})
        self._send_json(200, transaction)

    def do_DELETE(self):
        if not self._require_auth():
            return
        transaction_id = self._transaction_id()
        if not transaction_id or transaction_id == "collection":
            return self._send_json(404, {"error": "Not found"})
        if not self.store.delete(transaction_id):
            return self._send_json(404, {"error": "Transaction not found"})
        self._send_json(204)

    def log_message(self, format, *args):
        print("%s - %s" % (self.address_string(), format % args))


def main():
    host = os.environ.get("MOMO_LENS_HOST", "127.0.0.1")
    port = int(os.environ.get("MOMO_LENS_PORT", "8000"))
    store = TransactionHandler.store
    count = len(store.list_all())
    print("Data file: %s (%s records)" % (store.path.resolve(), count))
    server = ThreadingHTTPServer((host, port), TransactionHandler)
    print("MoMo Lens API listening on http://%s:%s" % (host, port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
