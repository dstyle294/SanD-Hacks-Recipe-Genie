import os
from typing import Optional
from fastapi import HTTPException
from jose import jwt
from datetime import datetime, timedelta
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from dotenv import load_dotenv

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 1 week

class AuthService:
    @staticmethod
    def verify_google_token(token: str):
        print(f"DEBUG: AuthService.verify_google_token called. Token length: {len(token) if token else 0}")
        if not GOOGLE_CLIENT_ID:
            print("DEBUG: GOOGLE_CLIENT_ID not found in environment. Using fallback.")
            return {"email": "test@example.com", "name": "Test User", "sub": "test-google-id", "picture": ""}
        
        try:
            print(f"DEBUG: Attempting verification with GOOGLE_CLIENT_ID: {GOOGLE_CLIENT_ID}")
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), GOOGLE_CLIENT_ID)
            print(f"DEBUG: Token verified. Email: {idinfo.get('email')}")
            return idinfo
        except Exception as e:
            print(f"DEBUG: Token verification failed: {str(e)}")
            raise HTTPException(status_code=401, detail=f"Invalid Google token: {str(e)}")

    @staticmethod
    def create_access_token(data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "sub": data.get("email")})
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str):
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
            return payload
        except:
            return None
