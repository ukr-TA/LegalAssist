from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

import firebase_admin
from firebase_admin import credentials, auth, firestore

# Initialize Firebase Admin
cred = credentials.Certificate("firebase_key.json")  # Make sure this path is correct
firebase_admin.initialize_app(cred)
db = firestore.client()

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],  # Replace with frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 token scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os

load_dotenv()

@app.get("/firebase-config")
async def get_firebase_config():
    return JSONResponse({
        "apiKey": os.getenv("FIREBASE_API_KEY"),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
        "projectId": os.getenv("FIREBASE_PROJECT_ID"),
        "appId": os.getenv("FIREBASE_APP_ID"),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
        "messagingSenderId": os.getenv("FIREBASE_MSG_SENDER_ID"),
        "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID"),
    })


# Pydantic models
class UserSignup(BaseModel):
    username: str  # Email for Firebase
    password: str

class ChatRequest(BaseModel):
    user_message: str

# Firebase Signup
@app.post("/signup")
async def signup(user: UserSignup):
    try:
        user_record = auth.create_user(
            email=user.username,
            password=user.password
        )
        return {"message": "User created successfully", "uid": user_record.uid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Firebase Login
@app.post("/login")
async def login(user: UserSignup):
    raise HTTPException(
        status_code=501,
        detail="Login is handled on the frontend with Firebase Auth. Use frontend to get token."
    )

# Chat endpoint (requires Firebase token)
@app.post("/chat")
async def chat(req: ChatRequest, token: str = Depends(oauth2_scheme)):
    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']

        # Optionally save message to Firestore
        db.collection("messages").add({
            "uid": uid,
            "message": req.user_message
        })

        return {"bot_reply": f"You said: {req.user_message}. LegalAssist says hello!"}
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

