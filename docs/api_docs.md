# MoMo Lens REST API

Base URL: `http://127.0.0.1:8000`  
Data: `data/transactions.json` (create with `python -m dsa.parse_xml`)  
Auth: HTTP Basic, `admin` / `password` (`Authorization: Basic …` or `curl -u admin:password`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/transactions` | List all transactions |
| GET | `/transactions/{id}` | One transaction by id |
| POST | `/transactions` | Create (body validated by `api/schemas.py`) |
| PUT | `/transactions/{id}` | Update; URL id must match body `transaction_id` |
| DELETE | `/transactions/{id}` | Remove transaction |

GET bodies use flat SMS fields from the XML parser. POST/PUT use the nested JSON in `examples/complex_transaction.json`.

---

## GET /transactions

Returns every transaction in the store as a JSON array. Requires Basic Auth.

**Request**

```http
GET /transactions HTTP/1.1
Host: 127.0.0.1:8000
Authorization: Basic YWRtaW46cGFzc3dvcmQ=
```

**Response 200**

```json
[
  {
    "id": "76662021700",
    "transaction_id": "76662021700",
    "transaction_type": "Received",
    "amount": 2000.0,
    "currency": "RWF",
    "fee": 0.0,
    "balance_after": 2000.0,
    "sender": "Jane Smith",
    "receiver": "Self",
    "timestamp": "2024-05-10 16:30:51",
    "raw_sms_body": "..."
  }
]
```

**Response 401**

```json
{"error": "Authentication required"}
```

---

## GET /transactions/{id}

Returns one transaction by `id` or `transaction_id`. Requires Basic Auth.

**Request**

```http
GET /transactions/76662021700 HTTP/1.1
Host: 127.0.0.1:8000
Authorization: Basic YWRtaW46cGFzc3dvcmQ=
```

**Response 200**

Single object with the same fields as one list item above.

**Response 404**

```json
{"error": "Transaction not found"}
```

---

## POST /transactions

Creates a new transaction from the nested JSON body. Requires Basic Auth and a unique `transaction_id`.

**Request**

```http
POST /transactions HTTP/1.1
Host: 127.0.0.1:8000
Authorization: Basic YWRtaW46cGFzc3dvcmQ=
Content-Type: application/json

(body from examples/complex_transaction.json)
```

Use a new `transaction_id` if that id already exists in `data/transactions.json` (409).

**Response 201**

Created record (same JSON as request body).

**Response 400**

```json
{"error": "Missing required fields: ..."}
```

**Response 409**

```json
{"error": "Transaction already exists"}
```

---

## PUT /transactions/{id}

Replaces an existing transaction. Path `{id}` must match `transaction_id` in the body.

**Request**

```http
PUT /transactions/13947831685 HTTP/1.1
Host: 127.0.0.1:8000
Authorization: Basic YWRtaW46cGFzc3dvcmQ=
Content-Type: application/json

(body from examples/complex_transaction.json; transaction_id must be 13947831685)
```

**Response 200**

Updated record (request body echoed).

**Response 400**

Invalid JSON, validation error, or `"Path ID must match transaction_id"`.

**Response 404**

```json
{"error": "Transaction not found"}
```

---

## DELETE /transactions/{id}

Removes the transaction with the given id from the store.

**Request**

```http
DELETE /transactions/13947831685 HTTP/1.1
Host: 127.0.0.1:8000
Authorization: Basic YWRtaW46cGFzc3dvcmQ=
```

**Response 204**

Empty body on success.

**Response 404**

```json
{"error": "Transaction not found"}
```

---

## Error codes

| Code | When | Example body |
|------|------|----------------|
| 200 | GET one, PUT success | JSON transaction |
| 201 | POST success | JSON transaction |
| 204 | DELETE success | (empty) |
| 400 | Bad or invalid JSON body | `{"error": "..."}` |
| 401 | No or wrong Basic Auth | `{"error": "Authentication required"}` |
| 404 | Wrong path or unknown id | `{"error": "Not found"}` or `{"error": "Transaction not found"}` |
| 409 | POST with existing id | `{"error": "Transaction already exists"}` |

---

## Security (report)

Basic Auth sends credentials on every request; use HTTPS in production. Alternatives: JWT or OAuth2.

---

## curl

```bash
python -m dsa.parse_xml
python -m api.app

curl -u admin:password http://127.0.0.1:8000/transactions/76662021700
curl -i http://127.0.0.1:8000/transactions
curl -u admin:password -X POST http://127.0.0.1:8000/transactions \
  -H "Content-Type: application/json" \
  --data-binary @examples/complex_transaction.json
```
