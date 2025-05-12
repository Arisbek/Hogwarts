# app/profile.py
import os
import json
from fastapi import APIRouter, HTTPException
from typing import List
from app.Schema import FrameBase
from app.mongodb import db
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


# rename frames to avoid collision with collection
profiles = APIRouter(prefix="/profiles")

# refer to your MongoDB collection explicitly
profile_collection = db["users"]

@profiles.get("/")
async def list_frames():
    """
    Return list of all saved frame names.
    """
    try:
        # projection to only include 'name'
        docs = await profile_collection.find({})
        return [d["name"] for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch frame list")

@profiles.get("/{username}")
async def get_profile(username: str):
    try:
        doc = await profile_collection.find_one({"username": username})
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch profile from database")

    if not doc:
        raise HTTPException(status_code=404, detail="Profile not found")

    doc.pop("_id", None)
    doc.pop("hashed_password", None)  # Remove password if present

    # Ensure everything is JSON serializable
    safe_doc = jsonable_encoder(doc)
    return JSONResponse(content=safe_doc)

# @profiles.patch("/")
# async def create_frame(frame: FrameBase):
#     """
#     Save a new frame to the database (upsert).
#     """
#     payload = frame.dict()
#     try:
#         await profile_collection.replace_one({"name": frame.name}, payload, upsert=True)
#     except Exception:
#         raise HTTPException(status_code=500, detail="Failed to save frame to database")
#     return frame