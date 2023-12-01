import datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from .main import app, get_db
from . import models
from .database import engine


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"  # IN-MEMORY seems to fail all tests...
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args = {"check_same_thread" : False},
    poolclass = StaticPool,    
    )
TestingSessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)

models.Base.metadata.create_all(bind = engine) 

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Test Root and Empty Databasee                
def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Welcome to your Coronavirus Vaccination Appointment"}
    
def test_get_appointments_empty():    
    response = client.get("/appointment/check/all")
    assert response.status_code == 200
    assert response.json() == []    

#Test Create
def test_book_appointment():  
    """
    Test Booking a simple appointment 1 day in the future
    """
    response = client.post("/appointment/book/", json = {"user_id" : "User1", "description" : "Vaccine", "date"  : str(datetime.datetime.now().date() + datetime.timedelta(1)), "start_time" : str(datetime.time(12,00)), "end_time" : str(datetime.time(12, 30))})  
    assert response.status_code == 200
    assert response.json()["msg"] == "Booking Successful"
    assert response.json()["data"]["user_id"] == "User1"
    
def test_book_appointment_multiple():
    """
    Test booking multiple appointments at same time, different user_ids
    """
    responses = []
    for i in range(5):
        response = client.post("/appointment/book/", json = {"user_id" : f"User2_{i}", "description" : "Vaccine", "date"  : str(datetime.datetime.now().date() + datetime.timedelta(1)), "start_time" : str(datetime.time(13,00)), "end_time" : str(datetime.time(13, 30))})
        assert response.status_code == 200
        responses.append(response)
        
    assert responses[0].json()["msg"] == "Booking Successful"
    for i in range(1,5):
        assert responses[i].json()["msg"] == "Booking not available"
        
def test_book_appointment_in_past():
    """
    Test booking an appointment in the past does not book an appointment
    """
    response = client.post("/appointment/book/", json = {"user_id" : "User3", "description" : "Vaccine", "date"  : str(datetime.date(2023, 11, 30)), "start_time" : str(datetime.time(8,00)), "end_time" : str(datetime.time(8, 30))})  
    assert response.status_code == 200
    assert response.json()["msg"] == "Appointment start-time must be in the future."
    assert response.json()["data"] == None
#    
def test_book_appointment_end_before_start():
    """
    Test booking an invalid appointment (start_time > end_time) doesn't book an appointment
    """
    response = client.post("/appointment/book/", json = {"user_id" : "User4", "description" : "Vaccine", "date"  : str(datetime.datetime.now().date() + datetime.timedelta(1)), "start_time" : str(datetime.time(9,00)), "end_time" : str(datetime.time(8, 30))})  
    assert response.status_code == 200
    assert response.json()["msg"] == "Appointment start-time must be before appointment end-time." 
    assert response.json()["data"] == None
    
def test_add_additional_appointments():
    response = client.post("/appointment/book/", json = {"user_id" : "User5", "description" : "Vaccine", "date"  : str(datetime.datetime.now().date() + datetime.timedelta(1)), "start_time" : str(datetime.time(9,00)), "end_time" : str(datetime.time(9, 30))})  
    response = client.post("/appointment/book/", json = {"user_id" : "User6", "description" : "Vaccine", "date"  : str(datetime.datetime.now().date() + datetime.timedelta(2)), "start_time" : str(datetime.time(14,00)), "end_time" : str(datetime.time(15, 00))})  
    response = client.post("/appointment/book/", json = {"user_id" : "User7", "description" : "Vaccine", "date"  : str(datetime.datetime.now().date() + datetime.timedelta(1)), "start_time" : str(datetime.time(12,30)), "end_time" : str(datetime.time(13, 00))})  
    response = client.post("/appointment/book/", json = {"user_id" : "User8", "description" : "Vaccine", "date"  : str(datetime.datetime.now().date() + datetime.timedelta(3)), "start_time" : str(datetime.time(12,00)), "end_time" : str(datetime.time(12, 30))})   

def test_book_appointment_user_already_booked():
    """
    Test a user who already has an appointment cannot add an additional appointment
    """
    response = client.post("/appointment/book/", json = {"user_id" : "User1", "description" : "Vaccine", "date"  : str(datetime.datetime.now().date() + datetime.timedelta(2)), "start_time" : str(datetime.time(10,00)), "end_time" : str(datetime.time(10, 30))})
    assert response.status_code == 200
    assert response.json()["msg"] == "Booking not available, User is already booked"
    assert response.json()["data"] == None
    
def test_book_appointment_invalid_values():
    """
    Test if user_id isn't a string
    """
    response = client.post("/appointment/book/", json = {"user_id" : 123, "description" : "Vaccine", "date"  : str(datetime.datetime.now().date() + datetime.timedelta(2)), "start_time" : str(datetime.time(10,00)), "end_time" : str(datetime.time(10, 30))})
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == 'Input should be a valid string'

# Test Get/Check
 
def test_get_appointments():   
    """
    Test all appointments can be receieved
    """      
    response = client.get("/appointment/check/all")
    assert response.status_code == 200
    assert len(response.json()) == 6

def test_get_appointments_day():
    """
    Test all appointments on a given day can be received
    """
    date = str(datetime.datetime.now().date() + datetime.timedelta(1))
    response = client.get(f"/appointment/check/all_available/{date}")
    assert response.status_code == 200
    assert len(response.json()) == 4
    for res in response.json():
        assert res["date"] == date

def test_get_appointment_status():
    """
    Test if appointment timeslot already exists when it does
    """
    date = str(datetime.datetime.now().date() + datetime.timedelta(1))
    start_time = str(datetime.time(13, 00))
    end_time = str(datetime.time(13, 30))    
    response = client.get("/appointment/check/", params = {"date" :  date, "start_time" : start_time, "end_time" : end_time})
    assert response.status_code == 200, response.text
    assert response.json() == {"msg": "Appointment Status", "data" : "Unavailable"}

def test_get_appointment_status_does_not_exist():
    """
    Test if appointment timeslot already exists when it doesn't
    """
    date = str(datetime.datetime.now().date() + datetime.timedelta(1))
    start_time = str(datetime.time(11, 00))
    end_time = str(datetime.time(11, 30))    
    response = client.get("/appointment/check/", params = {"date" :  date, "start_time" : start_time, "end_time" : end_time})
    assert response.status_code == 200, response.text
    assert response.json() == {"msg": "Appointment Status", "data" : "Available"}

# Test Delete

def test_cancel_appointment():
    """
    Test if can cancel appointment that exists
    """
    user_id = "User8"
    date = str(datetime.datetime.now().date() + datetime.timedelta(3))
    response = client.delete(f"/appointment/cancel/{user_id}", params = {"date" : date})
    assert response.status_code == 200
    assert response.json()["msg"] == "Booking Deleted"
    assert response.json()["data"]["user_id"] == user_id
    assert response.json()["data"]["date"] == date
    

def test_cancel_appointment_does_not_exist():
    """
    Test if can cancel appointmnet that doesn't exist
    """
    user_id = "User9"
    date = str(datetime.datetime.now().date() + datetime.timedelta(1))
    response = client.delete(f"/appointment/cancel/{user_id}", params = {"date" : date})
    assert response.status_code == 200
    assert response.json()["msg"] == "No booking deleted"
    assert response.json()["data"] == None
    
# Test Ideas:
# Book appointments too far in the future - limit 3 months
# Book appointment outside of business hours

