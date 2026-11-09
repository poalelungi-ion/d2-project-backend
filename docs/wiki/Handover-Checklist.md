# Project Handover & Delivery Checklist

This checklist is designed for project evaluators, client stakeholders, or incoming development teams receiving the **Study Progress Analysis (SPA)** platform.

---

## 📋 Handover Verification Package

* [x] **Client Source Code:** [`d2-project-client`](https://github.com/poalelungi-ion/d2-project-client) (Branch: `feature/login-settings-and-api-config` / `main`)
* [x] **Backend Source Code:** [`d2-project-backend`](https://github.com/poalelungi-ion/d2-project-backend) (Branch: `feature/cors-config-hardening` / `main`)
* [x] **Central Docker Compose Orchestration:** [`docker-compose.yml`](file:///c:/Users/ionut/Desktop/D2_Project/docker-compose.yml)
* [x] **Traceability Matrix:** [`wiki/Traceability-Matrix.md`](file:///c:/Users/ionut/Desktop/D2_Project/wiki/Traceability-Matrix.md) mapping all 27 Sprint 3 items
* [x] **Complete Project Wiki:** [`wiki/Home.md`](file:///c:/Users/ionut/Desktop/D2_Project/wiki/Home.md)
* [x] **Zero-Rebuild Container Entrypoint:** Dynamic runtime `/config.js` generator for seamless remote deployment

---

## 🔑 Default Credentials & Demonstration Accounts

When booting with `SEED_ON_STARTUP=true`, the following demonstrative records are pre-populated:

### 1. Default University Staff Accounts
* **Staff Member 1:** `poalelungi@uni-hildesheim.de`
* **Staff Member 2:** `chiriciuc@uni-hildesheim.de`
* **Staff Member 3:** `poalelungi@uni-hildesheim.de`
* **Default Password:** `Password123!` (or register any new `@uni-hildesheim.de` account)

### 2. Database Service Credentials
* **Host / Port:** `localhost:5432` (or service name `db` inside Docker network)
* **Username:** `spa_user`
* **Password:** `spa_password`
* **Database Name:** `spa_db`

---

## ⚙️ Environment Variables Verification

| Key | Default (Dev) | Production Target | Description |
| :--- | :--- | :--- | :--- |
| `VITE_API_BASE_URL` | `http://localhost:8000/api` | `http://<server-ip>:8000/api` | API endpoint called by clients' browsers |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | `http://<server-ip>:5173` | Exact comma-separated list of allowed web origins |
| `JWT_SECRET` | `insecure-development-secret-change-me` | Fresh 32-byte secret | Token signing key (`openssl rand -hex 32`) |
| `COOKIE_SECURE` | `false` | `true` | Enforces HTTPS-only delivery for refresh cookies |
| `POSTGRES_USER` | `spa_user` | Secure DB user | PostgreSQL database credentials |
| `POSTGRES_PASSWORD` | `spa_password` | Secure DB password | PostgreSQL database credentials |

---

## 💾 Database Backup & Restoration

### Backup Database to SQL Dump
```bash
docker compose exec db pg_dump -U spa_user spa_db > backup_spa_db.sql
```

### Restore Database from SQL Dump
```bash
cat backup_spa_db.sql | docker compose exec -T db psql -U spa_user -d spa_db
```

---

## ❓ Common Troubleshooting & Handover FAQ

### 1. "Failed to Fetch / Network Error" on Login
* **Cause:** The frontend browser cannot reach the backend URL, or CORS blocked the request.
* **Resolution:**
  1. Click the **Settings (gear ⚙️)** icon in the top-right header of the login screen.
  2. Enter the correct backend address (e.g. `http://localhost:8000/api` or `http://<server-ip>:8000/api`).
  3. Click **Test Connection** to verify network reachability.
  4. Ensure the origin you are opening (e.g. `http://localhost:5173`) is listed in `CORS_ORIGINS` in `.env`.

### 2. Husky / Symlink Commit Error on Windows
* **Cause:** Git hooks symlinks inside `.githooks` on Windows without elevated privileges.
* **Resolution:** Commit using `git commit --no-verify`.

### 3. CI Complexity Quality Gate Failed
* **Cause:** A component function exceeded 500 lines.
* **Resolution:** Extract self-contained UI sections into modular components (like `BackendApiConnectionSection.tsx` and `StudyProgramAliasesSection.tsx`).
