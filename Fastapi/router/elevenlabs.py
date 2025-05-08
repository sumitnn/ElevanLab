from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request, Header
from dotenv import load_dotenv
import os
import json
from utils.websockets import stop_websocket
from fastapi import HTTPException, status
from db.config import get_db
from utils.chatgpt import OpenAiModel
from fastapi.responses import JSONResponse
from utils.elevanlab import verify_elevanlab_webhook_signature
from utils.chatgpt import OpenAiModel
from utils.dentally import create_patient_and_store, create_appointment_and_store
from datetime import datetime, timedelta,timezone
from pymongo import ASCENDING
from dateutil import parser as date_parser
import requests
from typing import List
from router.dentally import get_availability_from_dentally

load_dotenv()
elevanlab_router = APIRouter()


ELEVENLABS_AGENT_ID = os.getenv("ELEVENLABS_AGENT_ID")

@elevanlab_router.get("/practitioners", status_code=status.HTTP_200_OK)
async def get_practitioners(db=Depends(get_db)):
    cursor = db["practitioners"].find({"active": True})
    practitioners_raw = await cursor.to_list(length=15)  # limit to avoid overload

    lines = []
    for doc in practitioners_raw:
        user = doc.get("user", {})
        full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
        practitioner_id = doc.get("id")
        if full_name and practitioner_id:
            lines.append(f"{full_name} ({practitioner_id})")

    if not lines:
        return {"text": "Sorry, no active practitioners are currently available."}

    spoken_text = (
        "Here are the available practitioners: " +
        "; ".join(lines) 
       
    )

    return {"text": spoken_text}



@elevanlab_router.get("/check-available-time/{practitioner_id}/{start_time}/{finish_time}/{duration}", status_code=status.HTTP_200_OK)
async def check_available_time(practitioner_id: int, start_time: str, finish_time: str,duration:int, db=Depends(get_db)):
    print("Start time:", start_time)
    print("Finish time:", finish_time)
    print("Duration:", duration)
    try:
        # Call Dentally API to check availability
        availability_data = get_availability_from_dentally([practitioner_id], start_time, finish_time,duration)

        if not availability_data.get("availability"):
            return {
                "available_slots": "",
                "message": "You can book an appointment with this practitioner at any time slot.You Want"
            }

        # Extract only start_times and convert to a comma-separated string
        slot_times = [
            f"{slot['start_time']} to  {slot['finish_time']}"
            for slot in availability_data.get("availability", [])
        ]
        slot_string = ",".join(slot_times)

        return {
            "available_slots": slot_string,
            "message": "Available time slots are"
        }

    except Exception as e:
        return {
            "available_slots": "",
            "message": f"Something Went Wrong in Backend",
        }

@elevanlab_router.post("/create-appointment",status_code=status.HTTP_200_OK)
async def webhook_listener(request: Request, elevenlabs_signature: str = Header(None)):

    body = await request.body()

    if not verify_elevanlab_webhook_signature(body, elevenlabs_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    event = json.loads(body)
    db = await get_db()
    try:
        if event.get("type") == "post_call_transcription":
            data = event["data"]
            if data["agent_id"] == ELEVENLABS_AGENT_ID:
                transcipt_data=data["transcript"]
                response=await OpenAiModel(transcipt_data)
                print("Response from OpenAI:", response)
                if response:
                    pateint_data = {
                        "patient": {
                            "title": response.get('patient_title',"Mr"),
                            "first_name": response.get('patient_first_name'),
                            "last_name": response.get('patient_last_name'," "),
                            "date_of_birth": response.get('pateint_dob'),
                            "gender": response.get('pateint_gender',True), 
                            "ethnicity": response.get('patient_ethnicity'),
                            "address_line_1": response.get('patient_address_line_1'," "),
                            "postcode": response.get('pateint_postcode'," "),
                            "payment_plan_id": int(response.get('patient_payment_plan_id')),
                            "payment_plan": [int(response.get('patient_payment_plan_id'))],
                            "email_address": response.get('patient_email'),
                        }
                    }
                    appintment_data={
                        "appointment": {
                            "start_time": response.get('appointment_start_time'),
                            "finish_time": response.get('appointment_finish_time'),
                            "patient_id": response.get('appointment_patient_id'),
                            "practitioner_id": response.get('booked_practitioner_id'),
                            "reason": response.get('appointment_reason')
                        }
                    }
                    print("Formatted Data:", pateint_data)


                    created_patient = await create_patient_and_store(patient_data=pateint_data,db=db)
                    if created_patient and "id" in created_patient:
                        # Replace patient_id in appointment if needed
                        appintment_data["appointment"]["patient_id"] = created_patient["id"]
                        created=await create_appointment_and_store(appointment_data=appintment_data,db=db)
                        if created:
                            print("Appointment created successfully.")
                        else:
                            print("Failed to create appointment.")
            

        return {"received": True}
    except Exception as e:
        print("Error processing event:", e)
        return {"received": True}



