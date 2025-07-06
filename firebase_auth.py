import requests
import firebase_admin
from firebase_admin import credentials, auth
import json
import streamlit as st

# ✅ Initialize Firebase using secrets
if not firebase_admin._apps:
    firebase_config = json.loads(st.secrets["firebase_config"])
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

# ✅ Sign up function
def signup_user(email, password):
    try:
        email = email.strip().lower()
        user = auth.create_user(email=email, password=password)
        verification_link = auth.generate_email_verification_link(email)
        print("✅ Email verification link:", verification_link)
        return f"User {email} created successfully! ✅\nPlease verify your email.\n\nLink: {verification_link}"
    except Exception as e:
        return str(e)

# ✅ Login function using Firebase REST API
def login_user(email, password):
    try:
        email = email.strip().lower()
        api_key = st.secrets["firebase_web_api_key"]  # ✅ stored in secrets
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"

        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        res = requests.post(url, json=payload)
        data = res.json()

        if "idToken" in data:
            if not data.get("emailVerified", False):
                print("⚠️ Email not verified")
                return False
            return True
        else:
            print("Login Error:", data.get("error", {}).get("message", "Unknown"))
            return False
    except Exception as e:
        print("Login Error:", e)
        return False
