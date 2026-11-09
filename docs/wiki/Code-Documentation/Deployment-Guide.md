# Deployment & Enterprise Configuration Guide

Complete operational guide for deploying the Study Progress Analysis system locally or in production environments.

---

## 🚀 1. Local Development Stack (Docker Compose)

The repository provides a root `docker-compose.yml` orchestrating PostgreSQL, the FastAPI backend, and the React frontend.

```bash
# 1. Clone both repositories into the root workspace
git clone https://github.com/poalelungi-ion/d2-project-client.git
git clone https://github.com/poalelungi-ion/d2-project-backend.git

# 2. Copy the environment configuration
cp .env.example .env

# 3. Boot the complete stack
docker compose up -d --build
```

### Published Ports & Services
* **Client Frontend:** [http://localhost:5173](http://localhost:5173)
* **Backend API & Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **PostgreSQL Database:** `localhost:5432` (`spa_user` / `spa_password` / `spa_db`)

---

## 🌐 2. Remote Server Deployment (Zero-Rebuild Architecture)

When hosting the instance on a remote VM, domain, or cloud server, clients connect across the network rather than through `localhost`.

### Step 1: Configure `.env`
Edit `.env` on the host:
```env
# Point to your server's public IP address or domain:
VITE_API_BASE_URL=http://<YOUR_SERVER_IP_OR_DOMAIN>:8000/api
CORS_ORIGINS=http://<YOUR_SERVER_IP_OR_DOMAIN>:5173
```

### Step 2: Runtime Container Injection
* The client container does **not** need to be recompiled!
* On startup, `/docker-entrypoint.d/40-generate-config.sh` creates `/usr/share/nginx/html/config.js` containing:
  ```javascript
  window.__APP_CONFIG__ = {
    API_BASE_URL: "http://<YOUR_SERVER_IP_OR_DOMAIN>:8000/api"
  };
  ```
* All connecting browsers automatically receive this address.
* To change the server address in the future: update `.env` and restart containers (`docker compose up -d`).

---

## 📦 3. Pulling from GitLab Container Registry

Pre-built Docker images are published to the GWDG GitLab Container Registry:

```bash
# 1. Authenticate with the GitLab Registry
docker login registry.gitlab.gwdg.de

# 2. Pull the latest images
docker pull registry.gitlab.gwdg.de/poalelungi-ion/d2-project-backend:latest
docker pull registry.gitlab.gwdg.de/poalelungi-ion/d2-project-client:latest

# 3. Launch isolated containers
docker run -d --name spa_db \
  -e POSTGRES_USER=spa_user \
  -e POSTGRES_PASSWORD=spa_password \
  -e POSTGRES_DB=spa_db \
  -p 5432:5432 \
  postgres:15-alpine

docker run -d --name spa_backend \
  --link spa_db:db \
  -e DATABASE_URL=postgresql://spa_user:spa_password@db/spa_db \
  -e JWT_SECRET=production-secret-key-change-me \
  -e CORS_ORIGINS="http://<server-ip>:5173" \
  -p 8000:8000 \
  registry.gitlab.gwdg.de/poalelungi-ion/d2-project-backend:latest

docker run -d --name spa_client \
  -e VITE_API_BASE_URL="http://<server-ip>:8000/api" \
  -p 5173:5173 \
  registry.gitlab.gwdg.de/poalelungi-ion/d2-project-client:latest
```

---

## 🛠️ 4. In-Browser Troubleshooting & Rescue Tool

If client instances encounter networking or CORS issues:
1. **Access Settings:** Click the **Settings (gear ⚙️)** icon in the header of the Sign In screen, or click the University logo when logged in.
2. **Test Connection:** Input the target backend URL and click **Test Connection** to send an instant ping probe.
3. **Save Override:** Click **Save & Apply** to override the base URL in that specific browser's `localStorage`.
4. **Reset Default:** Click **Reset Default** to immediately revert to the global container default configured in `.env`.
