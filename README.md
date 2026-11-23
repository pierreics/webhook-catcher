# 🪝 Webhook Catcher

A lightweight, self-hosted HTTP webhook inspection service built with **Flask**, **PostgreSQL**, and **Docker**. Generate unique webhook URLs, capture incoming HTTP traffic, and inspect headers, query parameters, and payloads via a REST API.

---

## 🛠 Tech Stack

* **Backend:** Python 3, Flask (Blueprints)
* **Database:** PostgreSQL (`psycopg` 3)
* **Deployment:** Docker & Docker Compose

---

## 🚀 Quick Start

**1. Create a `.env` file in the project root:**
```env
SECRET_KEY=change-me-to-a-random-secret
DATABASE_URL=postgresql://postgres:postgres@db:5432/webhooks
```

**2. Build and start the containers:**
```bash
docker compose up --build -d
```

**3. Verify with the end-to-end test script:**
```bash
chmod +x test.sh && ./test.sh
```

---

## 📡 API Reference

| Method | Endpoint | Auth | Description |
| :--- | :--- | :---: | :--- |
| `GET` | `/health` | — | Service health check |
| `POST` | `/register` | — | Register a new user account |
| `POST` | `/login` | — | Authenticate and start a session |
| `POST` | `/endpoints` | ✓ | Create a new webhook endpoint |
| `GET` | `/endpoints` | ✓ | List all owned endpoints |
| `DELETE` | `/endpoints/<id>` | ✓ | Delete an endpoint and its history |
| `GET` | `/endpoints/<id>/requests` | ✓ | Retrieve captured requests (newest first) |
| `ANY` | `/c/<slug>` | — | Public endpoint to receive webhooks |

---

## 💻 Example Workflow

```bash
# 1. Register & log in (saves session cookie)
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "strongpassword"}'

curl -X POST -c cookie.txt http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "strongpassword"}'

# 2. Create a webhook endpoint (returns "id" and "slug")
curl -X POST -b cookie.txt http://localhost:5000/endpoints \
  -H "Content-Type: application/json" \
  -d '{"name": "Stripe Hook"}'

# 3. Send a test webhook to /c/<slug>
curl -X POST "http://localhost:5000/c/<slug>?source=cli" \
  -H "Content-Type: application/json" \
  -d '{"event": "payment.succeeded", "amount": 2500}'

# 4. Inspect captured requests
curl -b cookie.txt http://localhost:5000/endpoints/1/requests
```