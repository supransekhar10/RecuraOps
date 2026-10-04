# RecuraOps 🤖💸
### Autonomous Cost Intelligence & Recovery Engine

> **RecuraOps** is a 5-agent AI-powered platform that autonomously detects, decides on, and recovers enterprise cost leakages — from duplicate invoices to idle cloud resources — with human approval at every step.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask)](https://flask.palletsprojects.com)
[![Firebase](https://img.shields.io/badge/Firebase-Realtime%20DB-orange?logo=firebase)](https://firebase.google.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-green?logo=openai)](https://openai.com)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](LICENSE)

---

## 🎯 What It Does

| Problem | RecuraOps Solution |
|---|---|
| Duplicate invoices paid twice | Detection Agent → flags same vendor/amount/ref within 30 days |
| SaaS licenses nobody uses | Detection Agent → flags < 15% utilization |
| Cloud servers sitting idle | Detection Agent → flags CPU < 5%, inactive > 14 days |
| Cost spikes with no explanation | ML IsolationForest + Z-score detects statistical anomalies |
| Analysts spend weeks auditing | RecuraOps scans everything in **< 5 minutes**, continuously |

**In our demo scenario:** ₹29,59,200 in annual cost leakage identified across just 6 issues.

---

## 🏗️ Architecture — 5-Agent Pipeline

```
Firebase Realtime DB
       │
       ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Monitoring Agent│────▶│ Detection Agent  │────▶│ Decision Agent  │
│ (every 5 min)   │     │ Rules + ML       │     │ GPT-4o Reasoning│
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                           │
                                              ┌────────────▼────────────┐
                                              │  👤 Human Approval Gate  │
                                              └────────────┬────────────┘
                                                           │
                                              ┌────────────▼────────────┐    ┌──────────────────┐
                                              │    Action Agent         │───▶│ Verification Agent│
                                              │ Executes Approved Tasks │    │ Confirms + KPIs  │
                                              └─────────────────────────┘    └──────────────────┘
```

### Agents

| Agent | Role | Technology |
|---|---|---|
| **Monitoring Agent** | Fetches vendor invoices, SaaS subscriptions, cloud resources every 5 min | Firebase Admin SDK + APScheduler |
| **Detection Agent** | Rule-based checks + ML anomaly detection | IsolationForest, Z-score (scikit-learn) |
| **Decision Agent** | AI reasoning — severity, financial impact, recommended action | OpenAI GPT-4o |
| **Action Agent** | Executes: block_payment, cancel_licenses, shutdown_resource, notify | Firebase writes |
| **Verification Agent** | Confirms action success, updates KPI summary | Firebase Admin SDK |

---

## ✨ Features

- **Dashboard** — Live KPIs: savings realized, active issues, pending approvals, actions executed
- **Anomaly Feed** — Color-coded severity (Critical → Low), AI-generated descriptions
- **Anomaly Detail** — Full GPT-4o reasoning, financial impact (monthly + annual), recommended action
- **Approvals Queue** — One-click approve/reject with confirmation modal and projected savings
- **Action Log** — Complete audit trail: who approved, what was executed, savings locked in
- **Agent Status Widget** — Live status dots for all 5 agents in the sidebar
- **INR Formatting** — All monetary values in Indian number format (₹10,56,000)
- **Pastel Design System** — Premium UI with Fraunces + DM Sans fonts, Lucide icons

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Firebase project with Realtime Database enabled
- OpenAI API key (GPT-4o access)

### 1. Clone the Repository

```bash
git clone https://github.com/supransekhar10/RecuraOps.git
cd RecuraOps
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Flask
FLASK_SECRET_KEY=your-secret-key-here
FLASK_DEBUG=True
APP_HOST=0.0.0.0
APP_PORT=5000

# Firebase
FIREBASE_CREDENTIALS=firebase_service_account.json
FIREBASE_DB_URL=https://your-project-default-rtdb.firebaseio.com
FIREBASE_API_KEY=your-web-api-key
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your-sender-id
FIREBASE_APP_ID=your-app-id

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key

# Agent Config
AGENT_SCAN_INTERVAL_MINUTES=5
ACTION_POLL_INTERVAL_MINUTES=2
```

### 4. Add Firebase Service Account

Download your Firebase service account JSON from:
> Firebase Console → Project Settings → Service Accounts → Generate New Private Key

Save it as `firebase_service_account.json` in the project root.

### 5. Create Firebase Auth Users

```bash
python seed_users.py
```

This creates 3 demo users:
| Email | Password | Role |
|---|---|---|
| `admin@recuraops.io` | `Admin@123` | Admin (CFO) |
| `analyst@recuraops.io` | `Analyst@123` | Analyst |
| `approver@recuraops.io` | `Approver@123` | Approver |

### 6. Seed Demo Data

```bash
python seed_firebase.py
```

Seeds the Firebase Realtime DB with:
- 6 vendor invoices (with a duplicate)
- 4 SaaS subscriptions (with underutilized ones)
- 4 cloud resources (with idle instances)
- Pre-generated anomalies, approval requests, and action log

### 7. Run the Application

```bash
python run.py
```

Open **http://localhost:5000** — login with any demo account above.

---

## 📁 Project Structure

```
RecuraOps/
├── app/
│   ├── __init__.py          # Flask app factory + scheduler + template filters
│   ├── config.py            # Environment config loader
│   ├── auth/
│   │   ├── routes.py        # Login / logout routes
│   │   └── middleware.py    # @require_auth decorator
│   ├── dashboard/
│   │   └── routes.py        # Dashboard KPIs + anomaly feed
│   ├── anomalies/
│   │   └── routes.py        # Anomaly list + detail view
│   ├── approvals/
│   │   └── routes.py        # Approval queue + approve/reject actions
│   ├── actions/
│   │   └── routes.py        # Action audit log
│   ├── api/
│   │   └── routes.py        # REST API: /api/kpi, /api/anomalies, /api/run-scan
│   ├── agents/
│   │   ├── __init__.py      # Agent status registry
│   │   ├── monitoring_agent.py   # Data fetcher (APScheduler)
│   │   ├── detection_agent.py    # Rule-based + ML anomaly detection
│   │   ├── decision_agent.py     # GPT-4o reasoning engine
│   │   ├── action_agent.py       # Action executor
│   │   └── verification_agent.py # Post-action verification
│   ├── ml/
│   │   └── anomaly_detector.py   # IsolationForest + Z-score helpers
│   ├── static/
│   │   ├── css/
│   │   │   ├── main.css          # Design system tokens + layout
│   │   │   └── components.css    # KPI cards, tables, modals, timeline
│   │   ├── js/
│   │   │   ├── firebase-init.js  # Firebase Web SDK auth flow
│   │   │   └── dashboard.js      # Chart.js donut, KPI polling, scan button
│   │   └── images/
│   │       └── recuraops-logo.png
│   └── templates/
│       ├── base.html             # Sidebar layout, agent status widget
│       ├── auth/login.html       # Firebase auth login card
│       ├── dashboard/index.html  # KPI grid + anomaly feed + chart
│       ├── anomalies/
│       │   ├── list.html         # Filterable anomaly table
│       │   └── detail.html       # Full AI reasoning panel
│       ├── approvals/index.html  # Approval cards + confirm modal
│       └── actions/log.html      # Audit trail table
├── .env                     # ⚠️ Not committed — see setup above
├── firebase_service_account.json  # ⚠️ Not committed — add manually
├── requirements.txt
├── run.py                   # App entry point
├── seed_firebase.py         # Demo data seeder
└── seed_users.py            # Firebase Auth user creator
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/kpi` | Current KPI summary JSON |
| `GET` | `/api/anomalies` | All anomalies JSON |
| `POST` | `/api/run-scan` | Manually trigger Monitoring Agent |
| `GET` | `/api/agent-status` | Live agent health + last run timestamps |

---

## 🧠 Detection Logic

### Rule-Based Checks
| Rule | Trigger Condition |
|---|---|
| Duplicate Invoice | Same vendor + amount + reference number, within 30 days |
| Cost Spike | Current month spend > 3-month average × 1.20 |
| Inactive Subscription | License utilization < 15% |
| Idle Cloud Resource | CPU < 5% AND last active > 14 days |

### Machine Learning
- **IsolationForest** (scikit-learn) — detects statistical outliers in time-series spend data
- **Z-score** (scipy) — flags per-vendor deviations beyond 2σ threshold

### AI Decision Engine (GPT-4o)
For each confirmed anomaly, the Decision Agent sends a structured prompt to GPT-4o and receives:
- `severity` — critical / high / medium / low
- `recommended_action` — block_payment / cancel_licenses / shutdown_resource / notify_only
- `reasoning` — detailed natural-language explanation
- `financial_impact_monthly` / `financial_impact_annual` — rupee values
- `confidence_score` — 0.0–1.0

---

## 📦 Dependencies

```
flask
firebase-admin
openai
scikit-learn
scipy
numpy
apscheduler
python-dotenv
requests
```

Install all with:
```bash
pip install -r requirements.txt
```

---

## 🔐 Security Notes

- `.env` and `firebase_service_account.json` are in `.gitignore` — **never commit them**
- Firebase ID tokens are verified server-side via `firebase-admin` on every protected route
- Sessions are server-side with a secret key
- The `@require_auth` middleware protects all non-login routes

---
## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
