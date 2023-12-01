from fastapi.testclient import TestClient
import datetime
from .main import app, get_db
from . import models
from .database import engine, SessionLocal
from .schemas import AppointmentCreate

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
SQLALCHEMY_DATABASE_URL = "sqlite:///test.db"  # IN-MEMORY seems to fail all tests...
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args = {"check_same_thread" : False})
TestingSessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)


                

    
def setup():
    models.Base.metadata.create_all(bind = engine)    
    #session = TestingSessionLocal()
    #appointment = models.Appointment(user_id = "Jeff", description = "Vaccination", date = datetime.date(2023, 11, 29), start_time = datetime.time(11,00), end_time = datetime.time(11, 30))
    #session.add(appointment)
    #session.commit()
    #session.close()    
    
def teardown():
    models.Base.metadata.drop_all(bind = engine)        
    
def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Welcome to your Coronavirus Vaccination Appointment"}
        
def test_get_appointments_empty():    
    response = client.get("/appointment/check/all")
    assert response.status_code == 200
    assert response.json() == []
    
def test_get_appointments():    
    session = TestingSessionLocal()
    a1 = models.Appointment(user_id = "Jeff", description = "Vaccination", date = datetime.date(2023, 11, 29), start_time = datetime.time(11,00), end_time = datetime.time(11, 30))
    a2 = models.Appointment(user_id = "Molly", description = "Vaccine", date = datetime.date(2023, 11, 30), start_time = datetime.time(13,00), end_time = datetime.time(13, 30))
    session.add(a1)
    session.add(a2)
    session.commit()
    session.close()        
    response = client.get("/appointment/check/all")
    assert response.status_code == 200
    assert response.json() == []
    
        
def test_book_appointment():  
    #appointment = AppointmentCreate(user_id = "Jeff", description = "Vaccine", date  = datetime.date(2023, 11, 30), start_time = datetime.time(11,00), end_time = datetime.time(11, 30))
    response = client.post("/appointment/book/", json = {"user_id" : "Mandy", "description" : "Vaccine", "date"  : str(datetime.date(2023, 11, 30)), "start_time" : str(datetime.time(12,00)), "end_time" : str(datetime.time(12, 30))})  
    assert response.status_code == 200
    
def test_get_appointment_status():
    time_slot = 0
    date = datetime.date(2023, 11, 30)
    start_time = datetime.time(11, 0)
    end_time = datetime.time(11,15)
    
    response = client.get("/appointment/check/", params = {"date" :  date, "start_time" : start_time, "end_time" : end_time})
    assert response.status_code == 200, response.text
    assert response.json() == {"msg": "Appointment Status", "data" : "Available"}

def test_book_appointment_multiple():
    for i in range(5):
        response = client.post("/appointment/book/", json = {"user_id" : "Sam", "description" : "Vaccine", "date"  : str(datetime.date(2023, 11, 30)), "start_time" : str(datetime.time(13,00)), "end_time" : str(datetime.time(13, 30))})  
    assert response.status_code == 200
    
def test_book_appointment_in_past():
    response = client.post("/appointment/book/", json = {"user_id" : "Max", "description" : "Vaccine", "date"  : str(datetime.date(2023, 11, 30)), "start_time" : str(datetime.time(8,00)), "end_time" : str(datetime.time(8, 30))})  
    assert response.status_code == 200
    assert response.json()["msg"] == "Appointment start-time must be in the future."
    
def test_book_appointment_end_before_start():
    response = client.post("/appointment/book/", json = {"user_id" : "Mike", "description" : "Vaccine", "date"  : str(datetime.date(2023, 11, 30)), "start_time" : str(datetime.time(9,00)), "end_time" : str(datetime.time(8, 30))})  
    assert response.status_code == 200
    assert response.json()["msg"] == "Appointment start-time must be before appointment end-time."
    
# Test Ideas:
# Book appointments in the past
# Book appointments too far in the future - limit 3 months
# Book regular appointment
# Book appointment outside of business hours
# Book appointment as user who already has an appointment
# Check appointment in the above states
# Plus Book appointment and check status
# Plus don't book appointment and check status
# Cancel appointment that exists
# Cancel appointment that doesn't exist