# AI Usage Log

**Course:** Enterprise Web Development
**Project:** MoMo Lens - Mobile Money SMS Data Processing  
**Team:** Web Artisans  
**Members:** Ishimwe Rwigamba Kenny Louange, Maunice Akaliza, IBYISHAKA Jean Remy  



## 1. Compliance Statement

We used Gemini as a pair programming assistant for syntax checks, standard library discovery (such as regex patterns and XML parsing), schema validation, and documentation formatting. All core architectural decisions, data structures, routing logic, authentication flows, and SMS data extractions were designed, implemented, and tested directly by our team. All team members understand, tested, and can defend every line of code and document submitted.



## 2. Interaction Log

| Date | Team Member | Tool | Prompt | Assistance Provided | Where Applied |
|---|---|---|---|---|---|
| 2026-09-13 | Kenny Louange | Gemini | "Check MySQL syntax for table CHECK constraints on amount and balance." | Verified correct syntax for non-negative financial check constraints. | `database/database_setup.sql` |
| 2026-09-14 | Maunice Akaliza | Gemini | "Validate JSON Schema structure for required fields and nested objects." | Checked keyword accuracy (`$schema`, `type`, `items`, `required`). | `examples/json_schemas.json` |
| 2026-09-14 | Kenny Louange | Gemini | "Review SQL query joining transactions with categories using GROUP_CONCAT." | Checked query structure and verified `GROUP_CONCAT` separator syntax. | `database/crud_operations.sql` |
| 2026-09-15 | Kenny Louange | Gemini | "Check the formatting and the grammar" | Verified column alignment and readability for markdown tables. | `docs/MoMo_Lens_Database_Design_Document.pdf` |
| 2026-09-25 | Kenny Louange | Gemini | "What built-in Python module can parse an XML file without installing external packages like lxml or BeautifulSoup?" | Recommended `xml.etree.ElementTree` from Python's standard library to meet strict zero-dependency requirements. | `dsa/parse_xml.py` |
| 2026-09-25 | Kenny Louange | Gemini | "How to write Python re regex to extract transaction IDs with variations like 'TxId:' or 'Financial Transaction Id:' and comma-formatted amounts?" | Suggested non-capturing groups `(?:TxId|Financial Transaction Id)` and regex pattern `([\d,]+)` with `.replace(',', '')` helper. | `dsa/parse_xml.py` |
| 2026-09-26 | IBYISHAKA Jean Remy | Gemini | "How to split URL paths cleanly in BaseHTTPRequestHandler to support both /transactions and /transactions/{id}?" | Showed usage of standard library `urllib.parse.urlsplit` to break path segments cleanly without external routers. | `api/app.py` |
| 2026-09-26 | Kenny Louange | Gemini | "Which Python timer should I use to benchmark microsecond lookups between list search and dictionary lookup: time.time() or time.perf_counter()?" | Explained `time.perf_counter()` provides monotonic, high-resolution timing suitable for benchmarking CPU-bound operations. | `dsa/benchmark.py` |
| 2026-09-27 | Maunice Akaliza | Gemini | "How to decode standard HTTP Basic Auth headers using base64 and set the 401 WWW-Authenticate challenge header in http.server?" | Provided syntax for `base64.b64decode` on the `Authorization` header and sending header `WWW-Authenticate: Basic realm=\"MoMo Lens\"`. | `api/auth.py` |



## 3. Reflection

- **Standard Library Discovery:** Helped identify built-in modules (`re`, `xml.etree.ElementTree`, `urllib.parse`, `base64`) so we could fulfill the project requirement of using plain Python without external libraries.
- **Regex Construction:** Assisted in testing edge cases for SMS regex matching (unstructured SMS formats with missing labels or comma-separated currency values).
- **Benchmarking Precision:** Guided the choice of `time.perf_counter()` over `time.time()` for measuring microsecond differences in our DSA benchmark.
- **Accountability & Validation:** Every regex pattern and code suggestion was tested against the 1,600+ real records in `modified_sms_v2.xml` and reviewed by the team before committing.
