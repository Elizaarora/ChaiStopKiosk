import firebase_admin
from firebase_admin import credentials, auth

# Initialize Firebase only once
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_config.json")
    firebase_admin.initialize_app(cred)

# ✅ SIGNUP FUNCTION
def signup_user(email, password):
    try:
        user = auth.create_user(email=email, password=password)

        # Generate verification email link
        verification_link = auth.generate_email_verification_link(email)
        print("✅ Email verification link:", verification_link)

        return f"User {email} created successfully! ✅\nPlease verify your email.\n\nLink: {verification_link}"
    except Exception as e:
        return str(e)

# ✅ LOGIN FUNCTION
def login_user(email, password):
    try:
        user = auth.get_user_by_email(email)

        if not user.email_verified:
            return False  # Email not verified

        # ✅ Firebase Admin SDK can't check passwords directly!
        # So we assume the email is valid and verified.
        # Actual login (password check) is done via Firebase Client SDK in JS
        return True
    except Exception as e:
        print("Login Error:", e)
        return False
