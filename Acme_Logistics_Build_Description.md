# Inbound Carrier Sales Automation POC for Acme Logistics

## 1. Executive Summary

This proof of concept automates inbound carrier sales calls for Acme Logistics using a HappyRobot voice agent connected to a custom FastAPI backend.

The system allows a carrier to call in, provide an MC number, get verified, search for an available load, hear load details, negotiate the rate, and have the final outcome saved for reporting.

The goal is to reduce repetitive inbound carrier-sales work while giving Acme’s team visibility into call outcomes, negotiated rates, and carrier sentiment.

---

## 2. Business Problem

Freight brokers receive frequent inbound calls from carriers asking about available loads. These calls often require the same manual steps:

* Collect the carrier’s MC number
* Verify carrier eligibility
* Search for available loads
* Pitch lane, pickup, delivery, equipment, and rate details
* Handle rate negotiation
* Transfer accepted loads to a sales rep
* Record the offer outcome
* Track call performance and carrier sentiment

This process is repetitive and time-sensitive. Automating the first layer of inbound carrier calls can help sales reps focus on higher-value conversations and exceptions.

---

## 3. Proposed Solution

The solution is an inbound voice agent built in HappyRobot and connected to a deployed backend API.

The agent can:

1. Answer inbound carrier calls through the HappyRobot web call trigger.
2. Ask for the carrier’s MC number.
3. Verify carrier eligibility through a backend carrier verification endpoint.
4. Search available loads by lane and equipment type.
5. Pitch the best matching load.
6. Ask whether the carrier is interested.
7. Evaluate a counteroffer using pricing rules.
8. Mock-transfer the call when a price is agreed.
9. Save the final offer details.
10. Classify the outcome and sentiment.
11. Display saved activity in a custom dashboard.

---

## 4. Demo Workflow

The primary demo flow is:

```text
Carrier provides MC number: 123456
↓
Agent verifies carrier as Sample Express LLC
↓
Carrier asks for dry van load from Dallas to Phoenix
↓
Agent finds load L1001
↓
Agent pitches pickup, delivery, equipment, commodity, weight, miles, and rate
↓
Carrier asks for $2,200
↓
Negotiation endpoint accepts the counteroffer
↓
Agent mocks transfer to sales rep
↓
Offer outcome is saved
↓
Dashboard updates
```

---

## 5. Carrier Verification

The backend includes a carrier verification endpoint:

```text
GET /carrier/verify
```

The endpoint accepts an MC number and returns:

* MC number
* Carrier name
* Eligibility status
* Authority status
* Insurance status
* Safety rating

The backend is configured with an FMCSA API key through environment variables. For demo reliability, MC number `123456` uses a deterministic fallback carrier profile:

```text
Carrier: Sample Express LLC
MC Number: 123456
Authority Status: ACTIVE
Insurance Status: VALID
Safety Rating: SATISFACTORY
Eligible: true
```

This keeps the demo stable while preserving an FMCSA-ready verification path.

---

## 6. Load Search

The backend includes a load search endpoint:

```text
GET /loads/search
```

The demo load data is stored in a JSON file and includes the required load fields:

* load_id
* origin
* destination
* pickup_datetime
* delivery_datetime
* equipment_type
* loadboard_rate
* notes
* weight
* commodity_type
* num_of_pieces
* miles
* dimensions

Primary demo load:

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

## 7. Negotiation Logic

The backend includes a negotiation endpoint:

```text
POST /negotiate
```

The pricing logic is intentionally simple for the proof of concept:

* The system accepts carrier offers up to 105% of the listed loadboard rate.
* If the carrier asks above the approval limit, the system returns a counteroffer.
* If no agreement is reached after 3 rounds, the call is classified as `no_agreement_price`.

For the demo load:

```text
Listed Rate: $2,100
Auto-Accept Limit: $2,205
Carrier Counteroffer: $2,200
Decision: accept
```

The agent then says:

```text
I can make $2,200 work for this load. Transfer was successful and now you can wrap up the conversation.
```

---

## 8. Offer Capture

The final call result is saved through:

```text
POST /offers
```

Saved fields include:

* call_id
* mc_number
* carrier_name
* load_id
* loadboard_rate
* carrier_offer
* final_offer
* negotiation_rounds
* outcome
* sentiment
* created_at

Example saved result:

```text
Call ID: CALL-001
MC Number: 123456
Carrier: Sample Express LLC
Load ID: L1001
Listed Rate: $2,100
Carrier Offer: $2,200
Final Offer: $2,200
Outcome: accepted_counteroffer
Sentiment: positive
```

---

## 9. Outcome and Sentiment Classification

The workflow classifies call outcomes using clear labels:

```text
accepted_listed_rate
accepted_counteroffer
ineligible_carrier
no_matching_load
carrier_not_interested
no_agreement_price
call_incomplete
```

Sentiment is classified as:

```text
positive
neutral
negative
```

For the main demo flow, the expected result is:

```text
Outcome: accepted_counteroffer
Sentiment: positive
```

---

## 10. Dashboard and Metrics

A custom dashboard was built outside HappyRobot analytics.

Dashboard link:

```text
https://happyrobot-fde-backend.onrender.com/dashboard
```

The dashboard displays:

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

This gives Acme Logistics visibility into the operational performance of the inbound carrier sales workflow.

---

## 11. Deployment and Security

The backend is built with FastAPI and deployed on Render as a Docker web service.

Security measures include:

* API key authentication through the `x-api-key` header
* Environment variables for secrets
* FMCSA API key stored outside the codebase
* Dockerized backend deployment
* HTTPS through Render’s hosted service

Key environment variables:

```text
API_KEY
FMCSA_API_KEY
```

The solution includes a `Dockerfile`, `requirements.txt`, and README instructions for local setup and deployment.

---

## 12. Known Limitations

This is a proof of concept, so the goal is to demonstrate the complete workflow rather than build a full production freight system.

Current limitations:

* The demo uses a small set of sample loads.
* MC number `123456` is included as a stable demo carrier profile.
* Load data is stored in a JSON file rather than a production TMS or loadboard.
* Offer records are saved to a local JSON file, which may reset on Render after redeploy.
* The dashboard is intentionally lightweight.
* The sales rep transfer is mocked because web call transfer is out of scope.
* The main demo path is optimized around load `L1001`.
* A production version would use persistent database storage, live TMS/loadboard integrations, deeper FMCSA validation, authentication, audit logs, and richer reporting.

---

## 13. Recommended Production Next Steps

For a production rollout, I would recommend:

1. Connect carrier verification directly to Acme’s compliance and onboarding systems.
2. Replace JSON load data with Acme’s TMS or loadboard integration.
3. Store offers and calls in a persistent database.
4. Add authentication and role-based access for dashboard users.
5. Add call recording links and transcripts to saved offer records.
6. Expand negotiation rules by lane, customer, equipment type, margin, and market conditions.
7. Add rep handoff payloads so sales reps receive structured call summaries.
8. Add monitoring, alerting, and audit logs.

---

## 14. Summary

This proof of concept demonstrates how Acme Logistics could automate the first layer of inbound carrier sales calls.

The system verifies carriers, searches loads, pitches details, handles a controlled negotiation, saves the final offer, and reports use case metrics through a custom dashboard.

It is designed to show both the customer-facing workflow and the technical foundation needed for a more production-ready carrier sales automation system.
