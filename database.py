import sqlite3
import hashlib

def create_tables():
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

if __name__ == "__main__":
    create_tables()