
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class EmployeeBase(BaseModel):
    name: str
    email: EmailStr
    department: Optional[str] = None
    role: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    name: str = Field(..., min_length=1, description="Name of the employee")
    email: EmailStr = Field(..., description="Unique email address of the employee")

class EmployeeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, description="Name of the employee")
    email: Optional[EmailStr] = Field(None, description="Unique email address of the employee")
    department: Optional[str] = None
    role: Optional[str] = None

class Employee(EmployeeBase):
    id: int
    date_joined: datetime

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True