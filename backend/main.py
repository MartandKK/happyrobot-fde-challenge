import json
import os
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
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

    mc_number = "".join(char for char in mc_number if char.isdigit())

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

    carrier = mock_carriers.get(mc_number)

    if not carrier:
        return {
            "mc_number": mc_number,
            "carrier_name": "Unknown Carrier",
            "eligible": False,
            "authority_status": "NOT_FOUND",
            "insurance_status": "UNKNOWN",
            "safety_rating": "UNKNOWN"
        }

    return carrier


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