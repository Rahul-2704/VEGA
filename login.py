import streamlit as st
import sqlite3
from passlib.hash import pbkdf2_sha256
# from home import home

global unique_id
global username_login
def new_lecture():
    st.title("Lecture Form")
        # Add your form code here
    
    with st.form("User Information Form"):

        st.header("Enter Lecture Details")
        subject_name = st.text_input("Enter Subject Name")
        lecture_start = st.time_input("Enter Lecture Start time",value=None)
        lecture_end = st.time_input("Enter Lecture End Time",value=None)
        division=st.selectbox("Enter Division",["COMPSA","COMPSB","AIML","DS","EXTC-E","ETRX-F"],placeholder="Select a Division",index=None)
        submit_button = st.form_submit_button("Submit")

        if submit_button:
            create_table_lecture(1,subject_name,lecture_start,lecture_end,division)
            st.write("$subject_name")
            
def previous_session():
    st.write("New session")
       
def home():
    pages = {
    "New Lecture": new_lecture,
    "Previous Lecture": previous_session
    }
     
    page = st.sidebar.selectbox("Select a page", list(pages.keys()))
    pages[page]()

def previous_session():
    st.write("Prev Session")
    
def create_table():
    conn = sqlite3.connect('C:\\Users\\Aman\\VEGA.db')
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

def create_table_lecture(id,subjectName,startTime,endTime,division):
    conn = sqlite3.connect('C:\\Users\\Aman\\VEGA.db')
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
    conn = sqlite3.connect('C:\\Users\\Aman\\VEGA.db')
    cursor = conn.cursor()
    hashed_password = pbkdf2_sha256.hash(password)
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()

# Function to authenticate a user
def authenticate_user(username, password):
    conn = sqlite3.connect('C:\\Users\\Aman\\VEGA.db')
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

# Display the login/registration toggle

def login():
    login_or_register = st.radio("Select an option:", ("Login", "Register"))

    # Show the appropriate form based on the selected option
    if login_or_register == "Login":
        st.header("Login")
        username_login = st.text_input("Username:")
        password_login = st.text_input("Password:", type="password")
        
        if st.button("Login"):
            if authenticate_user(username_login, password_login):
                if st.success("Login successful!"):
                    st.session_state["loggedin"]=True
                    st.experimental_rerun()
                # pg=st.sidebar.selectbox("Select a page",["New Session","Previous Session"])
                # if pg=="New Session":
                #     new_session()
                else:
                    st.write("error")


            else:
                st.error("Invalid username or password. Please try again.")

    else:  # Registration form
        st.header("Register")
        username_register = st.text_input("Choose a username:")
        password_register = st.text_input("Choose a password:", type="password")

        if st.button("Register"):
            if username_exists(username_register):
                st.error("Username already exists. Please choose another one.")
            else:
                register_user(username_register, password_register)
                st.success("Registration successful! You can now log in.")


def main():
    if "loggedin" not in st.session_state:
        st.session_state["loggedin"]=False
    
    if st.session_state["loggedin"]:
        home()
    else:
        login()
        

if __name__=="__main__":
    main()
