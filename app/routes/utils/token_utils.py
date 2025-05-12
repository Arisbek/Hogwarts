import os
from itsdangerous import URLSafeTimedSerializer, BadTimeSignature, SignatureExpired
from pydantic import EmailStr
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fetch SECRET_KEY from environment, error if missing
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set in environment variables")

serializer = URLSafeTimedSerializer(SECRET_KEY, salt="email-verification")

def make_token(email: EmailStr) -> str:
    return serializer.dumps(email)

def verify_token(token: str, max_age: int = 1800) -> str | None:
    try:
        return serializer.loads(token, max_age=max_age)
    except (SignatureExpired, BadTimeSignature):
        return None