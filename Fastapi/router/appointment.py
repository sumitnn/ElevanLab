from fastapi import APIRouter, HTTPException, status, Depends
from schema.appointment import Appointment, AppointmentCreate, AppointmentList
from db.config import get_db
from bson import ObjectId

appointment_router = APIRouter()


@appointment_router.get("/appointmentss", response_model=AppointmentList, response_model_by_alias=False)
async def list_appointments(db=Depends(get_db)):
    cursor = db["appointments"].find()
    appointments_raw = await cursor.to_list(length=100)
    appointments = [Appointment(**doc) for doc in appointments_raw]
    return {"results": appointments}


@appointment_router.get("/appointments/{id}", response_model=Appointment,response_model_by_alias=False)
async def get_appointment(id: str, db=Depends(get_db)):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ObjectId")
    appointment = await db["appointments"].find_one({"_id": ObjectId(id)})
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return Appointment(**appointment)








