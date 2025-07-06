import firebase_admin
from firebase_admin import firestore
import streamlit as st

# ✅ Initialize Firebase Firestore
if not firebase_admin._apps:
    firebase_admin.initialize_app()

db = firestore.client()

# ✅ Save order to Firestore
def save_order_to_firebase(user_email, summary):
    try:
        # Normalize email
        summary["user_id"] = user_email.strip().lower()

        # Save to Firestore
        db.collection("orders").add(summary)
        return True
    except Exception as e:
        print("❌ Error saving order:", e)
        return False

# ✅ Fetch user's past orders
def fetch_user_orders(user_email):
    try:
        user_id = user_email.strip().lower()
        orders_ref = db.collection("orders") \
            .where("user_id", "==", user_id) \
            .order_by("timestamp", direction=firestore.Query.DESCENDING)

        docs = orders_ref.stream()
        orders = [doc.to_dict() for doc in docs]

        print("📦 Orders fetched:", orders)
        return orders
    except Exception as e:
        print("❌ Firestore query failed:", e)
        st.info("📦 No past orders found (or index still being created).")
        return []
