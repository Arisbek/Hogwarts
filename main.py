from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
# from PIL import Image
import io
# import base64
import uvicorn
# from ..maindir.check import *  # Assuming this is where your `process_image` function is
# from app.mongodb import database
from app.routes.Test import test
from app.routes.check import check
from app.routes.check2 import check2
from app.routes.check3 import check3
from app.routes.Frame import frames
from app.routes.auth_routes import router
from app.routes.profile import profiles
from fastapi.staticfiles import StaticFiles
from app.auth import get_current_user, student_required
from app.create_admin import create, create2
import asyncio, os

app = FastAPI()
app.include_router(router)  # Include your auth routes here
app.include_router(test)
app.include_router(check)
app.include_router(check2)
app.include_router(check3)
app.include_router(frames)
app.include_router(profiles)

origins = [
]

# Add CORS middleware to allow requests from specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # You can add more origins here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)


if __name__ == "__main__":
    # asyncio.run(create())
    # asyncio.run(create2())
    uvicorn.run('main:app', host="localhost", port=8000)
