import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import plotly.express as px
from PIL import Image
import io
import hashlib

# Initialize database
def init_db():
    conn = sqlite3.connect('workouts.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY,
                  username TEXT UNIQUE,
                  password_hash TEXT)''')
    
    # Workouts table
    c.execute('''CREATE TABLE IF NOT EXISTS workouts
                 (id INTEGER PRIMARY KEY,
                  user_id INTEGER,
                  date TEXT,
                  day_name TEXT,
                  exercise TEXT,
                  sets INTEGER,
                  reps INTEGER,
                  weight REAL,
                  duration INTEGER,
                  intensity TEXT,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    # Nutrition table
    c.execute('''CREATE TABLE IF NOT EXISTS nutrition
                 (id INTEGER PRIMARY KEY,
                  user_id INTEGER,
                  date TEXT,
                  meal_type TEXT,
                  meal_time TEXT,
                  protein REAL,
                  carbs REAL,
                  fat REAL,
                  notes TEXT,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    # Body measurements
    c.execute('''CREATE TABLE IF NOT EXISTS body_measurements
                 (id INTEGER PRIMARY KEY,
                  user_id INTEGER,
                  date TEXT,
                  weight REAL,
                  chest REAL,
                  waist REAL,
                  hips REAL,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    # Progress photos
    c.execute('''CREATE TABLE IF NOT EXISTS progress_photos
                 (id INTEGER PRIMARY KEY,
                  user_id INTEGER,
                  date TEXT,
                  image BLOB,
                  notes TEXT,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    conn.commit()
    conn.close()

init_db()

# Authentication functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Session state
if "user" not in st.session_state:
    st.session_state.user = None
if "username" not in st.session_state:
    st.session_state.username = None

# Login/Register Page
def auth_page():
    st.title("Login / Register")
    choice = st.radio("Choose", ["Login", "Register"], horizontal=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Submit"):
        conn = sqlite3.connect('workouts.db')
        c = conn.cursor()
        if choice == "Register":
            hashed_pw = hash_password(password)
            try:
                c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed_pw))
                conn.commit()
                st.success("Account created! Please login.")
            except sqlite3.IntegrityError:
                st.error("Username already exists!")
        else:
            c.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
            user = c.fetchone()
            if user and user[1] == hash_password(password):
                st.session_state.user = user[0]
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid credentials!")
        conn.close()

# Restrict access if not logged in
if not st.session_state.user:
    auth_page()
    st.stop()

# Main App
st.set_page_config(page_title="Recomp Tracker Pro", layout="wide")
st.title(f"Welcome, {st.session_state.username}!")

# Sidebar
page = st.sidebar.selectbox("Menu", ["Workout Log", "Nutrition Log", "Body Measurements", "Progress Photos", "Progress Dashboard"])
if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.session_state.username = None
    st.rerun()

conn = sqlite3.connect('workouts.db')

# --- Workout Logging ---
if page == "Workout Log":
    st.header("🏋️ Log Workout")
    
    workout_plan_exercises = {
        "Full-Body Strength": ["Barbell Back Squats", "Bench Press", "Bent-Over Barbell Rows", "Overhead Press", "Plank"],
        "HIIT Cardio": ["Sprint Intervals", "Incline Treadmill Sprints", "Bike Sprints"],
        "Upper Body Hypertrophy": ["Incline Dumbbell Press", "Pull-Ups/Lat Pulldowns", "Dumbbell Flyes", "Single-Arm Dumbbell Rows", "Lateral Raises"],
        "Lower Body Power": ["Deadlifts", "Walking Lunges", "Leg Press", "Farmers Carry", "Hanging Leg Raises"],
        "Metabolic Circuit": ["Kettlebell Swings", "Push-Ups", "Dumbbell Step-Ups", "TRX Rows", "Mountain Climbers"],
        "Steady-State Cardio": ["Incline Treadmill Walk", "Cycling", "Rowing"]
    }
    
    cardio_days = ["HIIT Cardio", "Steady-State Cardio"]
    day_options = list(workout_plan_exercises.keys())
    
    selected_day = st.selectbox("Select Day Type", day_options)
    exercise = st.selectbox("Exercise", workout_plan_exercises[selected_day])
    
    if selected_day in cardio_days:
        duration = st.number_input("Duration (minutes)", min_value=1, value=20)
        intensity = st.selectbox("Intensity Level", ["Low", "Moderate", "High"])
        sets = reps = weight = None
    else:
        sets = st.number_input("Sets", min_value=1, value=4)
        reps = st.number_input("Reps", min_value=1, value=8)
        weight = st.number_input("Weight (kg)", min_value=0.0, value=20.0)
        duration = intensity = None
    
    if st.button("Save Workout"):
        today = datetime.now().strftime("%Y-%m-%d")
        conn.execute('''INSERT INTO workouts 
                     (user_id, date, day_name, exercise, sets, reps, weight, duration, intensity)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (st.session_state.user, today, selected_day, exercise, sets, reps, weight, duration, intensity))
        conn.commit()
        st.success("✅ Workout saved!")

# --- Nutrition Logging ---
elif page == "Nutrition Log":
    st.header("🍎 Log Meal")
    
    meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
    meal_time = st.time_input("Time", datetime.now().time())
    protein = st.number_input("Protein (g)", min_value=0, value=30)
    carbs = st.number_input("Carbs (g)", min_value=0, value=40)
    fat = st.number_input("Fat (g)", min_value=0, value=15)
    notes = st.text_input("Meal Description (e.g., 'Grilled chicken with rice')")
    
    if st.button("Save Meal"):
        today = datetime.now().strftime("%Y-%m-%d")
        conn.execute('''INSERT INTO nutrition 
                     (user_id, date, meal_type, meal_time, protein, carbs, fat, notes)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                     (st.session_state.user, today, meal_type, str(meal_time), protein, carbs, fat, notes))
        conn.commit()
        st.success("✅ Meal saved!")

# --- Body Measurements ---
elif page == "Body Measurements":
    st.header("📏 Body Measurements")
    
    weight = st.number_input("Weight (kg)", min_value=0.0)
    chest = st.number_input("Chest (cm)", min_value=0.0)
    waist = st.number_input("Waist (cm)", min_value=0.0)
    hips = st.number_input("Hips (cm)", min_value=0.0)
    
    if st.button("Save Measurements"):
        today = datetime.now().strftime("%Y-%m-%d")
        conn.execute('''INSERT INTO body_measurements 
                     (user_id, date, weight, chest, waist, hips)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                     (st.session_state.user, today, weight, chest, waist, hips))
        conn.commit()
        st.success("✅ Measurements saved!")
    
    st.subheader("Progress Over Time")
    measurements_df = pd.read_sql_query(
        "SELECT date, weight, chest, waist, hips FROM body_measurements WHERE user_id = ?",
        conn, params=(st.session_state.user,)
    )
    if not measurements_df.empty:
        fig = px.line(measurements_df, x='date', y=['weight', 'chest', 'waist', 'hips'])
        st.plotly_chart(fig)
    else:
        st.warning("No measurements recorded yet")

# --- Progress Photos ---
elif page == "Progress Photos":
    st.header("📸 Progress Photos")
    
    uploaded_file = st.file_uploader("Upload Photo (JPEG/PNG)", type=["jpg", "jpeg", "png"])
    notes = st.text_area("Photo Notes")
    
    if uploaded_file and st.button("Save Photo"):
        today = datetime.now().strftime("%Y-%m-%d")
        image_bytes = uploaded_file.read()
        conn.execute('''INSERT INTO progress_photos (user_id, date, image, notes)
                     VALUES (?, ?, ?, ?)''',
                     (st.session_state.user, today, image_bytes, notes))
        conn.commit()
        st.success("✅ Photo saved!")
    
    st.subheader("Your Photos")
    photos = conn.execute("SELECT date, notes FROM progress_photos WHERE user_id = ? ORDER BY date DESC", (st.session_state.user,)).fetchall()
    for date, note in photos:
        st.write(f"**{date}**: {note}")
        photo_data = conn.execute("SELECT image FROM progress_photos WHERE date = ? AND user_id = ?", (date, st.session_state.user)).fetchone()[0]
        st.image(Image.open(io.BytesIO(photo_data)), width=300)
        st.write("---")

# --- Progress Dashboard ---
elif page == "Progress Dashboard":
    st.header("📈 Progress Dashboard")
    
    # Workout Progress
    st.subheader("🏋️ Workout History")
    workout_df = pd.read_sql_query("SELECT * FROM workouts WHERE user_id = ?", conn, params=(st.session_state.user,))
    
    if not workout_df.empty:
        exercise_list = workout_df['exercise'].unique()
        selected_exercise = st.selectbox("Select Exercise", exercise_list)
        exercise_df = workout_df[workout_df['exercise'] == selected_exercise]
        
        fig = px.line(exercise_df, x='date', y='weight', 
                     title=f"{selected_exercise} Weight Progression",
                     markers=True)
        st.plotly_chart(fig)
        
        st.dataframe(workout_df)
    else:
        st.warning("No workout data yet")
    
    # Nutrition Progress
    st.subheader("🍎 Nutrition Summary")
    nutrition_df = pd.read_sql_query("SELECT * FROM nutrition WHERE user_id = ?", conn, params=(st.session_state.user,))
    
    if not nutrition_df.empty:
        nutrition_df['date'] = pd.to_datetime(nutrition_df['date'])
        daily_totals = nutrition_df.groupby('date')[['protein', 'carbs', 'fat']].sum().reset_index()
        
        fig = px.line(daily_totals, x='date', y=['protein', 'carbs', 'fat'],
                     title="Daily Macro Trends")
        st.plotly_chart(fig)
        
        st.dataframe(nutrition_df)
    else:
        st.warning("No nutrition data yet")

conn.close()