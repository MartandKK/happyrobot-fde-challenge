# HappyRobot FDE Technical Challenge - Inbound Carrier Sales

## Overview

This project is a proof of concept for automating inbound carrier sales calls for a freight brokerage.

A carrier calls in through a HappyRobot web call, provides their MC number, gets verified, searches for an available load, hears the load details, negotiates pricing, and has the final offer outcome saved to a custom dashboard.

The solution includes:

* HappyRobot inbound voice workflow
* FastAPI backend
* Carrier verification endpoint with FMCSA-ready logic
* Load search API
* Negotiation API
* Offer saving API
* Custom dashboard outside HappyRobot analytics
* Dockerized deployment on Render

---

## Live Links

Health Check:
https://happyrobot-fde-backend.onrender.com/health

Dashboard:
https://happyrobot-fde-backend.onrender.com/dashboard

GitHub Repository:
<PASTE_GITHUB_REPO_LINK_HERE>

HappyRobot Workflow:
<PASTE_HAPPYROBOT_WORKFLOW_LINK_HERE>
Note: This link may require HappyRobot workspace access.

Demo Video:
<PASTE_DEMO_VIDEO_LINK_HERE>

---

## Demo Script

Use this script for the main demo path:

```text
Carrier: My MC number is 123456.

Carrier: I’m looking for a dry van load from Dallas to Phoenix.

Carrier: Yes, but can you do $2,200?
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
verify_carrier
↓
find_available_loads
↓
negotiate_rate
↓
submit_offer
```

---

## Architecture

```text
HappyRobot Web Call
        ↓
Inbound Voice Agent
        ↓
FastAPI Backend
        ↓
Load Data / Offer Records / Dashboard
```

### HappyRobot Tools

| Tool                   | Purpose                    | Backend Endpoint      |
| ---------------------- | -------------------------- | --------------------- |
| `verify_carrier`       | Verifies carrier MC number | `GET /carrier/verify` |
| `find_available_loads` | Searches available loads   | `GET /loads/search`   |
| `negotiate_rate`       | Evaluates counteroffers    | `POST /negotiate`     |
| `submit_offer`         | Saves final call outcome   | `POST /offers`        |

---

## Main Demo Load

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

### Health Check

```bash
curl "https://happyrobot-fde-backend.onrender.com/health"
```

### Carrier Verification

```bash
curl -H "x-api-key: demo-secret-key" "https://happyrobot-fde-backend.onrender.com/carrier/verify?mc_number=123456"
```

### Load Search

```bash
curl -H "x-api-key: demo-secret-key" "https://happyrobot-fde-backend.onrender.com/loads/search?origin=Dallas&destination=Phoenix&equipment_type=Dry%20Van"
```

### Negotiation

```bash
curl -X POST -H "x-api-key: demo-secret-key" "https://happyrobot-fde-backend.onrender.com/negotiate?loadboard_rate=2100&carrier_offer=2200&negotiation_round=1"
```

### Metrics

```bash
curl -H "x-api-key: demo-secret-key" "https://happyrobot-fde-backend.onrender.com/metrics"
```

---

## Dashboard

Dashboard link:

```text
https://happyrobot-fde-backend.onrender.com/dashboard
```

The dashboard shows:

* Total calls
* Accepted loads
* Acceptance rate
* Recent carrier calls
* MC number
* Carrier name
* Load ID
* Listed rate
* Final offer
* Outcome
* Sentiment

---

## Local Setup

Clone the repository:

```bash
git clone <PASTE_GITHUB_REPO_LINK_HERE>
cd happyrobot-fde-challenge/backend
```

Create a `.env` file:

```env
API_KEY=demo-secret-key
FMCSA_API_KEY=<your_fmcsa_api_key>
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run locally:

```bash
python -m uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/dashboard
```

---

## Docker Commands

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

## Render Deployment Notes

The backend is deployed on Render as a Docker web service.

Render configuration:

```text
Service Type: Web Service
Runtime: Docker
Root Directory: backend
Branch: main
```

Environment variables configured in Render:

```env
API_KEY=demo-secret-key
FMCSA_API_KEY=<configured in Render>
```

Deployment process:

```text
Push to GitHub → Render builds Docker image → Render deploys FastAPI app
```

If auto-deploy does not trigger:

```text
Render → happyrobot-fde-backend → Manual Deploy → Deploy latest commit
```

---

## Security

The backend uses API key authentication through the `x-api-key` header.

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

Secrets are stored in environment variables and are not committed to GitHub.

---

## FMCSA Verification

The backend supports FMCSA carrier verification through:

```text
FMCSA_API_KEY
```

For demo reliability, MC number `123456` uses a deterministic fallback carrier profile:

```text
Sample Express LLC
```

This keeps the walkthrough stable while still keeping the backend FMCSA-ready.

---

## Known Limitations

This project is a proof of concept, so the focus is on showing the full inbound carrier sales workflow end-to-end rather than building a production-scale freight system.

* The demo uses a small set of sample loads so the walkthrough is predictable and easy to test.
* MC number `123456` is included as a reliable demo carrier profile. The backend also supports an FMCSA API key for live carrier verification.
* The load data is stored in a local JSON file. In a production version, this would connect to a TMS, loadboard, or internal brokerage database.
* Offer records are currently saved to a local `offers.json` file. On Render, this data may reset after a redeploy. A production version would use a persistent database.
* The dashboard is intentionally lightweight. It is meant to show the key use case metrics without relying on HappyRobot platform analytics.
* The sales rep transfer is mocked with the message “Transfer was successful and now you can wrap up the conversation,” because live transfer is out of scope for the web call demo.
* The main demo path is optimized around load `L1001`, listed at `$2,100`, with a `$2,200` accepted counteroffer.
* A production version would add stronger database storage, live loadboard/TMS integrations, deeper FMCSA validation, user authentication, audit logs, and more detailed reporting.

---

## Submission Checklist

* Health check link
* Dashboard link
* GitHub repository link
* HappyRobot workflow link
* Demo video link
* Broker-facing build document
* Email to Carlos Becker with recruiter in cc
