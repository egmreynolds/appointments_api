from sqlalchemy.orm import Session
from sqlalchemy import and_
from . import models, schemas
import datetime

def create_appointment(db: Session, appointment: schemas.AppointmentCreate):
    """
    Takes an array of VALUES, inserts into appointments table
    Returns Nothing
    """
    db_appointment = models.Appointment(user_id = appointment.user_id, description = appointment.description, date = appointment.date, start_time = appointment.start_time, end_time = appointment.end_time)
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

# get all appointment times
def get_all_appointments(db: Session):
    """
    Returns all booked appointment date and times
    """
    return db.query(models.Appointment).all()

def get_appointment_date_and_time(db: Session, date: datetime.date, start_time: datetime.time, end_time: datetime.time):
    """
    Checks if appointment already exists or clashes with existing appointment
    Returns True if a clash exists, else False
    """
    return db.query(models.Appointment).filter(models.Appointment.date == date).filter(
        and_(
            models.Appointment.start_time  < end_time,
            models.Appointment.end_time > start_time
        )
    ).all()

# check date
def get_all_appointments_by_date(db: Session, date: datetime.date):
    """
    Returns all booked appointments for date
    """
    return db.query(models.Appointment).filter(models.Appointment.date == date).all()

# check user
def get_all_appointments_by_user(db:Session, user_id: str):
    """
    Returns all booked appointments for user
    """
    return db.query(models.Appointment).filter(models.Appointment.user_id == user_id).all()

# delete appointment
def delete_appointment(db:Session, user_id: str, date: datetime.date):
    """
    Delete users appointment on specified date
    """
    row_to_delete= db.query(models.Appointment).filter_by(user_id = user_id, date = date).first()
    if row_to_delete:
        db.delete(row_to_delete)
        db.commit()
        return row_to_delete
    
    return []
