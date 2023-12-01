# Appointments API
This app is designed to create, check, and delete appointments at your local doctors office using in-memory database

### Prerequisites:
Python3.10

fastapi, uvicorn[standard], sqlalchemy

### Setup and Run:
```
git clone https://github.com/egmreynolds/appointments_api.git
cd appointments_api
python -m venv venv 
. venv/Scripts/activate #windows
# ./venv/bin/activate #unix
pip install -r requirements.txt

uvicorn app.main:app --reload
```





