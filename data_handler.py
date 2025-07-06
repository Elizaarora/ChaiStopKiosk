# data_handler.py
import firebase_admin
from firebase_admin import firestore
import streamlit as st

if not firebase_admin._apps:
    firebase_admin.initialize_app()

db = firestore.client()

def save_order_to_firebase(user_email, order_data):
    try:
        order = order_data.copy()
        order["user_id"] = user_email.strip().lower()
        db.collection("orders").add(order)
        st.success("Order saved!")
        return True
    except Exception as e:
        st.error(f"Error saving order: {e}")
        return False

def fetch_user_orders(user_email):
    try:
        uid = user_email.strip().lower()
        orders_ref = db.collection("orders") \
            .where("user_id", "==", uid) \
            .order_by("Time", direction=firestore.Query.DESCENDING)
        docs = orders_ref.stream()
        orders = [d.to_dict() for d in docs]
        st.write("DEBUG orders list:", orders)
        return orders
    except Exception as e:
        st.error("Unable to fetch orders (maybe missing index).")
        st.write("DEBUG fetch error:", e)
        return []
