from pydantic import BaseModel
import datetime

class AppointmentBase(BaseModel):
    user_id: str
    description: str
    date: datetime.date
    start_time: datetime.time
    end_time: datetime.time
    
class AppointmentCreate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    aid: int
    created_at: datetime.datetime