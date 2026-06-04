import json
import os
import requests
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="HappyRobot Inbound Carrier Sales API")

API_KEY = os.getenv("API_KEY", "demo-secret-key")


def check_api_key(x_api_key: Optional[str]):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


def load_loads():
    with open("loads.json", "r") as file:
        return json.load(file)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/carrier/verify")
def verify_carrier(mc_number: str, x_api_key: Optional[str] = Header(None)):
    check_api_key(x_api_key)

    # Normalize spoken/transcribed MC numbers like "12 3456", "123,456", or "MC 123456"
    mc_number = "".join(char for char in mc_number if char.isdigit())

    # Mock demo carriers first for reliable demo
    # This keeps your HappyRobot demo stable while still supporting live FMCSA lookup below.
    mock_carriers = {
        "123456": {
            "mc_number": "123456",
            "carrier_name": "Sample Express LLC",
            "eligible": True,
            "authority_status": "ACTIVE",
            "insurance_status": "VALID",
            "safety_rating": "SATISFACTORY"
        },
        "999999": {
            "mc_number": "999999",
            "carrier_name": "Risky Carrier Inc",
            "eligible": False,
            "authority_status": "INACTIVE",
            "insurance_status": "EXPIRED",
            "safety_rating": "UNSATISFACTORY"
        }
    }

    if mc_number in mock_carriers:
        return mock_carriers[mc_number]

    fmcsa_api_key = os.getenv("FMCSA_API_KEY")

    # Try live FMCSA lookup for all other MC numbers
    if fmcsa_api_key:
        try:
            url = f"https://mobile.fmcsa.dot.gov/qc/services/carriers/docket-number/{mc_number}"

            response = requests.get(
                url,
                params={"webKey": fmcsa_api_key},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                carrier_data = data.get("content", data)

                if isinstance(carrier_data, list) and carrier_data:
                    carrier_data = carrier_data[0]

                if isinstance(carrier_data, dict) and carrier_data:
                    carrier_name = (
                        carrier_data.get("legalName")
                        or carrier_data.get("dbaName")
                    )

                    fmcsa_mc_number = carrier_data.get("mcNumber")
                    allow_to_operate = carrier_data.get("allowToOperate")
                    out_of_service = carrier_data.get("outOfService")

                    # Only trust FMCSA if it gives real carrier data
                    if carrier_name or fmcsa_mc_number or allow_to_operate:
                        eligible = allow_to_operate == "Y" and out_of_service != "Y"

                        return {
                            "mc_number": str(fmcsa_mc_number or mc_number),
                            "carrier_name": carrier_name or "Unknown Carrier",
                            "eligible": eligible,
                            "authority_status": "ACTIVE" if allow_to_operate == "Y" else "INACTIVE",
                            "insurance_status": "UNKNOWN",
                            "safety_rating": carrier_data.get("safetyRating") or "UNKNOWN"
                        }

        except Exception:
            # If FMCSA fails, return standard not-found response below
            pass

    return {
        "mc_number": mc_number,
        "carrier_name": "Unknown Carrier",
        "eligible": False,
        "authority_status": "NOT_FOUND",
        "insurance_status": "UNKNOWN",
        "safety_rating": "UNKNOWN"
    }


@app.get("/loads/search")
def search_loads(
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    equipment_type: Optional[str] = None,
    x_api_key: Optional[str] = Header(None)
):
    check_api_key(x_api_key)

    loads = load_loads()
    matches = []

    for load in loads:
        origin_match = True
        destination_match = True
        equipment_match = True

        if origin:
            origin_match = origin.lower() in load["origin"].lower()

        if destination:
            destination_match = destination.lower() in load["destination"].lower()

        if equipment_type:
            equipment_match = equipment_type.lower() in load["equipment_type"].lower()

        if origin_match and destination_match and equipment_match:
            matches.append(load)

    return {
        "count": len(matches),
        "matches": matches
    }


class OfferRequest(BaseModel):
    call_id: Optional[str] = None
    mc_number: str
    carrier_name: Optional[str] = None
    load_id: str
    loadboard_rate: float
    carrier_offer: Optional[float] = None
    final_offer: Optional[float] = None
    negotiation_rounds: int = 0
    outcome: str
    sentiment: str


@app.post("/offers")
def submit_offer(offer: OfferRequest, x_api_key: Optional[str] = Header(None)):
    check_api_key(x_api_key)

    record = offer.dict()
    record["created_at"] = datetime.utcnow().isoformat()

    try:
        with open("offers.json", "r") as file:
            offers = json.load(file)
    except FileNotFoundError:
        offers = []

    offers.append(record)

    with open("offers.json", "w") as file:
        json.dump(offers, file, indent=2)

    return {
        "status": "saved",
        "offer": record
    }


@app.post("/negotiate")
def negotiate(
    loadboard_rate: float,
    carrier_offer: float,
    negotiation_round: int,
    x_api_key: Optional[str] = Header(None)
):
    check_api_key(x_api_key)

    max_auto_accept = loadboard_rate * 1.05
    first_counter = loadboard_rate * 1.03
    final_counter = loadboard_rate * 1.05

    if carrier_offer <= max_auto_accept:
        return {
            "decision": "accept",
            "final_offer": carrier_offer,
            "message": f"I can make ${carrier_offer:,.0f} work for this load."
        }

    if negotiation_round >= 3:
        return {
            "decision": "reject",
            "final_offer": None,
            "message": "It sounds like we may be too far apart on price today. I’ll note your offer and have the team follow up if anything changes."
        }

    if negotiation_round == 1:
        counter = first_counter
    else:
        counter = final_counter

    return {
        "decision": "counter",
        "final_offer": counter,
        "message": f"I’m not able to get to ${carrier_offer:,.0f}. The best I can do right now is ${counter:,.0f}. Would that work?"
    }

@app.get("/metrics")
def get_metrics(x_api_key: Optional[str] = Header(None)):
    check_api_key(x_api_key)

    try:
        with open("offers.json", "r") as file:
            offers = json.load(file)
    except FileNotFoundError:
        offers = []

    total_calls = len(offers)
    accepted_counteroffers = sum(1 for o in offers if o.get("outcome") == "accepted_counteroffer")
    accepted_listed_rate = sum(1 for o in offers if o.get("outcome") == "accepted_listed_rate")
    no_agreement = sum(1 for o in offers if o.get("outcome") == "no_agreement_price")

    final_offers = [
        o.get("final_offer") for o in offers
        if isinstance(o.get("final_offer"), (int, float))
    ]

    average_final_offer = sum(final_offers) / len(final_offers) if final_offers else 0

    sentiment_counts = {}
    for offer in offers:
        sentiment = offer.get("sentiment", "unknown")
        sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1

    return {
        "total_calls": total_calls,
        "accepted_counteroffers": accepted_counteroffers,
        "accepted_listed_rate": accepted_listed_rate,
        "no_agreement": no_agreement,
        "average_final_offer": average_final_offer,
        "sentiment_counts": sentiment_counts,
        "recent_offers": offers[-10:]
    }


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    try:
        with open("offers.json", "r") as file:
            offers = json.load(file)
    except FileNotFoundError:
        offers = []

    total_calls = len(offers)
    accepted = sum(
        1 for o in offers
        if o.get("outcome") in ["accepted_counteroffer", "accepted_listed_rate"]
    )

    acceptance_rate = round((accepted / total_calls) * 100, 1) if total_calls else 0

    rows = ""
    for offer in offers[-10:]:
        rows += f"""
        <tr>
            <td>{offer.get("call_id", "")}</td>
            <td>{offer.get("mc_number", "")}</td>
            <td>{offer.get("carrier_name", "")}</td>
            <td>{offer.get("load_id", "")}</td>
            <td>${offer.get("loadboard_rate", "")}</td>
            <td>${offer.get("final_offer", "")}</td>
            <td>{offer.get("outcome", "")}</td>
            <td>{offer.get("sentiment", "")}</td>
        </tr>
        """

    return f"""
    <html>
    <head>
        <title>Inbound Carrier Sales Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .cards {{ display: flex; gap: 20px; margin-bottom: 30px; }}
            .card {{ border: 1px solid #ddd; border-radius: 8px; padding: 20px; width: 220px; }}
            .metric {{ font-size: 28px; font-weight: bold; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            th {{ background-color: #f4f4f4; }}
        </style>
    </head>
    <body>
        <h1>Inbound Carrier Sales Dashboard</h1>

        <div class="cards">
            <div class="card">
                <div>Total Calls</div>
                <div class="metric">{total_calls}</div>
            </div>
            <div class="card">
                <div>Accepted Loads</div>
                <div class="metric">{accepted}</div>
            </div>
            <div class="card">
                <div>Acceptance Rate</div>
                <div class="metric">{acceptance_rate}%</div>
            </div>
        </div>

        <h2>Recent Carrier Calls</h2>
        <table>
            <tr>
                <th>Call ID</th>
                <th>MC Number</th>
                <th>Carrier</th>
                <th>Load ID</th>
                <th>Listed Rate</th>
                <th>Final Offer</th>
                <th>Outcome</th>
                <th>Sentiment</th>
            </tr>
            {rows}
        </table>
    </body>
    </html>
    """