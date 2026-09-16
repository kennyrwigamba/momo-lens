# AI Usage Log

**Course:** Enterprise Web Development
**Project:** MoMo Lens - Mobile Money SMS Data Processing  
**Team:** Web Artisans  
**Members:** Ishimwe Rwigamba Kenny Louange, Maunice Akaliza  



## 1. Compliance Statement

We used Gemini as a pair programming assistant for syntax checks, schema validation and documentation formatting. All database architecture, table relationships, business logic and SMS data analysis were designed and implemented directly by us. Both members understand, tested and can defend every query, schema and document in this project.



## 2. Interaction Log

| Date | Team Member | Tool | Prompt | Assistance Provided | Where Applied |
|---|---|---|---|---|---|
| 2026-09-13 | Kenny Louange | Gemini | "Check MySQL syntax for table CHECK constraints on amount and balance." | Verified correct syntax for non-negative financial check constraints. | `database/database_setup.sql` |
| 2026-09-14 | Maunice Akaliza | Gemini | "Validate JSON Schema structure for required fields and nested objects." | Checked and helped with keyword accuracy (`$schema`, `type`, `items`, `required`). | `examples/json_schemas.json` |
| 2026-09-14 | Kenny Louange | Gemini | "Review SQL query joining transactions with categories using GROUP_CONCAT." | Checked query structure and verified `GROUP_CONCAT` separator syntax. | `database/crud_operations.sql` |
| 2026-09-15 | Kenny Louange | Gemini | "Check the formatting and the grammar" | Verified column alignment and readability for markdown tables. | `docs/MoMo_Lens_Database_Design_Document.pdf` |



## 3. Reflection

- **Syntax Verification:** Helped verify MySQL constraints and JSON Schema keywords quickly without guessing.
- **Efficiency:** Saved time on formatting tables so we could focus on data normalization, ERD relationships, and SQL testing.
- **Accountability:** Every piece of generated syntax was tested locally on MySQL and reviewed before being kept.
