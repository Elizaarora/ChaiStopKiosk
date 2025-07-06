import requests
import firebase_admin
from firebase_admin import credentials, auth
import json
import streamlit as st

# ✅ Initialize Firebase Admin SDK using Streamlit Secrets
if not firebase_admin._apps:
    firebase_config = json.loads(st.secrets["firebase_config"])
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

# ✅ SIGNUP FUNCTION (creates user + email verification link)
def signup_user(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        verification_link = auth.generate_email_verification_link(email)
        st.success(f"User created successfully ✅\n\nPlease verify your email:\n{verification_link}")
        return True
    except Exception as e:
        st.error(f"Signup Error: {e}")
        return False

# ✅ LOGIN FUNCTION (via Firebase REST API)
def login_user(email, password):
    try:
        # 🔑 Use your Web API key stored securely in Streamlit secrets
        api_key = st.secrets["firebase_web_api_key"]

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
                st.warning("Please verify your email before logging in.")
                return False
            return True
        else:
            error_msg = data.get("error", {}).get("message", "Unknown error")
            st.error(f"Login failed: {error_msg}")
            return False

    except Exception as e:
        st.error(f"Login error: {e}")
        return False
