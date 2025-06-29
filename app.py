import streamlit as st
from datetime import datetime
import random
import pandas as pd

from firebase_auth import signup_user, login_user
from data_handler import save_order_to_firebase, fetch_user_orders

from ml_model import recommend_chai

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="Smart ChaiBot",
    page_icon="🫖",
    layout="wide"
)

# ------------------ SESSION STATE ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "page" not in st.session_state:
    st.session_state.page = "login"

# ------------------ AUTH PAGES ------------------
def show_login():
    st.title("🔐 Login to Smart ChaiBot")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if login_user(email, password):
            st.session_state.logged_in = True
            st.session_state.user_email = email
        else:
            st.error("Invalid email or password.")

    if st.button("Go to Sign Up"):
        st.session_state.page = "signup"

def show_signup():
    st.title("🆕 Create an Account")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        result = signup_user(email, password)
        if "successfully" in result:
            st.success(result)
            st.session_state.page = "login"
        else:
            st.error(result)

    if st.button("Back to Login"):
        st.session_state.page = "login"

# ------------------ MAIN ORDER PAGE ------------------
def show_order_page():
    st.markdown(f"### Welcome, `{st.session_state.user_email}` ☕")
    st.markdown("##### Customize and place your perfect chai order below")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Your Name")
        contact = st.text_input("Phone or Email")
    with col2:
        base = st.selectbox("Chai Base", ["Milk", "Almond Milk", "Water"])
        flavor = st.radio("Flavor", ["Plain", "Ginger (Adrak)", "Elaichi", "Masala"])
        sugar = st.slider("Sugar (spoons)", 0, 5, 2)

    strength = st.select_slider("Strength Level", ["Light", "Medium", "Strong"])
    masala = st.toggle("Add Extra Masala?")
    cups = st.number_input("No. of Cups", 1, 10, 1)
    snacks = st.multiselect("Snacks with your Chai?", ["Samosa", "Kachori", "Rusk", "Biscuits", "Mathri"])
    special = st.text_area("Special Instructions")
    payment = st.radio("Payment Mode", ["UPI", "Card", "Cash"])

     # 🧠 ML-based recommendation
    user_input = {
        "Base": base,
        "Flavor": flavor,
        "Strength": strength,
        "Sugar": sugar,
        "Masala": "Yes" if masala else "No"
                }

    try:
        recommended_index = recommend_chai(user_input)
        recommendations = [
            "Masala Chai with Strong Milk",
            "Plain Ginger Chai with Almond Milk",
            "Elaichi Chai with 3 sugars",
            "Light Adrak Chai with no sugar",
            "Medium Masala Chai with Rusk"
        ]

        st.markdown("🎯 **You may also like:**")
        st.success(f"{recommendations[recommended_index]}")
    except Exception as e:
        st.warning("⚠️ Could not generate recommendation. Please try again.")
        st.text(str(e))
   

    if st.button("✅ Place Order"):
        token = random.randint(1000, 9999)
        wait_time = 5 + cups

        st.success(f"Your order token is #{token}. Ready in ~{wait_time} mins.")
        st.balloons()

        summary = {
            "Name": name,
            "Contact": contact,
            "Base": base,
            "Flavor": flavor,
            "Sugar": sugar,
            "Strength": strength,
            "Masala": "Yes" if masala else "No",
            "Cups": cups,
            "Snacks": ", ".join(snacks) if snacks else "None",
            "Special": special,
            "Payment": payment,
            "Token": token,
            "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Email": st.session_state.user_email
        }

        saved = save_order_to_firebase(st.session_state.user_email, summary)
        if saved:
            st.success("Order saved to database!")
        else:
            st.warning("Could not save order to Firebase.")

        df = pd.DataFrame([summary])
        st.dataframe(df)

        receipt = "\n".join([f"{k}: {v}" for k, v in summary.items()])
        st.download_button("📄 Download Receipt", receipt, file_name="chai_order.txt")

# ------------------ ORDER HISTORY ------------------
def show_order_history():
    st.markdown("### 📜 Your Order History")
    orders = fetch_user_orders(st.session_state.user_email)

    if not orders:
        st.warning("No previous orders found.")
    else:
        for i, order in enumerate(orders[::-1], start=1):  # Show latest first
            with st.expander(f"📦 Order #{i} - {order.get('Time', 'N/A')}"):
                for k, v in order.items():
                    st.markdown(f"**{k}**: {v}")

# ------------------ PAGE ROUTING ------------------
if st.session_state.logged_in:
    st.sidebar.image("https://cdn.pixabay.com/photo/2016/01/05/13/58/chai-1129942_1280.jpg", use_container_width=True)
    st.sidebar.title("📂 Navigation")
    nav = st.sidebar.radio("Go to", ["Order", "History", "Logout"])

    if nav == "Order":
        show_order_page()
    elif nav == "History":
        show_order_history()
    elif nav == "Logout":
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.page = "login"
        st.experimental_rerun()
else:
    if st.session_state.page == "login":
        show_login()
    else:
        show_signup()
