# SQL to JSON Mapping Guide
**System:** MoMo Lens SMS Data Processing System  
**Team:** Web Artisans  
**Course:** Enterprise Web Development (ALU)  

---

## 1. Overview

Relational databases like MySQL store data across separate tables to keep records organized and avoid duplicates. However, web applications and APIs use JSON to send and receive data.

When converting SQL data to JSON, we use **nested objects and arrays** so related information is bundled together in a single API response rather than requiring multiple database queries.

This document explains how each SQL table, column, and relationship maps to our JSON format.

---

## 2. Table to JSON Mapping

### 2.1 Table: `users` → JSON `User` Object

| MySQL Column | MySQL Data Type | JSON Key | JSON Type | Notes |
|---|---|---|---|---|
| `user_id` | `INT` | `user_id` | `integer` | User ID number. |
| `phone_number` | `VARCHAR(20)` | `phone_number` | `string` | Phone number string. |
| `full_name` | `VARCHAR(100)` | `full_name` | `string` | Registered name. |
| `user_type` | `ENUM(...)` | `user_type` | `string` | Role (e.g. `INDIVIDUAL`, `MERCHANT`). |
| `created_at` | `DATETIME` | `created_at` | `string` | Date and time string (`YYYY-MM-DDTHH:mm:ssZ`). |

---

### 2.2 Table: `transaction_categories` → JSON `Category` Object

| MySQL Column | MySQL Data Type | JSON Key | JSON Type | Notes |
|---|---|---|---|---|
| `category_id` | `INT` | `category_id` | `integer` | Category ID number. |
| `category_code` | `VARCHAR(30)` | `category_code` | `string` | Short code (e.g. `P2P_TRANSFER`). |
| `category_name` | `VARCHAR(100)` | `category_name` | `string` | Display name of the category. |
| `description` | `VARCHAR(255)` | `description` | `string` / `null` | Category description. |
| `is_primary` *(from map)* | `TINYINT(1)` | `is_primary` | `boolean` | Converted from `1`/`0` to `true`/`false`. |

---

### 2.3 Table: `transactions` → Nested JSON `Transaction` Object

| MySQL Column / Join | MySQL Source | JSON Key | JSON Type | Notes |
|---|---|---|---|---|
| `transaction_id` | `transactions` | `transaction_id` | `string` | Transaction ID kept as string. |
| `sender_id` (FK) | `JOIN users` | `sender` | `object` | **Nested Object:** Full sender details. |
| `receiver_id` (FK) | `JOIN users` | `receiver` | `object` | **Nested Object:** Full receiver details. |
| `amount` | `transactions` | `amount` | `number` | Transferred amount. |
| `currency` | `transactions` | `currency` | `string` | Currency code (`RWF`). |
| `fee` | `transactions` | `fee` | `number` | Transaction fee. |
| `balance_after` | `transactions` | `balance_after` | `number` | Balance after transaction. |
| `tx_timestamp` | `transactions` | `tx_timestamp` | `string` | Transaction date and time. |
| `status` | `transactions` | `status` | `string` | Status (e.g. `COMPLETED`). |
| `raw_sms_body` | `transactions` | `raw_sms_body` | `string` | Original SMS message text. |
| **M:N Junction** | `JOIN transaction_category_map` | `categories` | `array` | **Nested Array:** List of categories for this transaction. |

---

### 2.4 Table: `system_logs` → JSON `SystemLog` Object

| MySQL Column | MySQL Data Type | JSON Key | JSON Type | Notes |
|---|---|---|---|---|
| `log_id` | `INT` | `log_id` | `integer` | Log entry ID. |
| `process_name` | `VARCHAR(50)` | `process_name` | `string` | Name of the process (e.g. `XML_PARSER`). |
| `status` | `ENUM(...)` | `status` | `string` | Run status (`SUCCESS`, `WARNING`, `ERROR`). |
| `records_processed` | `INT` | `records_processed` | `integer` | Number of processed records. |
| `message` | `TEXT` | `message` | `string` / `null` | Log message or error details. |
| `created_at` | `DATETIME` | `created_at` | `string` | Date and time the log was created. |

---

## 3. Data Type Conversions

1. **Numbers and Decimals:**
   - In MySQL, money values use `DECIMAL(12,2)` to prevent rounding errors. In JSON, these are converted to regular numbers (e.g. `25000.00`).

2. **Booleans (`true` / `false`):**
   - MySQL stores flags like `is_primary` as `TINYINT(1)` using `1` and `0`. In JSON, these are converted to boolean `true` or `false`.

3. **Dates and Times:**
   - MySQL `DATETIME` values (such as `2026-09-14 10:10:00`) are converted to standard ISO date strings (`"2026-09-14T10:10:00Z"`) so any frontend or API client can easily read them.

4. **Foreign Keys to Nested Objects:**
   - Instead of returning just foreign key IDs like `sender_id: 1` and `receiver_id: 5`, the API joins the tables and includes the complete sender and receiver objects inside the transaction. This gives the client all necessary information in a single response.
