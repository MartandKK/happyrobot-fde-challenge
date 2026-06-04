# HappyRobot FDE Technical Challenge - Inbound Carrier Sales

## Overview

This project is a proof of concept for inbound carrier load sales automation. It supports an AI voice agent that can verify carriers, search available loads, negotiate pricing, and save call outcomes.

## Objective 1 Features

- Carrier MC number verification
- Load search by origin, destination, and equipment type
- Load pitching support
- Negotiation logic with approval thresholds
- Offer/call data capture
- Outcome classification
- Sentiment classification

## Backend API

The backend is built with FastAPI.

### Endpoints

GET /health

GET /carrier/verify?mc_number=123456

GET /loads/search?origin=Dallas&equipment_type=Dry%20Van

POST /negotiate?loadboard_rate=2100&carrier_offer=2200&negotiation_round=1

POST /offers

## Security

All main API endpoints require an API key header:

x-api-key: demo-secret-key

## Run Locally

Go into the backend folder:

```powershell
cd backend