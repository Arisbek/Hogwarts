
# app/frames.py
import os
import json
from fastapi import APIRouter, HTTPException
from typing import List
from app.Schema import FrameBase
from app.mongodb import db

# rename frames to avoid collision with collection
frames = APIRouter(prefix="/frames")

# refer to your MongoDB collection explicitly
frames_collection = db["frames"]

@frames.get("/", response_model=List[str])
async def list_frames():
    """
    Return list of all saved frame names.
    """
    try:
        # projection to only include 'name'
        docs = await frames_collection.find({}, {"_id":0, "name":1}).to_list(length=1000)
        return [d["name"] for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch frame list")

@frames.get("/{name}", response_model=FrameBase)
async def get_frame(name: str):
    """
    Return a specific frame by name.
    """
    try:
        doc = await frames_collection.find_one({"name": name}, {"_id":0})
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch frame from database")
    if not doc:
        raise HTTPException(status_code=404, detail="Frame not found")
    return doc

@frames.post("/", response_model=FrameBase)
async def create_frame(frame: FrameBase):
    """
    Save a new frame to the database (upsert).
    """
    payload = frame.dict()
    try:
        await frames_collection.replace_one({"name": frame.name}, payload, upsert=True)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to save frame to database")
    return frame