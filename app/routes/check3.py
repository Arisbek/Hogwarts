from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List
from app.mongodb import db
from app.Schema import TestBase
import datetime


check3 = APIRouter(prefix="/check3")
tests_collection = db["tests"]
users_collection = db["users"]

@check3.post("/{variant}")
async def check_test(
    variant: str,
    role: str=Form(...),
    response: List=Form(...)
):

    # 3) Fetch test definition
    try:
        doc = await tests_collection.find_one({"variant": variant})
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch test from database")
    if not doc:
        raise HTTPException(status_code=404, detail="Test not found")

    # 4) Validate and extract answers
    test = TestBase(**doc)
    data = test.dict()
    data.pop('variant', None)
    data.pop('photos', None)
    correct_answers = list(data.values())

    total_questions = len(correct_answers)
    if len(response) != total_questions:
        raise HTTPException(status_code=400, detail="Answer count mismatch")

    # 5) Compute correctness flags and section scores
    def score_section(start: int, end: int):
        count = 0
        for i in range(start, end):
            if response[i] == correct_answers[i]:
                count += 1
        return count

    math1 = score_section(0, 30)
    math2 = score_section(30, 60)
    adp   = score_section(60, 90)
    reading = score_section(90, 120)
    grammar = score_section(120, 150)
    score = (math1 + math2) * 70 / 60 + adp * 70 / 30 + reading * 2 + grammar * 1.5

    # 6) Record timestamp and score under 'marks'
    timestamp = datetime.datetime.now()
    record = {'timestamp': timestamp, 'variant': variant, 'score': score}
    try:
        await users_collection.update_one(
            {'username': role},
            {'$push': {'marks': record}},
            upsert=True
        )
    except Exception:
        pass

    # 7) Return result
    payload_out = {"result": correct_answers, "score": score}
    return JSONResponse(jsonable_encoder(payload_out))
