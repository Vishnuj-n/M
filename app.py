import streamlit as st
from PIL import Image
from main import Meme
import random
import os
import csv

def validate_roll_number(roll_no):
    """Validate if roll number is alphanumeric and not empty"""
    if not roll_no:
        return False, "Roll Number cannot be empty"
    if not roll_no.isalnum():
        return False, "Roll Number must be alphanumeric"
    return True, "Valid"

def register_user(name, roll_no):
    """Register user with name and roll number"""
    is_valid, message = validate_roll_number(roll_no)
    if not name:
        return False, "Name cannot be empty"
    if not is_valid:
        return False, message
    
    # Check if roll number already exists
    if check_user_exists(roll_no):
        return False, "Roll number already registered"
    
    # Save to register.csv
    csv_path = "register.csv"
    file_exists = os.path.isfile(csv_path)
    
    try:
        with open(csv_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            # Write header if file is new
            if not file_exists:
                writer.writerow(["Name", "Roll Number"])
            # Write user data
            writer.writerow([name, roll_no])
        return True, "Registration successful"
    except Exception as e:
        return False, f"Registration failed: {str(e)}"

def check_user_exists(roll_no):
    """Check if user with roll number exists in register.csv"""
    if not os.path.isfile("register.csv"):
        return False
    
    try:
        with open("register.csv", mode='r') as file:
            reader = csv.reader(file)
            # Skip header
            next(reader, None)
            for row in reader:
                if len(row) >= 2 and row[1] == roll_no:
                    return True
        return False
    except Exception:
        return False

def get_user_name(roll_no):
    """Get user name from roll number"""
    if not os.path.isfile("register.csv"):
        return None
    
    try:
        with open("register.csv", mode='r') as file:
            reader = csv.reader(file)
            # Skip header
            next(reader, None)
            for row in reader:
                if len(row) >= 2 and row[1] == roll_no:
                    return row[0]
        return None
    except Exception:
        return None

# Initialize session state for user login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""


api_keys=["GEMINI_API_KEY", "GM1", "GM2"]
key = random.choice(api_keys)
meme_generator = Meme(key=key)

# Sidebar for auth
st.sidebar.header("User Authentication & API")

# Add this after the authentication header but before the login/logout sections

# Sidebar for auth
st.sidebar.header("User Authentication")

# Optional API key input
with st.sidebar.expander("API Settings (Optional)", expanded=False):
    user_api_key = st.text_input("Enter your Gemini API Key:", type="password", 
                                help="Leave empty to use the default API keys")

# Initialize Meme class with user API key if provided
if 'user_api_key' in locals() and user_api_key:
    meme_generator = Meme(key=random.choice(api_keys), user_api_key=user_api_key)
else:
    api_keys=["GEMINI_API_KEY", "GM1", "GM2"]
    key = random.choice(api_keys)
    meme_generator = Meme(key=key)

# Show login or logout based on session state
if not st.session_state.logged_in:
    # Login section
    login_tab, register_tab = st.sidebar.tabs(["Login", "Register"])
    
    with login_tab:
        login_roll_no = st.text_input("Roll Number", key="login_roll")
        if st.button("Login"):
            if check_user_exists(login_roll_no):
                user_name = get_user_name(login_roll_no)
                st.session_state.logged_in = True
                st.session_state.user_name = user_name
                st.sidebar.success(f"Welcome, {user_name}!")
                st.rerun()  # Use st.rerun() instead of st.experimental_rerun()
            else:
                st.sidebar.error("Roll number not registered")
    
    with register_tab:
        user_name = st.text_input("Name")
        roll_no = st.text_input("Roll Number")
        if st.button("Register"):
            success, message = register_user(user_name, roll_no)
            if success:
                st.sidebar.success(message)
            else:
                st.sidebar.error(message)
else:
    # Show logged in user info and logout button
    st.sidebar.success(f"Logged in as {st.session_state.user_name}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_name = ""
        st.rerun()  # Use st.rerun() instead of st.experimental_rerun()

st.title("AI Meme Generator")

# User inputs
prompt = st.text_input("Enter a prompt for image generation:")
text = st.text_area("Enter meme text:")
position = st.selectbox("Select text position:", ["top", "center", "bottom"], index=2)

if st.button("Generate Meme"):
    if prompt:
        with st.spinner("Generating image..."):
            image = meme_generator.generate_image(prompt)
            if image:
                st.image(image, caption="Generated Image",  use_container_width=True)
            else:
                st.error("Failed to generate image.")
    else:
        st.warning("Please enter a prompt for image generation.")

if st.button("Add Text to Meme"):
    if text:
        with st.spinner("Adding text to image..."):
            try:
                image1=Image.open("gemini-native-image.png")
                if image1.mode != 'RGBA':
                    image1 = image1.convert('RGBA')
                meme = meme_generator.add_text(image1,text, position)
                st.image(meme, caption="Final Meme", use_container_width =True)
                #meme_generator.save_meme("final_meme.png")
                st.success("Meme saved as final_meme.png")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please enter text for the meme.")
