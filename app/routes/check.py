from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from fastapi.responses import JSONResponse
from app.mongodb import db
from app.Schema import TestBase
import io
from maindir.check import process_image
import datetime


profile_collection = db["users"]

# Map Cyrillic letters to indices
d = {'а': 0, 'б': 1, 'в': 2, 'г': 3, 'д': 4}

check = APIRouter(prefix="/check")

tests_collection = db["tests"]
users_collection = db["users"]

@check.post("/{variant}")
async def check_test(
    variant: str,
    role: str = Form(...),
    photo: UploadFile = File(...)
):
    # 1) Validate file type
    if not photo.content_type.startswith("image/"):
        return JSONResponse({"error": "Invalid file type"}, status_code=400)

    # 2) Read uploaded image bytes
    contents = await photo.read()

    # 3) Fetch the test definition from MongoDB
    try:
        doc = await tests_collection.find_one({"variant": variant})
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch test from database")
    if not doc:
        raise HTTPException(status_code=404, detail="Test not found")

    # 4) Parse into Pydantic model to validate schema
    test = TestBase(**doc)

    # 5) Extract answer letters and map to indices
    #    Assume all fields after 'variant' in TestBase are the answers
    data = test.dict()
    data.pop('variant', None)
    data.pop('_id', None)
    data.pop('photos', None)
    values = list(data.values())
    answers = [d.get(letter, None) for letter in values]
    if None in answers:
        raise HTTPException(status_code=500, detail="Unknown answer letter in test data")

    # 6) Split into question groups (example logic)
    m1 = answers[:30]
    m2 = answers[30:60]
    a  = answers[60:90]
    r  = answers[90:120]
    g  = answers[120:150]

    m1 = [m1[i*6:(i+1)*6] for i in range(5)]
    m2 = [m2[i*8:(i+1)*8] for i in range(4)]
    a  = [a[i*6:(i+1)*6] for i in range(5)]
    r  = [r[i*6:(i+1)*6] for i in range(5)]
    g  = [g[i*6:(i+1)*6] for i in range(5)]
    m2[-1].append(0)
    m2[-1].append(0)

    # 7) Run OMR processing
    photo_file = io.BytesIO(contents)
    result_b64, score = process_image(m1, m2, a, r, g, photo_file)

    # 8) Record timestamp and score under "marks"
    timestamp = datetime.datetime.now()
    record = { 'timestamp': timestamp, 'variant': variant, 'score': score }
    try:
        await users_collection.update_one(
            {'username': role},
            {'$push': {'marks': record}},
            upsert=True
        )
    except Exception:
        # Log warning but continue
        pass

    # 8) Return the processed image
    return JSONResponse({"image": result_b64})
