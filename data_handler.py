import streamlit as st
import json
import firebase_admin
from firebase_admin import credentials, firestore

# ✅ Load from Streamlit secrets (NOT a file!)
if not firebase_admin._apps:
    firebase_config = json.loads(st.secrets["firebase_config"])
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

# ✅ Firestore database client
db = firestore.client()

# ------------------------------
# Save Order to Firebase Firestore
# ------------------------------
def save_order_to_firebase(user_email, order_data):
    try:
        doc_ref = db.collection("orders").document()
        doc_ref.set({
            "email": user_email,
            "order": order_data,
            "timestamp": firestore.SERVER_TIMESTAMP
        })
    except Exception as e:
        st.error(f"Error saving order: {e}")

# ------------------------------
# Fetch Order History
# ------------------------------
def fetch_user_orders(user_email):
    try:
        orders_ref = db.collection("orders").where("email", "==", user_email).order_by("timestamp", direction=firestore.Query.DESCENDING)
        orders = orders_ref.stream()
        return [order.to_dict() for order in orders]
    except Exception as e:
        st.error(f"Error fetching orders: {e}")
        return []
