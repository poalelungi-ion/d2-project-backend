# Sprint 2: Visual Analytics & Authenticated Identity

* **Sprint Timeline:** `September 01, 2026 – September 14, 2026` (`01.09.2026 – 14.09.2026`)
* **Sprint Status:** Completed
* **Target Delivery Release:** Release v2.0.0

---

## 🎯 Sprint 2 Objectives & Deliverables

1. **Enterprise Identity & Access (#95642):**
   - Implemented registration restricted to `@uni-hildesheim.de` domain.
   - Salted `bcrypt` password hashing (`BCRYPT_ROUNDS=12`).
   - In-memory JWT access tokens paired with rotating `httpOnly` refresh cookies.
   - Global session gate and automatic silent token refresh on 401s.
2. **Visual Analytics Suite:**
   - Longitudinal student trajectories over time using Recharts `LineChart`.
   - Comparative grade distribution histograms highlighting individual student standing.
   - Pass vs. Fail breakdown donuts.
3. **Exam Attempt Categorization (#96055):**
   - Added `attempt_type` (`Exam 1`, `Exam 2`, `Other`) to wizard and persistence schema.
   - Graceful study program handling allowing missing data without blocking uploads.
