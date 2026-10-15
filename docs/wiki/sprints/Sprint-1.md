# D2-Project: Sprint 1 (Early Alpha Foundations & File Ingestion)

* **Official Kanban Board:** `D2-Project: Sprint 1` *(Created on: 08/14/2026 06:25 PM)*
* **Sprint Timeline:** `August 18, 2026 – August 31, 2026` (`18.08.2026 – 31.08.2026`)
* **Sprint Status:** Completed
* **Git Release Branch:** [`release/sprint-1-v0.1.0-alpha`](https://gitlab.gwdg.de/sudarshan.bashyal/d2-project-client/-/tree/release/sprint-1-v0.1.0-alpha)
* **Git Release Tag:** [`v0.1.0-alpha`](https://gitlab.gwdg.de/sudarshan.bashyal/d2-project-client/-/tags/v0.1.0-alpha) (`release-sprint-1-v0.1.0-alpha`)
* **Target Delivery Release:** `v0.1.0-alpha` (Alpha Release 1)

---

## 🎯 Sprint 1 Objectives & Deliverables

1. **Multi-Format Spreadsheet Ingestion Foundations:**
   - Initial file parsing engine for `.xlsx`, `.csv`, `.tsv`, and `.ods` via Pandas.
   - Dynamic file extension parser dispatch.
2. **Data Validation Engine:**
   - Mandatory field inspection: Matrikelnummer, First Name, Last Name, Semester.
   - Initial error boundary reporting for missing headers.
3. **Interactive AG Grid Review:**
   - 4-step wizard prototype with editable cells for inline corrections.
4. **Database Archival:**
   - Single atomic transaction guaranteeing zero partial writes on upload errors.
