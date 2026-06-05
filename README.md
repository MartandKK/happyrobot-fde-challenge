# HappyRobot FDE Technical Challenge - Inbound Carrier Sales

## Overview

This project is a proof of concept for automating inbound carrier sales calls for a freight brokerage.

A carrier calls through a HappyRobot web call, provides an MC number, gets verified, searches for an available load, negotiates pricing, and has the final offer outcome saved to a custom dashboard.

The solution includes a HappyRobot inbound voice workflow, FastAPI backend, FMCSA-ready carrier verification, load search, negotiation, offer saving, a custom dashboard outside HappyRobot analytics, and Dockerized deployment on Render.

---

## Live Links

Health Check:
https://happyrobot-fde-backend.onrender.com/health

Dashboard:
https://happyrobot-fde-backend.onrender.com/dashboard

GitHub Repository:
https://github.com/MartandKK/happyrobot-fde-challenge

HappyRobot Workflow:
https://platform.happyrobot.ai/fdemartandkarnik/workflows/z6uyqu3i2kbd/editor/oja2egww8awd
Note: This link may require HappyRobot workspace access.

Demo Video:
https://drive.google.com/file/d/1CK-oh-iKp0AdJK8gp1Mz1cn2VdFyZyPH/view?usp=sharing

---

## Demo Path

Carrier says:

```text
My MC number is 123456.
I’m looking for a dry van load from Dallas to Phoenix.
Yes, but can you do $2,200?
```

Expected result:

```text
Carrier: Sample Express LLC
Load: L1001
Lane: Dallas, TX → Phoenix, AZ
Equipment: Dry Van
Listed Rate: $2,100
Final Offer: $2,200
Outcome: accepted_counteroffer
Sentiment: positive
```

Expected HappyRobot tool order:

```text
verify_carrier → find_available_loads → negotiate_rate → submit_offer
```

---

## Architecture

```text
HappyRobot Web Call
        ↓
Inbound Voice Agent
        ↓
FastAPI Backend on Render
        ↓
Load Data / Offer Records / Dashboard
```

| Tool                   | Purpose                    | Endpoint              |
| ---------------------- | -------------------------- | --------------------- |
| `verify_carrier`       | Verifies carrier MC number | `GET /carrier/verify` |
| `find_available_loads` | Searches available loads   | `GET /loads/search`   |
| `negotiate_rate`       | Evaluates counteroffers    | `POST /negotiate`     |
| `submit_offer`         | Saves final call outcome   | `POST /offers`        |

---

## Demo Load

```text
Load ID: L1001
Origin: Dallas, TX
Destination: Phoenix, AZ
Pickup: 2026-06-05 09:00
Delivery: 2026-06-07 15:00
Equipment: Dry Van
Listed Rate: $2,100
Weight: 34,000 lbs
Commodity: Consumer goods
Miles: 1,065
Notes: Appointment required at pickup. No-touch freight.
```

---

## API Endpoints

Protected endpoints require the `x-api-key` header.

```bash
curl "https://happyrobot-fde-backend.onrender.com/health"

curl -H "x-api-key: demo-secret-key" "https://happyrobot-fde-backend.onrender.com/carrier/verify?mc_number=123456"

curl -H "x-api-key: demo-secret-key" "https://happyrobot-fde-backend.onrender.com/loads/search?origin=Dallas&destination=Phoenix&equipment_type=Dry%20Van"

curl -X POST -H "x-api-key: demo-secret-key" "https://happyrobot-fde-backend.onrender.com/negotiate?loadboard_rate=2100&carrier_offer=2200&negotiation_round=1"

curl -H "x-api-key: demo-secret-key" "https://happyrobot-fde-backend.onrender.com/metrics"
```

The root URL is not configured as a homepage. Use `/health` to verify the API deployment and `/dashboard` to view reporting.

---

## Dashboard

Dashboard:
https://happyrobot-fde-backend.onrender.com/dashboard

The dashboard shows total calls, accepted loads, acceptance rate, average final offer, average rate delta, accepted counteroffers, positive sentiment count, and recent call records with carrier, load, rate, outcome, and sentiment.

Seeded example outcomes include accepted counteroffers, accepted listed-rate bookings, no-agreement calls, and ineligible carriers.

---

## Local Setup

```bash
git clone https://github.com/MartandKK/happyrobot-fde-challenge
cd happyrobot-fde-challenge/backend
```

Create a `.env` file:

```env
API_KEY=demo-secret-key
FMCSA_API_KEY=<your_fmcsa_api_key>
```

Install dependencies and run locally:

```bash
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/dashboard
```

---

## Docker

Build the image:

```bash
cd backend
docker build -t happyrobot-fde-backend .
```

Run on Windows PowerShell:

```powershell
docker run -p 8000:8000 `
  -e API_KEY=demo-secret-key `
  -e FMCSA_API_KEY=<your_fmcsa_api_key> `
  happyrobot-fde-backend
```

Run on Mac/Linux:

```bash
docker run -p 8000:8000 \
  -e API_KEY=demo-secret-key \
  -e FMCSA_API_KEY=<your_fmcsa_api_key> \
  happyrobot-fde-backend
```

---

## Render Deployment

The backend is deployed on Render as a Docker web service.

```text
Service Type: Web Service
Runtime: Docker
Root Directory: backend
Branch: main
Environment Variables: API_KEY, FMCSA_API_KEY
```

Deployment flow:

```text
Push to GitHub → Render builds Docker image → Render deploys FastAPI app
```

If auto-deploy does not trigger:

```text
Render → happyrobot-fde-backend → Manual Deploy → Deploy latest commit
```

---

## Security

* HTTPS is provided by Render.
* Protected endpoints use API key authentication through the `x-api-key` header.
* Secrets are stored as environment variables.
* `.env` and generated files are excluded from GitHub.

Protected endpoints:

```text
/carrier/verify
/loads/search
/negotiate
/offers
/metrics
```

Public endpoints:

```text
/health
/dashboard
```

---

## FMCSA Verification

The backend supports FMCSA carrier verification through the `FMCSA_API_KEY` environment variable.

For demo reliability, MC number `123456` uses a deterministic fallback carrier profile, `Sample Express LLC`, while keeping the backend FMCSA-ready.

---

## Known Limitations

This is a proof of concept focused on showing the end-to-end workflow.

* Demo uses sample load data.
* MC number `123456` uses a reliable demo carrier profile.
* Load data is stored in JSON instead of a production TMS or loadboard.
* Offer records use local JSON storage and may reset after Render redeploy.
* Transfer to a sales rep is mocked because web call transfer is out of scope.
* A production version would add persistent database storage, live TMS/loadboard integrations, deeper FMCSA validation, user authentication, audit logs, and richer reporting.

---

## Additional Deliverables

* Broker-facing build document: `Acme_Logistics_Build_Description.md`
* Email to Carlos Becker with recruiter in cc
