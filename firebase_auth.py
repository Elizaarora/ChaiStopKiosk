import requests
import firebase_admin
from firebase_admin import credentials, auth
import json
import streamlit as st

# ✅ Initialize Firebase only once
if not firebase_admin._apps:
    firebase_config = json.loads(st.secrets["firebase_config"])
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

# ✅ SIGNUP FUNCTION
def signup_user(email, password):
    try:
        # Create user
        user = auth.create_user(email=email, password=password)

        # Generate verification link
        verification_link = auth.generate_email_verification_link(email)

        # Show it on the screen
        st.success("✅ User created successfully!")
        st.warning("⚠️ You must verify your email before logging in.")
        st.info(f"🔗 Click to verify your email: [Verify Email]({verification_link})")

        return True
    except Exception as e:
        st.error(f"❌ Signup failed: {e}")
        return False


# ✅ LOGIN FUNCTION (using Firebase REST API)
def login_user(email, password):
    try:
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
            # ✅ Logged in successfully
            user_info = auth.get_user_by_email(email)
            if not user_info.email_verified:
                st.warning("⚠️ Please verify your email before logging in.")
                return False
            return True
        else:
            error_msg = data.get("error", {}).get("message", "Unknown error")
            st.error(f"❌ Login failed: {error_msg}")
            return False
    except Exception as e:
        st.error(f"❌ Login error: {e}")
        return False
