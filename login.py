import streamlit as st
import sqlite3
from passlib.hash import pbkdf2_sha256
import cv2
import face_recognition
import numpy as np
import os
import uuid
import time
from gtts import gTTS
import os
import pygame
import librosa
import numpy as np
from audio_recorder_streamlit import audio_recorder

# Assuming the other functions (create_table, create_table_lecture, username_exists, register_user, authenticate_user) remain unchanged
total_time = 0
global_lecture_end = 0
global_lecture_start = 0
global_lecture_id = 0
# Simplified state management for login and form submission
def main():
    # Initialize session state variables if they don't exist
    if "loggedin" not in st.session_state:
        st.session_state["loggedin"] = False
    if "submitted" not in st.session_state:
        st.session_state["submitted"] = False
    if "finished" not in st.session_state:
        st.session_state["finished"] = False
    if "audio_verification_started" not in st.session_state:
        st.session_state["audio_verification_started"] = False

    # Page routing based on state
    if st.session_state["loggedin"]:
        if not st.session_state["submitted"] :
            new_lecture()  # Show the form for a new lecture
        elif not st.session_state["finished"]:
            webcam()  # Show the webcam page after form submission
        elif st.session_state["audio_verification_started"]:
            audio()  # Show the audio verification page after finishing webcam step
    else:
        login()  # Show the login page if not logged in

def audio():
    def record_audio(filename, duration=5, sr=44100):
        import sounddevice as sd
        from scipy.io.wavfile import write

        # Record audio
        recording = sd.rec(int(duration * sr), samplerate=sr, channels=1, dtype='float32')
        sd.wait()  # Wait until recording is finished

        # Save recording to file
        write(filename, sr, recording)

        return recording

    # Streamlit interface
    st.title("Voice Authentication")

    # Button to start and stop recording
    record_button = st.button("Record")

    if record_button:
        st.write("Recording... Speak now.")
        recorded_audio = record_audio("recorded_audio.wav", duration=5)
        st.write("Recording finished.")

        # Authenticate user
        stored_audio_path = "omkar.wav"  # Path to stored audio file
        test_audio_path = "recorded_audio.wav"  # Path to recorded audio file

        # Load stored audio
        stored_audio, _ = librosa.load(stored_audio_path, sr=44100)

        # Load recorded audio
        test_audio, _ = librosa.load(test_audio_path, sr=44100)

        # Calculate correlation coefficient
        min_length = min(len(stored_audio), len(test_audio))
        stored_audio = stored_audio[:min_length]
        test_audio = test_audio[:min_length]
        r = np.corrcoef(stored_audio, test_audio)[0, 1]

        # Authenticate user based on correlation coefficient
        threshold = 0  # Adjust the threshold as needed
        if r > threshold:
            st.success(f'User authenticated ')
        else:
            st.error(f'User authentication failed !')

def new_lecture():
    st.title("Lecture Form")
    with st.form("User Information Form"):
        # Form fields
        st.header("Enter Lecture Details")
        subject_name = st.text_input("Enter Subject Name")
        lecture_start = st.time_input("Enter Lecture Start time")
        lecture_start = lecture_start.strftime("%H:%M:%S")
        global global_lecture_start,global_lecture_end
        global_lecture_start = lecture_start
        lecture_end = st.time_input("Enter Lecture End Time")
        lecture_end = lecture_end.strftime("%H:%M:%S")
        global_lecture_end = lecture_end
        division = st.selectbox("Enter Division", ["COMPSA", "COMPSB", "AIML", "DS", "EXTC-E", "ETRX-F"], placeholder="Select a Division")
        type(division)
        # Form submission
        submit_button = st.form_submit_button("Submit")

        if submit_button:
            # Update the session state to indicate that the form was submitted
            st.session_state["submitted"] = True
            # You might want to save the form data to a database or perform some action here
            conn = sqlite3.connect('C:\\Users\\omkar\\Downloads\\VEGA.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO lecture(subjectName,startTime,endTime,division) VALUES(?,?,?,?)",
            (subject_name,lecture_start,lecture_end,division))

            lecture_id=cursor.execute("""SELECT lectureId FROM lecture
                                    ORDER BY lectureId DESC
                                    LIMIT 1""")
            global global_lecture_id
            global_lecture_id = lecture_id
            conn.commit()
            conn.close()
            # Rerun the app to reflect changes in the state
            st.experimental_rerun()

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

def speak(text):
    tts = gTTS(text=text, lang='en')
    tts.save("temp.mp3")
    pygame.mixer.init()
    pygame.mixer.music.load("temp.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    os.remove("temp.mp3")

def audio_verification(upload_audio_path, stored_audio_path='omkar.wav'):
    stored_audio, _ = librosa.load(stored_audio_path, sr=44000)
    test_audio, _ = librosa.load(upload_audio_path, sr=44000)
    min_length = min(len(stored_audio), len(test_audio))
    stored_audio = stored_audio[:min_length]
    test_audio = test_audio[:min_length]
    r=0
    r = np.corrcoef(stored_audio, test_audio)[0, 1]
    threshold = 0  # Adjust based on your requirement
    if r > threshold:
        return f'User authenticated (r = {r:.4f})'
    else:
        return f'User authentication failed (r = {r:.4f})'

def webcam():
    start = time.time()
    face_verified = False
    # Initialize the webcam
    video_capture = cv2.VideoCapture(0)

    # Lower the resolution to speed up processing
    video_capture.set(3, 640)  # Width
    video_capture.set(4, 480)  # Height

    # Specify the folder where your images are stored
    images_folder = "C:\\Users\\omkar\\OneDrive\\Desktop\\REAL TIME FACE RECO\\database"

    # Initialize lists for face encodings and names
    known_face_encodings = []
    known_face_names = []

    # Load each file from the images folder
    for filename in os.listdir(images_folder):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            # Extract the student name from the filename
            name = os.path.splitext(filename)[0]

            # Load the image file
            image_path = os.path.join(images_folder, filename)
            image = face_recognition.load_image_file(image_path)

            # Attempt to extract a single face encoding from each image
            try:
                face_encoding = face_recognition.face_encodings(image)[0]
                # Add the face encoding and name to our lists
                known_face_encodings.append(face_encoding)
                known_face_names.append(name)
            except IndexError:
                # If no face is found in the image, skip it
                print(f"No face found in {filename}, skipping.")

    # Display the title
    st.title("Real-Time Face Recognition")

    # Create a placeholder for the video
    video_placeholder = st.empty()

    while True and not face_verified:
        # Grab a single frame of video
        ret, frame = video_capture.read()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            # Use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                face_verified = True
                name = known_face_names[best_match_index]
                print(name)
            face_names.append(name)

        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            # Draw a label with a name below the face
            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)

        # Display the resulting video stream
        video_placeholder.image(frame, channels="BGR")
        if face_verified:
            break
        
        # Hit 'q' on the keyboard to quit!
        #if cv2.waitKey(1) & 0xFF == ord('q'):
        #    break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()
    if face_verified:
        st.write("Verification Successful !")
        end = time.time()
        margin = end - start
        global total_time,global_lecture_end,global_lecture_start
        total_time += margin
        late = (global_lecture_end-global_lecture_start)//2
    #st.title("Audio Authentication")
    # Record audio
        if st.button("Mark Attendance"):
            conn = sqlite3.connect('C:\\Users\\omkar\\Downloads\\VEGA.db')
            cursor = conn.cursor()
            cursor.execute("select UID from students where Name=?", (name,))
            result = cursor.fetchone()
            if result:
                uid = result[0]
            # st.write(uid)
            global global_lecture_id
            cursor.execute("""select subjects.subjectId FROM lecture
                            JOIN subjects ON lecture.subjectName = subjects.subjectName;""")
            res= cursor.fetchone()
            if res:
                subjectId = res[0]
            cursor.execute("insert into attendancerecord(uid,lectureId,subjectId,status) values (?,?,?,?)",(uid,global_lecture_id,subjectId,"present"))
            conn.commit()
            conn.close()
            st.experimental_rerun()
        if st.button("Finish Attendance"):
            st.session_state["finished"] = True
            st.session_state['audio_verification_started'] = True
            st.experimental_rerun()
    
            


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
    # login_or_register = st.radio("Select an option:", ("Login", "Register"))
    login_or_register = "Login"
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


# Make sure to call the main function
if __name__ == "__main__":
    main()