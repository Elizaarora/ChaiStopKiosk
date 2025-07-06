import firebase_admin
from firebase_admin import firestore
import streamlit as st

# ✅ Reuse existing Firebase app instance
if not firebase_admin._apps:
    firebase_admin.initialize_app()

# ✅ Initialize Firestore DB
db = firestore.client()

# ✅ Save an order to Firestore
def save_order_to_firebase(user_id, chai_type, sweetness, milk_type, timestamp):
    try:
        order_data = {
            "user_id": user_id,
            "chai_type": chai_type,
            "sweetness": sweetness,
            "milk_type": milk_type,
            "timestamp": timestamp
        }
        db.collection("orders").add(order_data)
        return True
    except Exception as e:
        print("❌ Error saving order:", e)
        return False

# ✅ Fetch past orders for a user (safe version)
def fetch_user_orders(user_id):
    try:
        # This query needs a composite index: (user_id + timestamp)
        orders_ref = db.collection("orders") \
            .where("user_id", "==", user_id) \
            .order_by("timestamp", direction=firestore.Query.DESCENDING)

        docs = orders_ref.stream()
        return [doc.to_dict() for doc in docs]

    except Exception as e:
        # Log actual error for developer
        print("❌ Firestore query failed:", e)

        # Show friendly info message to user
        st.info("📦 No past orders found (or database index is still being created).")

        # Return empty safely
        return []
