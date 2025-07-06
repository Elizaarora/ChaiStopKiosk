


# app.py
import streamlit as st
from datetime import datetime
import random
import pandas as pd

from firebase_auth import signup_user, login_user
from data_handler import save_order_to_firebase, fetch_user_orders
from ml_model import recommend_chai

st.set_page_config(page_title="ChaiStopKiosk", layout="wide")

# ------------------ Session State ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "page" not in st.session_state:
    st.session_state.page = "landing"

# ------------------ CSS ------------------
st.markdown("""
    <style>
    html, body {
        background-color: #fff5e6;
        margin: 0;
        padding: 0;
    }

    .landing {
        background-color: #fff8ec;
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem auto;
        text-align: center;
        max-width: 90vw;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    .heading {
        font-size: 3.2rem;
        font-weight: 900;
        color: #2f1b0c;
        margin-bottom: 0.5rem;
    }

    .sub-heading {
        font-size: 2.5rem;
        color: #f4a300;
        font-weight: 800;
    }

    .desc {
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
        color: #6a4f3c;
        max-width: 500px;
    }

    .custom-btn {
        background: linear-gradient(to right, #ffc371, #ff5f6d);
        border: none;
        border-radius: 25px;
        padding: 1rem 2rem;
        color: black;
        font-weight: bold;
        font-size: 1.2rem;
    }

    .emoji-suggestion {
        background: #fff1da;
        border-radius: 12px;
        padding: 0.75rem;
        font-size: 1rem;
        margin-bottom: 10px;
        color: #333;
        max-width: 90%;
        margin-left: auto;
        margin-right: auto;
    }

    img {
        max-width: 90%;
        height: auto;
        border-radius: 10px;
        margin-top: 1rem;
    }

    @media screen and (max-width: 768px) {
        .heading {
            font-size: 2.5rem;
        }

        .sub-heading {
            font-size: 2rem;
        }

        .desc {
            font-size: 1rem;
        }
    }
    </style>
""", unsafe_allow_html=True)


# ------------------ LANDING PAGE ------------------
def show_landing():
    st.markdown("""
        <div class='landing'>
            <div class='heading'>ChaiStop <span class='sub-heading'>Kiosk</span></div>
            <p class='desc'>Let's dive in the essence of authentic Indian Masala chai, a desi way to brighten your mood.</p>
            <img src='https://cdn.shopify.com/s/files/1/1980/1825/files/uptown-tea-shop-tea-talk-all-about-chai.jpg?v=1698672089' width='400'>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🫥 Order now", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()

    st.markdown("### 🥽 What are you feeling today?")
    suggestions = [
        "🢪 Had a bad day? Have a kadak masala chai",
        "😡 Pissed off by the landlord? Have an adrak chai",
        "🤨 Nervous about the presentation? Have Elaichi chai",
        "🤭 Still cannot figure out? Have Sulaimani chai",
    ]
    for s in suggestions:
        st.markdown(f"<div class='emoji-suggestion'>{s}</div>", unsafe_allow_html=True)

    if st.button("Sign in / Register"):
        st.session_state.page = "login"
        st.rerun()

# ------------------ LOGIN ------------------
def show_login():
    st.title("🔐 Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if login_user(email, password):
            st.session_state.logged_in = True
            st.session_state.user_email = email.strip().lower()
            st.session_state.page = "dashboard"
            st.rerun()
        else:
            st.error("Invalid credentials or email not verified")

    if st.button("Go to Sign Up"):
        st.session_state.page = "signup"
        st.rerun()

# ------------------ SIGNUP ------------------
# ------------------ SIGNUP ------------------
def show_signup():
    st.title("🌟 Create Account")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        success = signup_user(email.strip().lower(), password)
        if success:
            st.success("User created successfully! ✅")
            st.warning("⚠️ Please verify your email before logging in.")
            link = st.session_state.get("verification_link")
            if link:
                st.markdown(f"[Click here to verify email]({link})", unsafe_allow_html=True)
            else:
                st.info("Verification link not available. Please try logging in and checking your inbox.")
        else:
            st.error("Signup failed. Please try again.")

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()


# ------------------ DASHBOARD ------------------
def show_dashboard():
    st.sidebar.title("📂 Dashboard")
    section = st.sidebar.radio("Navigate", ["Order", "Process", "Flavours", "Places", "History", "Logout"])

    if section == "Order":
        show_order_page()
    elif section == "Process":
        st.title("🔧 Chai Brewing Process")
        st.write("1. Heat water \n2. Add spices \n3. Boil with tea leaves \n4. Add milk & sugar \n5. Strain & serve")
    elif section == "Flavours":
        st.title("🌿 Chai Flavours")
        st.write("Masala, Adrak, Elaichi, Sulaimani, Tulsi")
    elif section == "Places":
        st.title("🌎 Popular Chai Places")
        st.write("Cutting Chai Mumbai, Sharma Chai Lucknow, Tapri Jaipur, Chai Sutta Bar")
    elif section == "History":
        show_order_history()
    elif section == "Logout":
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.page = "landing"
        st.rerun()

# ------------------ ORDER PAGE ------------------
def show_order_page():
    st.title("🍵 Customize Your Chai")
    name = st.text_input("Your Name")
    base = st.selectbox("Base", ["Milk", "Almond Milk", "Water"])
    flavor = st.radio("Flavor", ["Plain", "Ginger (Adrak)", "Elaichi", "Masala"])
    sugar = st.slider("Sugar (spoons)", 0, 5, 2)
    strength = st.select_slider("Strength", ["Light", "Medium", "Strong"])
    masala = st.toggle("Extra Masala?")
    cups = st.number_input("Cups", 1, 10, 1)
    snacks = st.multiselect("Snacks", ["Samosa", "Rusk", "Kachori", "Biscuits"])
    contact = st.text_input("Phone / Email")
    special = st.text_area("Special instructions")
    payment = st.radio("Payment", ["UPI", "Cash", "Card"])

    if st.button("✅ Place Order"):
        token = random.randint(1000, 9999)
        summary = {
            "user_id": st.session_state.user_email,
            "Name": name,
            "Contact": contact,
            "Base": base,
            "Flavor": flavor,
            "Sugar": sugar,
            "Strength": strength,
            "Masala": masala,
            "Cups": cups,
            "Snacks": ", ".join(snacks),
            "Special": special,
            "Payment": payment,
            "Token": token,
            "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_order_to_firebase(st.session_state.user_email, summary)
        st.success(f"Your order token is #{token}")
        st.balloons()

# ------------------ ORDER HISTORY ------------------
def show_order_history():
    st.title("📅 Order History")

    email = st.session_state.user_email.strip().lower()
    st.write("🔍 Logged in as:", email)

    orders = fetch_user_orders(email)
    st.write("📆 Orders fetched:", orders)

    if not orders:
        st.info("No past orders found.")
    else:
        for order in orders[::-1]:
            with st.expander(f"Order on {order.get('Time')}"):
                for k, v in order.items():
                    st.markdown(f"**{k}**: {v}")

# ------------------ ROUTER ------------------
if st.session_state.logged_in:
    show_dashboard()
else:
    if st.session_state.page == "landing":
        show_landing()
    elif st.session_state.page == "login":
        show_login()
    elif st.session_state.page == "signup":
        show_signup()
