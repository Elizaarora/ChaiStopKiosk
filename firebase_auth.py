import requests
import firebase_admin
from firebase_admin import credentials, auth

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_config.json")
    firebase_admin.initialize_app(cred)

# ✅ SIGNUP FUNCTION (same as before)
def signup_user(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        verification_link = auth.generate_email_verification_link(email)
        print("✅ Email verification link:", verification_link)
        return f"User {email} created successfully! ✅\nPlease verify your email.\n\nLink: {verification_link}"
    except Exception as e:
        return str(e)

# ✅ UPDATED LOGIN FUNCTION using Firebase REST API
def login_user(email, password):
    try:
        api_key = "AIzaSyCbpbHy4DSqXt1c9C9iBTvT7p5OxukNtgE"  # <-- Replace this with your actual Web API Key
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"

        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        res = requests.post(url, json=payload)
        data = res.json()

        if "idToken" in data:
            return True
        else:
            print("Login Error:", data.get("error", {}).get("message", "Unknown"))
            return False
    except Exception as e:
        print("Login Error:", e)
        return False
