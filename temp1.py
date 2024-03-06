import streamlit as st
import sqlite3
import cv2
import face_recognition
import numpy as np
import os
from passlib.hash import pbkdf2_sha256
import pygame

# Initialize session state variables
if "loggedin" not in st.session_state:
    st.session_state["loggedin"] = False
if "face_verified" not in st.session_state:
    st.session_state["face_verified"] = False

def main():
    if st.session_state["loggedin"]:
        if not st.session_state["face_verified"]:
            face_verification()  # Run face verification if not already verified
        else:
            mark_attendance()  # Show attendance marking options after face verification
    else:
        login()

def create_table():
    conn = sqlite3.connect('C:\\Users\\omkar\\Downloads\\VEGA.db')
    cursor = conn.cursor()


    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def new_lecture():
    st.title("Lecture Form")
    with st.form("User Information Form"):
        # Form fields
        st.header("Enter Lecture Details")
        subject_name = st.text_input("Enter Subject Name")
        lecture_start = st.time_input("Enter Lecture Start time")
        lecture_end = st.time_input("Enter Lecture End Time")
        division = st.selectbox("Enter Division", ["COMPSA", "COMPSB", "AIML", "DS", "EXTC-E", "ETRX-F"], placeholder="Select a Division")

        # Form submission
        submit_button = st.form_submit_button("Submit")

        if submit_button:
            # Update the session state to indicate that the form was submitted
            st.session_state["submitted"] = True
            # You might want to save the form data to a database or perform some action here

            # Rerun the app to reflect changes in the state
            st.experimental_rerun()

def face_verification():
    face_verified = False
    video_capture = cv2.VideoCapture(0)
    video_capture.set(3, 640)  # Width
    video_capture.set(4, 480)  # Height
    images_folder = "C:\\Users\\omkar\\OneDrive\\Desktop\\REAL TIME FACE RECO\\database"
    known_face_encodings = []
    known_face_names = []

    for filename in os.listdir(images_folder):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            name = os.path.splitext(filename)[0]
            image_path = os.path.join(images_folder, filename)
            image = face_recognition.load_image_file(image_path)
            try:
                face_encoding = face_recognition.face_encodings(image)[0]
                known_face_encodings.append(face_encoding)
                known_face_names.append(name)
            except IndexError:
                print(f"No face found in {filename}, skipping.")

    st.title("Real-Time Face Recognition")
    video_placeholder = st.empty()

    while not face_verified:
        ret, frame = video_capture.read()
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                face_verified = True
                name = known_face_names[best_match_index]
            face_names.append(name)
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)
        video_placeholder.image(frame, channels="BGR")
        if face_verified:
            st.write("Verification Successful !")
            st.session_state["face_verified"] = True
            break

    video_capture.release()
    cv2.destroyAllWindows()

def create_table_lecture(id,subjectName,startTime,endTime,division):
    conn = sqlite3.connect('C:\\Users\\omkar\\Downloads\\VEGA.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lecture(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subjectName TEXT NOT NULL,
            startTime TIME NOT NULL,
            endTime TIME NOT NULL,
            division TEXT NOT NULL
        )
    ''')
    cursor.execute("INSERT INTO lecture(id,subjectName,startTime,endTime,division) VALUES (?,?,?,?,?)",(id,subjectName,startTime,endTime,division))
    conn.commit()
    conn.close()

def mark_attendance():
    st.title("Attendance Marking")
    # Your attendance marking logic here

# Function to check if a username already exists
def username_exists(username):
    conn = sqlite3.connect('C:\\Users\\Aman\\VEGA.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user is not None

# Function to register a new user
def register_user(username, password):
    conn = sqlite3.connect('C:\\Users\\omkar\\Downloads\\VEGA.db')
    cursor = conn.cursor()
    hashed_password = pbkdf2_sha256.hash(password)
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()

# Function to authenticate a user
def authenticate_user(username, password):
    conn = sqlite3.connect('C:\\Users\\omkar\\Downloads\\VEGA.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    # unique_id=cursor.execute("SELECT teacherId from teachers where teachers.Name=?", (username_login,))
    user = cursor.fetchone()
    conn.close()

    if user is not None and pbkdf2_sha256.verify(password, user[2]):
        return True
    else:
        return False

# Create the database table
create_table()

def login():
    login_or_register = st.radio("Select an option:", ("Login", "Register"))
    if login_or_register == "Login":
        st.header("Login")
        username_login = st.text_input("Username:")
        password_login = st.text_input("Password:", type="password")
        
        if st.button("Login"):
            if authenticate_user(username_login, password_login):
                st.session_state["loggedin"] = True
                st.experimental_rerun()
            else:
                st.error("Invalid username or password. Please try again.")
    else:
        # Registration logic remains unchanged
        pass

if __name__ == "__main__":
    main()
