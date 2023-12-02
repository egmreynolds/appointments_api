from pydantic import BaseModel, condate, validator, ValidationError, field_validator, ValidationInfo
import datetime

GLOBAL_START_HOUR = 8
GLOBAL_END_HOUR = 17
GLOBAL_APPOINTMENT_LENGTH = 15 #minutes

class AppointmentBase(BaseModel):
    user_id: str
    description: str
    date: datetime.date
    start_time: datetime.time
    end_time: datetime.time
    
    @field_validator("date")
    def validate_date(cls, value) -> datetime.date:
        if value < datetime.date.today():
            raise ValueError("Date must be today or a future date")
        return value
    
    @field_validator("start_time")
    def validate_start_time(cls, value) -> datetime.time:
        opening_time = datetime.time(GLOBAL_START_HOUR, 00)
        closing_time = datetime.time(GLOBAL_END_HOUR, 00)

        if not (opening_time <= value < closing_time):
            raise ValueError(f"start_time must be between {opening_time} and {closing_time}")

        return value
    
    @field_validator("end_time")
    def validate_end_time(cls, value) -> datetime.time:
        opening_time = datetime.time(GLOBAL_START_HOUR, 00)
        closing_time = datetime.time(GLOBAL_END_HOUR, 00)

        if not (opening_time < value <= closing_time):
            raise ValueError(f"end_time must be between {opening_time} and {closing_time}")

        return value
    
    @field_validator("end_time")
    @classmethod
    def validate_event_duration(cls, value, info: ValidationInfo) -> datetime.time:
        #print(values)
        end_time = value
        start_time = info.data["start_time"]        
        if start_time and end_time:
            start_time = datetime.datetime.combine(datetime.datetime.today(), start_time)
            end_time = datetime.datetime.combine(datetime.datetime.today(), end_time)
            # Check if appointment is over before it begins
            if end_time < start_time:
                raise ValueError("Appointment end time must be greater than event start time")            
            
            # Check if the duration is within the allowed range
            if end_time - start_time > datetime.timedelta(minutes = GLOBAL_APPOINTMENT_LENGTH):
                raise ValueError("Appointment duration must be 15 minutes or less")

        return value
        
    
class AppointmentCreate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    aid: int
    created_at: datetime.datetime
    