import streamlit as st
import pickle
import numpy as np
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime

st.set_page_config(
    page_title="Ride Duration Prediction System",
    page_icon="🚕",
    layout="wide"
)

model = pickle.load(open("models/model.pkl", "rb"))

# ---------------- DATABASE ----------------

conn = sqlite3.connect("ride_predictions.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    password TEXT,
    role TEXT,
    created_at TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    passenger_count INTEGER,
    trip_distance REAL,
    pickup_hour INTEGER,
    day_type TEXT,
    prediction REAL,
    created_at TEXT
)
""")

conn.commit()
# Add username column if old table does not have it
try:
    cursor.execute("ALTER TABLE predictions ADD COLUMN username TEXT")
    conn.commit()
except sqlite3.OperationalError:
    pass

# ---------------- AUTH FUNCTIONS ----------------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, email, password, role):
    try:
        cursor.execute("""
        INSERT INTO users (username, email, password, role, created_at)
        VALUES (?, ?, ?, ?, ?)
        """, (
            username,
            email,
            hash_password(password),
            role,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        return True
    except:
        return False

def login_user(username, password):
    cursor.execute("""
    SELECT username, role FROM users
    WHERE username = ? AND password = ?
    """, (
        username,
        hash_password(password)
    ))
    return cursor.fetchone()

def save_prediction(username, passenger_count, trip_distance, pickup_hour, day_type, prediction):
    cursor.execute("""
    INSERT INTO predictions (
        username, passenger_count, trip_distance, pickup_hour, day_type, prediction, created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        username,
        passenger_count,
        trip_distance,
        pickup_hour,
        day_type,
        prediction,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()

def get_predictions(username=None):
    if username:
        return pd.read_sql_query(
            "SELECT * FROM predictions WHERE username = ? ORDER BY id DESC",
            conn,
            params=(username,)
        )
    return pd.read_sql_query(
        "SELECT * FROM predictions ORDER BY id DESC",
        conn
    )

def delete_prediction(prediction_id, username):
    cursor.execute(
        "DELETE FROM predictions WHERE id = ? AND username = ?",
        (prediction_id, username)
    )
    conn.commit()

# ---------------- SESSION ----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "role" not in st.session_state:
    st.session_state.role = ""

# ---------------- CSS ----------------

st.markdown("""
<style>
.stApp {
    background: #0f1218;
    color: white;
}

[data-testid="stSidebar"] {
    background: #121720;
    border-right: 1px solid #263241;
}

h1, h2, h3, h4, h5, p, label {
    color: white !important;
}

.card {
    background: #1e293b;
    border-radius: 18px;
    padding: 35px;
    border: 1px solid #222b36;
    box-shadow: 0 0 20px rgba(0,0,0,0.25);
}

.metric-card {
    background: #171c23;
    border-radius: 16px;
    padding: 20px;
    border-left: 3px solid #38bdf8;
}

.big-card {
    background: #171c23;
    border-radius: 20px;
    padding: 45px 30px;
    text-align: center;
    border: 1px solid #222b36;
}

.small-blue {
    color: #38bdf8;
    font-weight: 800;
    letter-spacing: 1px;
}

.stButton>button {
    background: #ef3038;
    color: white;
    border: none;
    border-radius: 14px;
    height: 55px;
    width: 100%;
    font-size: 18px;
    font-weight: 800;
}

.stButton>button:hover {
    background: #ff4148;
    color: white;
}

[data-testid="stMetricValue"] {
    color: #38bdf8;
    font-size: 38px;
}

.footer {
    color: #9ca3af;
    font-size: 13px;
    border-top: 1px solid #263241;
    padding-top: 15px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN / REGISTER ----------------

if not st.session_state.logged_in:

    st.markdown("""
    <h1 style="text-align:center;color:#38bdf8;">🚕 Ride Duration Prediction System</h1>
    <p style="text-align:center;">Login or register to access the dashboard</p>
    <hr>
    """, unsafe_allow_html=True)

    auth_page = st.sidebar.radio("Account", ["Login", "Register"])

    if auth_page == "Login":

        st.title("Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = login_user(username, password)

            if user:
                st.session_state.logged_in = True
                st.session_state.username = user[0]
                st.session_state.role = user[1]
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")

    elif auth_page == "Register":

        st.title("Register")

        username = st.text_input("Create Username")
        email = st.text_input("Email")
        password = st.text_input("Create Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        role = st.selectbox("User Role", ["Driver", "Analyst", "Admin"])

        if st.button("Register"):
            if password != confirm_password:
                st.error("Passwords do not match")
            elif username == "" or email == "" or password == "":
                st.error("Please fill all fields")
            else:
                success = register_user(username, email, password, role)

                if success:
                    st.success("Registration successful. Please login.")
                else:
                    st.error("Username or email already exists")

    st.stop()

# ---------------- SIDEBAR ----------------

st.sidebar.markdown("## 💠 Ride AI")
st.sidebar.success(f"Logged in as: {st.session_state.username}")
st.sidebar.info(f"Role: {st.session_state.role}")

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Predict",
        "Analytics",
        "Prediction History",
        "About"
    ]
)

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.rerun()

# ---------------- HEADER ----------------

st.markdown("""
<h2 style="color:#38bdf8;">💠 Ride Duration Prediction System</h2>
<p>Home > Dashboard</p>
<hr>
""", unsafe_allow_html=True)

# ---------------- OVERVIEW ----------------

if page == "Overview":

    st.title("Overview Dashboard")

    history_df = get_predictions(st.session_state.username)

    total_predictions = len(history_df)

    if total_predictions > 0:
        avg_prediction = history_df["prediction"].mean()
        avg_distance = history_df["trip_distance"].mean()
    else:
        avg_prediction = 0
        avg_distance = 0

    m1, m2, m3 = st.columns(3)

    with m1:
        st.markdown(f"""
        <div class="metric-card">
        <p class="small-blue">TOTAL PREDICTIONS</p>
        <h2>{total_predictions}</h2>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="metric-card">
        <p class="small-blue">AVG PREDICTED DURATION</p>
        <h2>{avg_prediction:.2f} min</h2>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
        <div class="metric-card">
        <p class="small-blue">AVG TRIP DISTANCE</p>
        <h2>{avg_distance:.2f} mi</h2>
        </div>
        """, unsafe_allow_html=True)

    if total_predictions > 0:
        chart_df = history_df.groupby("pickup_hour")["prediction"].mean().reset_index()
        chart_df.columns = ["Pickup Hour", "Average Prediction"]

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Average Prediction by Pickup Hour")
        st.line_chart(chart_df, x="Pickup Hour", y="Average Prediction")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No predictions yet. Go to Predict page and run a prediction.")

# ---------------- PREDICT ----------------

elif page == "Predict":

    left, right = st.columns([1, 2.2])

    with left:

        st.markdown("## Prediction Inputs ⚡")
        st.caption("MODEL LR-NYC-V1.0")

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<p class="small-blue">👥 PASSENGER COUNT</p>', unsafe_allow_html=True)

        passenger_count = st.radio(
            "Passenger Count",
            [1, 2, 3, 4, 5, 6],
            horizontal=True,
            label_visibility="collapsed"
        )

        st.markdown('</div>', unsafe_allow_html=True)
        st.write("")

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<p class="small-blue">✈️ TRIP DISTANCE</p>', unsafe_allow_html=True)

        trip_distance = st.number_input(
            "Trip Distance",
            min_value=0.1,
            value=3.45,
            step=0.1,
            label_visibility="collapsed"
        )

        st.markdown('</div>', unsafe_allow_html=True)
        st.write("")

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<p class="small-blue">🕒 PICKUP HOUR</p>', unsafe_allow_html=True)

        pickup_hour = st.slider(
            "Pickup Hour",
            0,
            23,
            14,
            label_visibility="collapsed"
        )

        st.markdown(
            f"<h2 style='color:#38bdf8;'>{pickup_hour}:00</h2>",
            unsafe_allow_html=True
        )

        st.markdown('</div>', unsafe_allow_html=True)
        st.write("")

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<p class="small-blue">📅 DAY TYPE</p>', unsafe_allow_html=True)

        day_type = st.selectbox("Day Type", ["Weekday", "Weekend"])
        is_weekend = 1 if day_type == "Weekend" else 0

        st.markdown('</div>', unsafe_allow_html=True)
        st.write("")

        predict_btn = st.button("⚡ Run Prediction")

    with right:

        if predict_btn:

            features = np.array([[
                passenger_count,
                trip_distance,
                pickup_hour,
                is_weekend
            ]])

            prediction = model.predict(features)[0]

            save_prediction(
                st.session_state.username,
                passenger_count,
                trip_distance,
                pickup_hour,
                day_type,
                prediction
            )

            st.markdown('<div class="card">', unsafe_allow_html=True)

            st.markdown('<p class="small-blue">⚡ AI PREDICTION READY</p>', unsafe_allow_html=True)

            st.metric(
                "Estimated Trip Duration",
                f"{prediction:.2f} min"
            )

            if prediction < 15:
                st.success("Short Trip 🚕")
            elif prediction < 40:
                st.warning("Medium Trip 🚖")
            else:
                st.error("Long Trip 🚗")

            st.success("Prediction saved to database successfully!")

            st.markdown('</div>', unsafe_allow_html=True)

        else:

            st.markdown('<div class="big-card">', unsafe_allow_html=True)

            st.markdown("""
            <div style="font-size:90px;">🚕</div>
            <h1>AWAITING PARAMETERS</h1>
            <p>
            Adjust the trip features in the left panel and click
            <span style="color:#ef3038;font-weight:800;">Run Prediction</span>
            to generate a duration estimate.
            </p>
            <br>
            <h3 style="color:#6b7280;">--.-- minutes</h3>
            """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

# ---------------- ANALYTICS ----------------

elif page == "Analytics":

    st.title("Ride Analytics Center")

    history_df = get_predictions(st.session_state.username)

    if history_df.empty:
        st.info("No database predictions yet. Run predictions first.")
    else:
        total = len(history_df)
        avg_pred = history_df["prediction"].mean()
        max_pred = history_df["prediction"].max()
        min_pred = history_df["prediction"].min()

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric("Total Records", total)

        with c2:
            st.metric("Average Prediction", f"{avg_pred:.2f} min")

        with c3:
            st.metric("Highest Prediction", f"{max_pred:.2f} min")

        with c4:
            st.metric("Lowest Prediction", f"{min_pred:.2f} min")

        hour_df = history_df.groupby("pickup_hour")["prediction"].mean().reset_index()
        hour_df.columns = ["Pickup Hour", "Average Duration"]

        day_df = history_df.groupby("day_type")["prediction"].mean().reset_index()
        day_df.columns = ["Day Type", "Average Duration"]

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Average Prediction by Pickup Hour")
            st.area_chart(hour_df, x="Pickup Hour", y="Average Duration")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Average Prediction by Day Type")
            st.bar_chart(day_df, x="Day Type", y="Average Duration")
            st.markdown('</div>', unsafe_allow_html=True)

# ---------------- HISTORY ----------------

elif page == "Prediction History":

    st.title("Prediction History")

    history_df = get_predictions(st.session_state.username)

    if history_df.empty:
        st.info("No predictions saved yet.")
    else:
        search_text = st.text_input("Search by Day Type or Date")

        filtered_df = history_df.copy()

        if search_text:
            filtered_df = filtered_df[
                filtered_df["day_type"].astype(str).str.contains(search_text, case=False, na=False) |
                filtered_df["created_at"].astype(str).str.contains(search_text, case=False, na=False)
            ]

        st.dataframe(filtered_df, use_container_width=True)

        csv = filtered_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download Prediction History CSV",
            data=csv,
            file_name="prediction_history.csv",
            mime="text/csv"
        )

        st.subheader("Delete Prediction Record")

        delete_id = st.number_input(
            "Enter Prediction ID to Delete",
            min_value=1,
            step=1
        )

        if st.button("Delete Record"):
            delete_prediction(delete_id, st.session_state.username)
            st.success(f"Prediction ID {delete_id} deleted successfully.")
            st.rerun()

# ---------------- ABOUT ----------------

elif page == "About":

    st.title("About Project")

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.write("""
    ## Ride Duration Prediction System

    This project predicts NYC taxi ride duration using Machine Learning.

    ### Main Users
    - Drivers
    - Transport Analysts
    - Ride-hailing Companies
    - Data Science Students

    ### Technologies Used
    - Python
    - Pandas
    - NumPy
    - Scikit-learn
    - Streamlit
    - SQLite Database
    - Password Hashing

    ### Features
    - Register
    - Login
    - Logout
    - Real-time Prediction
    - Save Predictions
    - View Prediction History
    - Search Predictions
    - Delete Predictions
    - Download CSV
    - User-wise Analytics
    """)

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- FOOTER ----------------

st.markdown("""
<div class="footer">
POWERED BY:
Python | Pandas | Scikit-learn | Streamlit | SQLite
<br>
© 2026 RideDuration AI. NYC OpenData.
</div>
""", unsafe_allow_html=True)