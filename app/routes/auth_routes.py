from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from app.auth import (
    authenticate_user, create_access_token,
    get_password_hash, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
from itsdangerous import URLSafeTimedSerializer, BadTimeSignature,SignatureExpired
from pydantic import EmailStr
from app.Schema import UserBase, EmailSchema
from app.models import User
from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from .utils.token_utils import make_token, verify_token
from .utils.mailer_utils import send_verification_email
import os
from app.mongodb import db

USERS = db["users"]
FRONTEND_URL = os.getenv("FRONTEND_URL")

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/profile")
async def profile(user=Depends(get_current_user)):
    return {
      "username": user.username,
      "email": user.email,
      "role": user.role
    }

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request: Request, payload: dict):
    """
    payload should contain at least:
      { "email": "...", "username": "...", "password": "..." }
    """
    email = payload.get("email")
    username = payload.get("username")
    raw_pw = payload.get("password")
    role = payload.get("role", "student")  # default to student
    password = payload.get("password", '')  # optional field

    # 1) check for existing email
    if await USERS.find_one({"email": email}):
        raise HTTPException(status_code=409, detail="Email already registered")
    
    if await USERS.find_one({"username": username}):
        raise HTTPException(status_code=409, detail="User already registered")

    # 2) hash and insert
    hashed = get_password_hash(raw_pw)
    new_user = {
        "email": email,
        "username": username,
        "hashed_password": hashed,
        "role": role,
        "marks": [],
        "password": password,
        "is_verified": False
    }
    result = await USERS.insert_one(new_user)
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to create user")

    # 3) email verification
    token = make_token(email)
    # verify_link = f"{FRONTEND_URL}/verify-email/{token}"
    # body = {
    #     "email": email,
    #     "project_name": "Hogwarts",
    #     "url": verify_link
    # }
    sent = send_verification_email(
        to_address=email,
        token = token
    )
    if not sent:
        # optionally roll back or log
        await USERS.delete_one({"_id": result.inserted_id})
        return {
            "message": "User created, but failed to send verification email."
        }

    return {
        "message": "Registration successful. Please check your email to verify."
    }

@router.post('/login/', status_code=status.HTTP_200_OK)
async def login(user_credentials:OAuth2PasswordRequestForm= Depends()):

    # Filter search for user
    user = await USERS.find_one({"username": user_credentials.username})


    if not user:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail= "Invalid Username or Password",
            headers={"WWW-Authenticate":"Bearer"}
        )
    if user.is_verified != True:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail= "Account Not Verified"
        )

    access_token = create_access_token(data={'user_id':user.id})
    return {
        'access_token':access_token,
        'token_type': 'bearer'
    }

@router.post(
    "/confirm-email/{token}/",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Verify a users email via token"
)
async def user_verification(token: str):
    # 1) Decode token → email
    email = verify_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Email verification token is invalid or expired."
        )

    # 2) Lookup user document
    user = await USERS.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user found with email {email}"
        )

    # 3) Update is_verified flag
    result = await USERS.update_one(
        {"email": email},
        {"$set": {"is_verified": True}}
    )
    if result.modified_count == 0:
        # either it was already verified, or update failed
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark email as verified."
        )

    return {
        "message": "Email verification successful.",
        "status": status.HTTP_202_ACCEPTED
    }

@router.post('/resend-verification/', status_code=status.HTTP_201_CREATED)
async def send_email_verfication(email_data:EmailSchema):
    user_check = USERS.find_one({"email": email_data.email})
    if not user_check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail= "User information does not exist")
    if user_check.is_verified == True:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail= "User already verified")
    token = token(email_data.email)
    mail_status = await send_verification_email(
        to_address=email_data.email,
        token = token
    )
    if mail_status == True:
        return {
        "message":"mail for Email Verification has been sent, kindly check your inbox.",
        "status": status.HTTP_201_CREATED
        }
    else:
        return {
        "message":"mail for Email Verification failled to send, kindly reach out to the server guy.",
        "status": status.HTTP_503_SERVICE_UNAVAILABLE
        }