from pydantic import BaseModel, Field,BeforeValidator,ConfigDict,HttpUrl    
from typing import Optional,List,Annotated,Dict
from bson import ObjectId
from datetime import datetime
PyObjectId = Annotated[str, BeforeValidator(str)]

class AppointmentSchemaBase(BaseModel):
    appointment_cancellation_reason_id: Optional[int] = None
    arrived_at: Optional[datetime] = None
    booked_via_api: Optional[bool] = None
    cancelled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    did_not_attend_at: Optional[datetime] = None
    duration: Optional[int] = None
    finish_time: Optional[datetime] = None
    import_id: Optional[str] = None
    in_surgery_at: Optional[datetime] = None
    metadata: Dict = Field(default_factory=dict)
    notes: Optional[str] = None
    patient_id: Optional[int] = None
    patient_image_url: Optional[HttpUrl] = None
    patient_name: Optional[str] = ""
    payment_plan_id: Optional[int] = None
    pending_at: Optional[datetime] = None
    practitioner_id: Optional[int] = None
    reason: Optional[str] = None
    room_id: Optional[int] = None
    start_time: Optional[datetime] = None
    state: Optional[str] = None
    treatment_description: Optional[str] = None
    updated_at: Optional[datetime] = None
    user_id: Optional[int] = None
    practitioner_site_id:Optional[str] = None
    uuid: Optional[str] = None


class AppointmentCreate(AppointmentSchemaBase):
    pass


class Appointment(AppointmentSchemaBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True)

class AppointmentList(BaseModel):
    results: List[Appointment]

