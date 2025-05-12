from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form, Request
from typing import List, Dict
from app.Schema import TestBase
from app.mongodb import db
import os, shutil, json, base64
from pydantic import BaseModel

MEDIA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'media'))
if not os.path.exists(MEDIA_DIR):
    os.makedirs(MEDIA_DIR, exist_ok=True)

# Create a test for test endpoints
test = APIRouter()

# Reference the MongoDB collection
tests_collection = db["tests"]

@test.get("/tests", response_model=List[str])
async def list_tests():
    """
    Return a list of all test variants.
    """
    try:
        # Only return the 'variant' field
        docs = await tests_collection.find({}).to_list(length=1000)
        return [d["variant"] for d in docs]
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch tests from database")

@test.get("/test/{variant}")
async def get_test(variant: str):
    """
    Fetch a single test by its variant.
    """
    try:
        doc = await tests_collection.find_one({"variant": variant})
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch test from database")
    if not doc:
        raise HTTPException(status_code=404, detail="Test not found")
    # Read and encode photos
    variant_dir = os.path.join(MEDIA_DIR, variant)
    embedded_photos: List[Dict[str, str]] = []
    for fn in sorted(doc.get("photos", [])):
        path = os.path.join(variant_dir, fn)
        if os.path.isfile(path):
            with open(path, "rb") as f:
                embedded_photos.append(base64.b64encode(f.read()).decode())
    # print(embedded_photos)
    doc.pop("photos", None)
    doc.pop("_id", None)
    return {
        **doc,
        "photos": embedded_photos
    }


@test.post("/test")
async def create_test(
    test_json: str = Form(...),
    photos: List[UploadFile] = File(None)
    ):
    """
    Create or overwrite a test definition.
    """
    try:
        test = json.loads(test_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid test JSON")
    # test = test.dict()
    variant = test["variant"]
    # Prepare directory for this variant
    variant_dir = os.path.join(MEDIA_DIR, variant)
    os.makedirs(variant_dir, exist_ok=True)

    if os.path.exists(variant_dir):
        for filename in os.listdir(variant_dir):
            file_path = os.path.join(variant_dir, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
    else:
        os.makedirs(variant_dir, exist_ok=True)

    photo_names: List[str] = []
    if photos:
        for idx, upload in enumerate(photos, start=1):
            ext = os.path.splitext(upload.filename)[1]
            filename = f"{idx}{ext}"
            dest_path = os.path.join(variant_dir, filename)
            content = await upload.read()
            with open(dest_path, 'wb') as out_file:
                out_file.write(content)
            photo_names.append(filename)
    
    
    # Build payload with answers and photo filenames
    
    test["photos"] = photo_names

    try:
        # Upsert by variant
        await tests_collection.replace_one({"variant": variant}, test, upsert=True)
        return variant # return the variant as a response
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to save test to database")

@test.put("/test", response_model=dict)
async def update_test(
    test_json: str = Form(...),
    photos: List[UploadFile] = File(None)
):
    """
    Update an existing test by variant.
    """
    try:
        test = json.loads(test_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid test JSON")
    # test = test.dict()
    variant = test["variant"]
    # Prepare directory for this variant
    variant_dir = os.path.join(MEDIA_DIR, variant)
    os.makedirs(variant_dir, exist_ok=True)

    if os.path.exists(variant_dir):
        for filename in os.listdir(variant_dir):
            file_path = os.path.join(variant_dir, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
    else:
        os.makedirs(variant_dir, exist_ok=True)

    photo_names: List[str] = []
    if photos:
        for idx, upload in enumerate(photos, start=1):
            ext = os.path.splitext(upload.filename)[1]
            filename = f"{idx}{ext}"
            dest_path = os.path.join(variant_dir, filename)
            content = await upload.read()
            with open(dest_path, 'wb') as out_file:
                out_file.write(content)
            photo_names.append(filename)

    # Build payload with answers and photo filenames
    test["photos"] = photo_names
    try:
        result = await tests_collection.update_one(
            {"variant": variant},
            {"$set": test}
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to update test in database")
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Test not found")
    return {"message": "Test changed successfully"}

@test.delete("/test/{variant}")
async def delete_test(variant: str):
    """
    Delete a test by its variant and remove its media subfolder.
    """
    try:
        result = await tests_collection.delete_one({"variant": variant})
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to delete test from database")
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Test not found")

    # Remove media folder
    variant_dir = os.path.join(MEDIA_DIR, variant)
    try:
        if os.path.exists(variant_dir):
            shutil.rmtree(variant_dir)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove media folder: {e}")

    return {"message": "Test and media deleted successfully"}

@test.put("/change/{curr}/{new}", response_model=dict)
async def change_variant(curr: str, new: str):
    """
    Change the variant name of a test and rename its media subfolder.
    """
    try:
        result = await tests_collection.update_one({"variant": curr}, {"$set": {"variant": new}})
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to change variant in database")
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Variant not found")

    # Rename media folder
    curr_dir = os.path.join(MEDIA_DIR, curr)
    new_dir = os.path.join(MEDIA_DIR, new)
    try:
        if os.path.exists(curr_dir):
            os.rename(curr_dir, new_dir)
    except Exception as e:
        # Attempt to rollback DB change
        await tests_collection.update_one({"variant": new}, {"$set": {"variant": curr}})
        raise HTTPException(status_code=500, detail=f"Failed to rename media folder: {e}")

    return {"message": "Variant changed successfully"}