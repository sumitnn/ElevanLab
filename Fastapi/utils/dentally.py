import os
import json
from bson import json_util
import requests
from typing import Optional
from dotenv import load_dotenv
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import APIRouter, Depends
from db.config import get_db
load_dotenv()


Dentally_api_key = os.getenv("DENTALLY_API_KEY")  

DENTALLY_BASE_URL = os.getenv("DENTALLY_BASE_URL")


HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {Dentally_api_key}"
}


async def create_patient_and_store(patient_data: dict, db) -> dict:


    url = f"{DENTALLY_BASE_URL}/patients"
    try:
        data=json.dumps(patient_data)
        response = requests.post(url, data=data, headers=HEADERS)
        response.raise_for_status()
        print(response.content)
        api_response = response.json()
        patient = api_response.get("patient")
        if not patient:
            print("❌ API response does not contain 'patient' key.")
            return False
        
        # Save to MongoDB with external ID from API
        await db["patients"].insert_one(patient)

        print("✅ Patient created and stored in MongoDB.")
        return patient
    except requests.RequestException as e:
        print("❌ Failed to create patient:", e)
        return False


async def create_appointment_and_store(appointment_data: dict, db) -> dict:


    url = f"{DENTALLY_BASE_URL}/appointments"
    data=json.dumps(appointment_data)
    try:
        response = requests.post(url, data=data, headers=HEADERS)
        response.raise_for_status()
        print(response.content)
        api_response = response.json()

        appointment = api_response.get("appointment")
        if not appointment:
            print("❌ API response does not contain 'appointment' key.")
            return False
 
        await db["appointments"].insert_one(appointment)

        print("✅ Appointment created and stored in MongoDB.")
        return True
    except requests.RequestException as e:
        print("❌ Failed to create appointment:", e)
        return False