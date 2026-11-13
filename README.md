<div align="center">
  <img src="app/static/images/recuraops-logo.png" alt="RecuraOps logo" width="140">
  <h1>RecuraOps</h1>
  <p><strong>Cost intelligence and recovery workflows for operations teams</strong></p>
  <p>Find potential cost leaks, review AI-assisted recommendations, and track approved actions.</p>
</div>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/Flask-3.x-000000?logo=flask&logoColor=white" alt="Flask 3">
  <img src="https://img.shields.io/badge/Firebase-Realtime%20Database-FFCA28?logo=firebase&logoColor=black" alt="Firebase Realtime Database">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-lightgrey" alt="MIT License"></a>
</p>

> [!IMPORTANT]
> **Prototype and demo use only.** RecuraOps uses seeded Firebase data. Its action workflow updates demo records in Firebase; it does not connect to real payment, SaaS, or cloud control planes. AI recommendations and estimated savings are illustrative, not independently validated. Use a dedicated test Firebase project: `python seed_firebase.py` replaces the entire `/recuraops` database node.

## Overview

| Item | Details |
| --- | --- |
| Purpose | Identify potential invoice, subscription, and cloud-resource cost anomalies. |
| Workflow | Monitor records, detect anomalies, request AI recommendations, review proposed actions, and track verification. |
| Data | Demo records are loaded from `seed_data.json` into Firebase Realtime Database. |
| Interface | Flask web application with a dashboard, anomaly views, approval queue, and action log. |

## Capabilities

- Detect possible duplicate invoices, underused subscriptions, and idle cloud resources using rule-based checks.
- Request severity, reasoning, financial-impact estimates, and action recommendations from the configured OpenAI model.
- Review approval requests and track action status in an audit log.
- View dashboard KPIs and in-process agent status.
- Format monetary values in Indian rupees.

## Workflow

| Stage | Responsibility |
| --- | --- |
| Monitoring | Reads invoice, subscription, and cloud-resource records from Firebase on a configurable schedule. |
| Detection | Applies duplicate, utilization, CPU, and last-active rules to create anomaly records. |
| Decision | Requests a structured recommendation from the configured OpenAI model. |
| Approval | Presents proposed actions in the application for review. |
| Action | Updates the corresponding demo record after an approval is recorded. |
| Verification | Checks the record update and refreshes KPI summaries. |

The implementation uses Flask, Firebase Admin SDK, Firebase Authentication in the browser, OpenAI, and APScheduler.

## Getting started

### Requirements

- Python 3.10 or newer
- A Firebase project with Realtime Database and Authentication enabled
- A Firebase service-account JSON file
- An OpenAI API key for AI-generated recommendations

### 1. Clone and install

```bash
git clone https://github.com/supransekhar10/RecuraOps.git
cd RecuraOps

python -m venv .venv
```

Activate the environment, then install dependencies:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### 2. Configure the environment

Create a `.env` file in the repository root:

```dotenv
FLASK_SECRET_KEY=replace-with-a-long-random-secret
FLASK_DEBUG=True
APP_HOST=127.0.0.1
APP_PORT=5000

FIREBASE_CREDENTIALS=firebase_service_account.json
FIREBASE_DB_URL=https://your-project-default-rtdb.firebaseio.com
FIREBASE_API_KEY=your-firebase-web-api-key
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your-sender-id
FIREBASE_APP_ID=your-app-id

OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o

AGENT_SCAN_INTERVAL_MINUTES=5
ACTION_POLL_INTERVAL_MINUTES=2
```

Set additional thresholds in `app/config.py` as needed. Never commit `.env` or the service-account file. The service-account JSON path is relative to the working directory unless you provide an absolute path.

### 3. Add Firebase credentials

In Firebase Console, create a service-account key for your test project and save it at the configured `FIREBASE_CREDENTIALS` path. Configure Firebase Authentication and the Realtime Database URL for the same project.

### 4. Create demo users and load demo data

```bash
python seed_users.py
python seed_firebase.py
```

The user seeder contains sample demo credentials in source. Change or remove those credentials before sharing a deployment. The data seeder overwrites `/recuraops`; run it only against a disposable demo database.

### 5. Start the application

```bash
python run.py
```

Open [http://localhost:5000](http://localhost:5000) and sign in with a demo Firebase Authentication user.

## API

All listed endpoints require an authenticated application session.

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/kpi` | Return the KPI summary. |
| `GET` | `/api/anomalies` | Return anomalies ordered by detection time. |
| `POST` | `/api/run-scan` | Start a monitoring scan in the background. |
| `GET` | `/api/agent-status` | Return the in-process agent status. |

## Project structure

```text
app/
  actions/       Action-log routes
  agents/        Monitoring, detection, decision, action, and verification agents
  anomalies/     Anomaly list and detail routes
  api/           Authenticated JSON endpoints
  approvals/     Approval queue routes
  auth/          Login routes and session middleware
  dashboard/     Dashboard routes
  static/        CSS, JavaScript, and brand assets
  templates/     Jinja templates
  config.py      Environment-backed application configuration
run.py            Local Flask entry point
seed_data.json    Synthetic Firebase demo records
seed_firebase.py  Demo database seeder (overwrites /recuraops)
seed_users.py     Firebase Authentication demo-user seeder
requirements.txt  Python dependencies
```

## Security and limitations

- Set `FLASK_DEBUG=False` outside local development and use a unique, strong `FLASK_SECRET_KEY`.
- Keep the Firebase service-account key and OpenAI API key on the server. Restrict Firebase Authentication and Realtime Database access with project-specific rules.
- Replace or remove the sample credentials in `seed_users.py` before sharing or deploying the app.
- Treat seeded records, AI recommendations, and displayed savings as illustrative demo data.
- The included `run.py` uses Flask's development server. Configure a production WSGI server and deployment environment before exposing the application publicly.

## License

RecuraOps is released under the MIT License. See [LICENSE](LICENSE).
