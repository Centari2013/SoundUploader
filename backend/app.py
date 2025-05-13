# backend/app.py
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import threading
from backend.uploader import upload_to_supabase

TAGGED_FILE_PATH = os.environ.get('TAGGED_OUTPUT_FILE')
APPROVED_FILE_PATH = os.environ.get('APPROVED_FILE_PATH')
app = FastAPI()
origins = ["http://localhost:5173"]  # Vue dev server

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/tagged")
def get_tagged():
    if os.path.exists(TAGGED_FILE_PATH):
        with open(TAGGED_FILE_PATH) as f:
            return json.load(f)
    return []


@app.post("/approve")
def approve_batch(data: list = Body(...)):
    with open(APPROVED_FILE_PATH, "w") as f:
        json.dump(data, f, indent=2)

    # Fire and forget upload job
    threading.Thread(target=upload_to_supabase).start()

    return {"status": "ok"}

