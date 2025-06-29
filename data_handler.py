import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("firebase_config.json")
try:
    firebase_admin.initialize_app(cred)
except:
    pass

db = firestore.client()

def save_order_to_firebase(user_email, order_data):
    try:
        db.collection("orders").document(user_email).collection("user_orders").add(order_data)
        return True
    except Exception as e:
        print(e)
        return False

def fetch_user_orders(user_email):
    try:
        docs = db.collection("orders").document(user_email).collection("user_orders").stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        print(e)
        return []
