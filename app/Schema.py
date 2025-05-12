from pydantic import BaseModel, EmailStr, Field
# from typing import Literal
from enum import Enum
from typing import List, Any
from datetime import datetime

class Choice(str, Enum):
    A = "а"
    B = "б"
    C = "в"
    D = "г"

class Choice2(str, Enum):
    A = "а"
    B = "б"
    C = "в"
    D = "г"
    E = "д"

class TestBase(BaseModel):
    variant: str
    M1: Choice
    M2: Choice
    M3: Choice
    M4: Choice
    M5: Choice
    M6: Choice
    M7: Choice
    M8: Choice
    M9: Choice
    M10: Choice
    M11: Choice
    M12: Choice
    M13: Choice
    M14: Choice
    M15: Choice
    M16: Choice
    M17: Choice
    M18: Choice
    M19: Choice
    M20: Choice
    M21: Choice
    M22: Choice
    M23: Choice
    M24: Choice
    M25: Choice
    M26: Choice
    M27: Choice
    M28: Choice
    M29: Choice
    M30: Choice

    M31: Choice2
    M32: Choice2
    M33: Choice2
    M34: Choice2
    M35: Choice2
    M36: Choice2
    M37: Choice2
    M38: Choice2
    M39: Choice2
    M40: Choice2
    M41: Choice2
    M42: Choice2
    M43: Choice2
    M44: Choice2
    M45: Choice2
    M46: Choice2
    M47: Choice2
    M48: Choice2
    M49: Choice2
    M50: Choice2
    M51: Choice2
    M52: Choice2
    M53: Choice2
    M54: Choice2
    M55: Choice2
    M56: Choice2
    M57: Choice2
    M58: Choice2
    M59: Choice2
    M60: Choice2

    A1: Choice
    A2: Choice
    A3: Choice
    A4: Choice
    A5: Choice
    A6: Choice
    A7: Choice
    A8: Choice
    A9: Choice
    A10: Choice
    A11: Choice
    A12: Choice
    A13: Choice
    A14: Choice
    A15: Choice
    A16: Choice
    A17: Choice
    A18: Choice
    A19: Choice
    A20: Choice
    A21: Choice
    A22: Choice
    A23: Choice
    A24: Choice
    A25: Choice
    A26: Choice
    A27: Choice
    A28: Choice
    A29: Choice
    A30: Choice

    R1: Choice
    R2: Choice
    R3: Choice
    R4: Choice
    R5: Choice
    R6: Choice
    R7: Choice
    R8: Choice
    R9: Choice
    R10: Choice
    R11: Choice
    R12: Choice
    R13: Choice
    R14: Choice
    R15: Choice
    R16: Choice
    R17: Choice
    R18: Choice
    R19: Choice
    R20: Choice
    R21: Choice
    R22: Choice
    R23: Choice
    R24: Choice
    R25: Choice
    R26: Choice
    R27: Choice
    R28: Choice
    R29: Choice
    R30: Choice

    G1: Choice
    G2: Choice
    G3: Choice
    G4: Choice
    G5: Choice
    G6: Choice
    G7: Choice
    G8: Choice
    G9: Choice
    G10: Choice
    G11: Choice
    G12: Choice
    G13: Choice
    G14: Choice
    G15: Choice
    G16: Choice
    G17: Choice
    G18: Choice
    G19: Choice
    G20: Choice
    G21: Choice
    G22: Choice
    G23: Choice
    G24: Choice
    G25: Choice
    G26: Choice
    G27: Choice
    G28: Choice
    G29: Choice
    G30: Choice

class CreateLog(TestBase):
    class Config:
        orm_mode = True


class Transform(BaseModel):
    scale: float
    x: float
    y: float

class Square(BaseModel):
    x: float
    y: float
    width: float
    height: float

class Group(BaseModel):
    question: str
    count: int
    x: float
    y: float
    width: float
    height: float
    squares: List[Square]

class FrameBase(BaseModel):
    name: str
    image_src: str
    transform: Transform
    groups: List[Group]

    class Config:
        orm_mode = True

class UserBase(BaseModel):
   email: EmailStr
   role: str="student" # "admin" or "student"
   username: str
   password:str

class UserCreate(UserBase):
    pass

class UserLogin(BaseModel):
    email:EmailStr
    password: str

class UserResponse(BaseModel):
    id:int
    email:EmailStr
    created_at:datetime
   
    class Config:
       orm_mode = True

class RegistrationUserRepsonse(BaseModel):
    message:str
    data: UserResponse
    
    
class EmailSchema(BaseModel):
    email:EmailStr