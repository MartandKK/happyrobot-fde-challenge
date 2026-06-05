# Inbound Carrier Sales Automation POC for Acme Logistics

## 1. Executive Summary

This proof of concept automates the first layer of inbound carrier sales calls for Acme Logistics using a HappyRobot voice agent connected to a custom FastAPI backend.

The agent can receive a carrier call, collect the MC number, verify eligibility, search available loads, pitch load details, handle rate negotiation, mock a transfer to a sales rep, and save the final offer outcome for reporting.

The goal is to reduce repetitive carrier-sales work while giving Acme’s team visibility into accepted loads, negotiated rates, call outcomes, and carrier sentiment.

---

## 2. Business Problem

Inbound carrier calls often follow a repetitive workflow. A sales rep needs to collect the carrier’s MC number, verify whether the carrier can work with the brokerage, search for available loads, explain load details, negotiate pricing, and record the final outcome.

This process is time-sensitive and operationally repetitive. Automating the first layer of these calls can help reps focus on higher-value exceptions, complex negotiations, and customer-facing work.

---

## 3. Proposed Solution

The proposed solution is an inbound HappyRobot voice workflow connected to a deployed backend API.

The workflow uses four main tools:

| Tool                   | Purpose                                             |
| ---------------------- | --------------------------------------------------- |
| `verify_carrier`       | Verifies the carrier by MC number                   |
| `find_available_loads` | Searches available loads by lane and equipment type |
| `negotiate_rate`       | Evaluates carrier counteroffers                     |
| `submit_offer`         | Saves the final call result for reporting           |

The backend is built with FastAPI, deployed on Render, protected with API key authentication, and containerized with Docker.

---

## 4. Demo Workflow

The main demo flow is:

1. The carrier provides MC number `123456`.
2. The agent verifies the carrier as `Sample Express LLC`.
3. The carrier asks for a dry van load from Dallas to Phoenix.
4. The agent finds load `L1001` and pitches the lane, pickup time, delivery time, equipment, weight, miles, and listed rate.
5. The carrier asks for `$2,200`.
6. The negotiation endpoint accepts the counteroffer.
7. The agent confirms the price, mocks the transfer, and saves the final offer outcome.
8. The dashboard updates with the completed call record.

Expected result:

Carrier: Sample Express LLC
Load: L1001
Lane: Dallas, TX → Phoenix, AZ
Listed Rate: $2,100
Final Offer: $2,200
Outcome: accepted_counteroffer
Sentiment: positive

---

## 5. Carrier Verification

Carrier verification is handled through the backend endpoint:

GET /carrier/verify

The endpoint accepts an MC number and returns structured carrier details, including carrier name, eligibility, authority status, insurance status, and safety rating.

The backend is configured with an FMCSA API key through environment variables. For demo reliability, MC number `123456` uses a stable fallback profile:

Carrier: Sample Express LLC
MC Number: 123456
Authority Status: ACTIVE
Insurance Status: VALID
Safety Rating: SATISFACTORY
Eligible: true

This keeps the walkthrough predictable while preserving an FMCSA-ready verification path.

---

## 6. Load Search and Pricing

Load search is handled through:

GET /loads/search

The main demo load is:

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

Negotiation is handled through:

POST /negotiate

For the proof of concept, the pricing logic accepts carrier offers up to 105% of the listed rate. For load L1001:

Listed Rate: $2,100
Auto-Accept Limit: $2,205
Carrier Counteroffer: $2,200
Decision: accept

The agent then responds:

I can make $2,200 work for this load. Transfer was successful and now you can wrap up the conversation.

---

## 7. Offer Capture and Classification

At the end of the call, the workflow saves the final result through:

POST /offers

The saved record includes the carrier, load, listed rate, carrier offer, final offer, negotiation rounds, outcome, sentiment, and timestamp.

The workflow classifies outcomes such as:

accepted_listed_rate
accepted_counteroffer
ineligible_carrier
no_matching_load
carrier_not_interested
no_agreement_price
call_incomplete

Sentiment is classified as:

positive
neutral
negative

For the main demo path:

Outcome: accepted_counteroffer
Sentiment: positive

---

## 8. Dashboard and Metrics

A custom dashboard was built outside HappyRobot analytics.

Dashboard:

https://happyrobot-fde-backend.onrender.com/dashboard

The dashboard shows:

* Total calls
* Accepted loads
* Acceptance rate
* Average final offer
* Average rate delta
* Accepted counteroffers
* Positive sentiment count
* Recent carrier call records

The recent call table includes MC number, carrier name, load ID, listed rate, final offer, outcome, and sentiment.

This gives Acme Logistics a quick operational view of whether inbound calls are converting, how much pricing changes during negotiation, and how carriers are responding.

---

## 9. Deployment and Security

The backend is deployed on Render as a Docker web service.

Security and infrastructure details:

* HTTPS provided through Render
* API key authentication through the `x-api-key` header
* FMCSA API key stored as an environment variable
* `.env` excluded from GitHub
* Dockerfile included for reproducible deployment
* README includes local setup, Docker commands, and Render deployment notes

Key environment variables:

API_KEY
FMCSA_API_KEY

---

## 10. Current Limitations

This is a proof of concept, so the focus is on demonstrating the full workflow rather than building a production-scale freight system.

Current limitations:

* The demo uses a small set of sample loads.
* MC number `123456` is included as a stable demo carrier profile.
* Load data is stored in JSON rather than a production TMS or loadboard.
* Offer records are stored in local JSON and may reset after Render redeploy.
* The dashboard is intentionally lightweight.
* The sales rep transfer is mocked because live transfer is out of scope for the web call demo.

---

## 11. Recommended Production Next Steps

For a production rollout, I would recommend:

1. Connect carrier verification directly to Acme’s compliance and onboarding systems.
2. Replace JSON load data with a TMS or live loadboard integration.
3. Store call and offer records in a persistent database.
4. Add authentication and role-based access for dashboard users.
5. Add call recording links and transcripts to saved offer records.
6. Expand negotiation rules by lane, customer, equipment type, margin, and market conditions.
7. Add structured rep handoff payloads.
8. Add monitoring, alerting, and audit logs.

---

## 12. Summary

This proof of concept demonstrates how Acme Logistics could automate the first layer of inbound carrier sales calls.

The system verifies carriers, searches loads, pitches load details, handles controlled negotiation, mocks transfer, saves offer outcomes, and reports metrics through a custom dashboard.

It is designed to show both the customer-facing workflow and the technical foundation needed for a production-ready carrier sales automation system.
