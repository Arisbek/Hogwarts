from motor.motor_asyncio import AsyncIOMotorClient
# from decouple import config  # or os.getenv

MONGO_URL = "mongodb://localhost:27017"
client    = AsyncIOMotorClient(MONGO_URL)
db        = client["omr_db"]
frames    = db["frames"]


# raw access to the same users collection that Beanie’s User model will use
users  = db["users"]
