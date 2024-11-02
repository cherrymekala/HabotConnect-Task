
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from crud import get_employee, get_employees, create_employee, update_employee, delete_employee
from schemas import EmployeeCreate, EmployeeUpdate, Employee, UserCreate  
from models import Base, User
from fastapi.security import OAuth2PasswordRequestForm
from auth import create_access_token, verify_password, hash_password, verify_token, get_current_user
from fastapi import Depends
from pydantic import BaseModel
from datetime import timedelta


app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/api/employees/", response_model=Employee, status_code=status.HTTP_201_CREATED)
def create_employee_endpoint(employee: EmployeeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_employee(db=db, employee=employee)


@app.get("/api/employees/", response_model=list[Employee])
def list_employees(skip: int = 0, limit: int = 10, department: str = None, role: str = None, db: Session = Depends(get_db)):
    return get_employees(db, skip=skip, limit=limit, department=department, role=role)

@app.get("/api/employees/{id}", response_model=Employee)
def retrieve_employee(id: int, db: Session = Depends(get_db)):
    db_employee = get_employee(db, id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

@app.put("/api/employees/{id}", response_model=Employee)
def update_employee_endpoint(id: int, employee: EmployeeUpdate, db: Session = Depends(get_db)):
    return update_employee(db, id, employee)

@app.delete("/api/employees/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee_endpoint(id: int, db: Session = Depends(get_db)):
    delete_employee(db, id)
    return {"message": "Employee deleted"}


@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
 
    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == form_data.username).first()
    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": db_user.username}, expires_delta=timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer"}