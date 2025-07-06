# firebase_auth.py
import requests
import firebase_admin
from firebase_admin import credentials, auth
import json
import streamlit as st

# Initialize Firebase Admin from secrets
if not firebase_admin._apps:
    firebase_config = json.loads(st.secrets["firebase_config"])
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

def signup_user(email, password):
    try:
        email = email.strip().lower()
        user = auth.create_user(email=email, password=password)
        link = auth.generate_email_verification_link(email)
        st.session_state["verification_link"] = link
        return True
    except Exception as e:
        st.error(f"Signup error: {e}")
        return False


def login_user(email, password):
    try:
        email = email.strip().lower()
        api_key = st.secrets["firebase_web_api_key"]
        url = (
            f"https://identitytoolkit.googleapis.com/v1/"
            f"accounts:signInWithPassword?key={api_key}"
        )
        payload = {"email": email, "password": password, "returnSecureToken": True}
        res = requests.post(url, json=payload)
        data = res.json()
        st.write(data)  # Debug: see response
        if "idToken" in data:
            user_info = auth.get_user_by_email(email)
            return user_info.email_verified
        else:
            return False
    except Exception as e:
        st.error(f"Login error: {e}")
        return False
