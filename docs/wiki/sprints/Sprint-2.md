# D2-Project: Sprint 2 (Core Analytics, Attempts & Absence Normalization)

* **Official Kanban Board:** `D2-Project: Sprint 2` *(Created on: 09/03/2026 05:36 PM)*
* **Sprint Timeline:** `September 01, 2026 – September 14, 2026` (`01.09.2026 – 14.09.2026`)
* **Sprint Status:** Closed / Delivered
* **Git Release Branch:** [`release/sprint-2-v0.2.0-alpha`](https://gitlab.gwdg.de/sudarshan.bashyal/d2-project-client/-/tree/release/sprint-2-v0.2.0-alpha)
* **Git Release Tag:** [`v0.2.0-alpha`](https://gitlab.gwdg.de/sudarshan.bashyal/d2-project-client/-/tags/v0.2.0-alpha) (`release-sprint-2-v0.2.0-alpha`)
* **Target Delivery Release:** `v0.2.0-alpha` (Release Alpha 2)

---

## 📊 Sprint 2 Backlog Registry

| Work Item ID | Subject / User Story | Type | Status | Priority | Assignee | Sprint |
| :---: | :--- | :---: | :---: | :---: | :--- | :---: |
| **#96054** | Grade-Driven Pass/Fail Calculation & Absence Parsing | USER STORY | Closed | Normal | Yazan Al Rifaee | Sprint 2 |
| **#99859** | Aggregated Data View: Per-Person History | USER STORY | Closed | Normal | Ion Poalelungi | Sprint 2 |
| **#96055** | Categorize Exam Attempts & Handle Missing Study Programs | USER STORY | Closed | Normal | Sudarshan Bashyal | Sprint 2 |
| **#99879** | Drag and drop window malfunction | BUG | Closed | High | Ion Poalelungi | Sprint 2 |
| **#99881** | Semesters on the dashboard are sorted alphabetically, not chronologically | BUG | Closed | Normal | Anna Chiriciuc | Sprint 2 |
| **#95732** | Upload an exam data file | USER STORY | Closed | Normal | Sudarshan Bashyal | Sprint 2 |
| **#96053** | Validate required fields | USER STORY | Closed | Normal | Sudarshan Bashyal | Sprint 2 |
| **#99900** | Display Number of Exams Taken by Students per Semester | USER STORY | Closed | Normal | Ion Poalelungi | Sprint 2 |
| **#99895** | Redirect and Display Imported Data After Course Import | USER STORY | Closed | Normal | Anna Chiriciuc | Sprint 2 |

---

## 🎯 Key Capabilities Delivered in Sprint 2

1. **Grade-Driven Pass/Fail Calculation & Absence Normalization (#96054):**
   - Automatically computes passing threshold (`grade <= 4.0`), with distinctive absence status handling (`na` = Not Appeared, `ta` = Terminated Attempt, `ne` = Not Examined).
   - Displayed as color-coded pillow badges on student transcripts and course rosters.
2. **Aggregated Data View: Per-Person History (#99859):**
   - Longitudinal exam records aggregated per individual student across semesters.
3. **Attempt Categorization & Graceful Study Programs (#96055):**
   - Three-tier attempt categorization (`Exam 1`, `Exam 2`, `Other`).
   - Unassigned/empty study programs defaulted cleanly to `"Unassigned / Unknown"` without aborting valid uploads.
4. **Ingestion Polish & Bug Fixes (#99879, #99881, #99895):**
   - Resolved drag-and-drop window freeze on modern browser drops.
   - Enforced strict chronological semester ordering (Winter vs. Summer semester terms) replacing lexical alphabetical sorting.
   - Automatic redirection from the upload wizard directly to the imported course detail view.
5. **Exam Distribution Metrics (#99900):**
   - Summary count of exam sittings taken per student across academic terms.
