# Sprint 1: Ingestion Pipeline & Data Foundations

* **Sprint Timeline:** `August 18, 2026 – August 31, 2026` (`18.08.2026 – 31.08.2026`)
* **Sprint Status:** Completed
* **Target Delivery Release:** Release v1.0.0

---

## 🎯 Sprint 1 Objectives & Deliverables

1. **Multi-Format Spreadsheet Ingestion (#95732):**
   - Built backend upload preview endpoint handling `.xlsx`, `.csv`, `.tsv`, and `.ods` via Pandas.
   - Dynamic MIME and extension parser dispatching to openpyxl, odfpy, and CSV engines.
2. **Data Validation Engine:**
   - Validating mandatory headers: Matrikelnummer, First Name, Last Name, Semester.
   - Flagging incomplete records with clear inline error lists.
3. **Interactive AG Grid Review:**
   - Implemented 4-step wizard with editable spreadsheet cells for in-place typo corrections.
   - Automatic deselection of approved absence codes (`na`, `ta`, `ne`).
4. **ACID Compliant Archival:**
   - Single atomic transaction (`db.flush()` + `db.commit()` / `db.rollback()`) guaranteeing zero partial saves.
