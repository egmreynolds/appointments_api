#!/usr/bin/env python
import datetime
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

#from slowapi import Limiter, _rate_limit_exceeded_handler
#from slowapi.util import get_remote_address
#from slowapi.errors import RateLimitExceeded

from . import crud, models, schemas
from .database import SessionLocal, engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup:
    models.Base.metadata.create_all(bind=engine)
    yield
    # Shutdown:
    pass

#limiter = Limiter(key_func=get_remote_address, default_limits=["5/second"])

app = FastAPI(lifespan = lifespan)

#app.state.limiter = limiter
#app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@app.get("/")
def read_main():
    """
    Return HomePage - Maybe add a button to take you to the next screen
    """
    return {"msg": "Welcome to your Coronavirus Vaccination Appointment"}

@app.get("/appointment/check/")
async def get_appointment_status(date: datetime.date, start_time: datetime.time, end_time: datetime.time, db: Session = Depends(get_db)):
    """
    Return Bool whether appointment time is booked or not.    
    """
    print("test")
    if crud.get_appointment_date_and_time(db = db, date = date, start_time = start_time, end_time = end_time) == []:
        return {"msg" : "Appointment Status", "data" : "Available"}
    
    return {"msg" : "Appointment Status", "data" : "Unavailable"}

@app.get("/appointment/check/all")
async def get_appointments(db: Session = Depends(get_db)):
    """
    Return all timeslots with availability
    """
    appointments = crud.get_all_appointments(db = db)
    return appointments

@app.get("/appointment/check/all_available/{date}")
async def get_appointments_day(date: datetime.date, db: Session = Depends(get_db)):
    """
    Return all timeslots with availability for {day}
    """
    return crud.get_all_appointments_by_date(db = db, date = date)

@app.post("/appointment/book/")
async def book_appointment(appointment: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    """
    Check appointment is valid
    Check appointment is available
    Check user_id hasn't already booked
    if true - > Book appointment
    Return Bool if appointment is successfully booked
    """
    if crud.get_appointment_date_and_time(db = db, date = appointment.date, start_time = appointment.start_time, end_time = appointment.end_time) == []:
        if crud.get_all_appointments_by_user(db = db, user_id = appointment.user_id) == []:
            crud.create_appointment(db = db, appointment = appointment)
            return {"msg" : "Booking Successful", "data" : appointment}
        else:
            return {"msg": "Booking not available, User is already booked", "data" : None}
    else:
        return {"msg" : "Booking not available", "data" : None}   

@app.delete("/appointment/cancel/{user_id}")
async def cancel_appointment(user_id: str, date : datetime.date, db = Depends(get_db)):
    """
    Check {user_id} has made an appointment
    If true -> Remove from database [set status to available]
    Return Bool
    """
    output = crud.delete_appointment(db = db, user_id = user_id, date = date)
    if output:
        return {"msg" : "Booking Deleted", "data" : output}
    
    return {"msg" : "No booking deleted", "data" : None}
