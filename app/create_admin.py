#!/usr/bin/env python3
from getpass import getpass
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models import User
from app.auth import get_password_hash
from mongodb import MONGO_URL

async def create():
    # Load environment variables (MONGODB_URI, etc.)

    # Initialize MongoDB client and Beanie
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.get_default_database()
    await init_beanie(database=db, document_models=[User])

    print("=== Admin User Creation ===")
    username = "admin"
    role = "admin"
    email = "admin@gmail.com"
    password = "admin"


    # Check if user already exists
    existing = await User.find_one({"username": username})
    if existing:
        print(f"User '{username}' already exists with role '{existing.role}'.")
        return

    # Create admin user
    hashed_pwd = get_password_hash(password)
    admin = User(
        username=username,
        email=email,
        hashed_password=hashed_pwd,
        role=role
    )
    await admin.insert()
    print(f"Admin user '{username}' created successfully.")

async def create2():
    # Load environment variables (MONGODB_URI, etc.)

    # Initialize MongoDB client and Beanie
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.get_default_database()
    await init_beanie(database=db, document_models=[User])

    print("=== Student User Creation ===")
    username = "student"
    email = "student@gmail.com"
    password = "student"
    role = "student"


    # Check if user already exists
    existing = await User.find_one({"username": username})
    if existing:
        print(f"User '{username}' already exists with role '{existing.role}'.")
        return

    # Create admin user
    hashed_pwd = get_password_hash(password)
    admin = User(
        username=username,
        email=email,
        hashed_password=hashed_pwd,
        role=role
    )
    await admin.insert()
    print(f"Student user '{username}' created successfully.")