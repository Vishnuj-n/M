import streamlit as st
from PIL import Image
from main import Meme
import random
import os
from google.oauth2 import service_account
from google.cloud import bigquery

# Initialize BigQuery client
@st.cache_resource
def get_bigquery_client():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    return bigquery.Client(credentials=credentials)

# Initialize BigQuery tables if they don't exist
def initialize_bigquery_tables():
    client = get_bigquery_client()
    dataset_id = st.secrets.get("bigquery_dataset", "meme_generator")
    table_id = "users"
    
    # Check if dataset exists, if not create it
    dataset_ref = client.dataset(dataset_id)
    try:
        client.get_dataset(dataset_ref)
    except Exception:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"  # You can change the location if needed
        client.create_dataset(dataset)
    
    # Check if users table exists, if not create it
    table_ref = dataset_ref.table(table_id)
    try:
        client.get_table(table_ref)
    except Exception:
        schema = [
            bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("roll_number", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("registration_date", "TIMESTAMP", mode="REQUIRED")
        ]
        table = bigquery.Table(table_ref, schema=schema)
        client.create_table(table)

def validate_roll_number(roll_no):
    """Validate if roll number is alphanumeric and not empty"""
    if not roll_no:
        return False, "Roll Number cannot be empty"
    if not roll_no.isalnum():
        return False, "Roll Number must be alphanumeric"
    return True, "Valid"

def register_user(name, roll_no):
    """Register user with name and roll number in BigQuery"""
    is_valid, message = validate_roll_number(roll_no)
    if not name:
        return False, "Name cannot be empty"
    if not is_valid:
        return False, message
    
    # Check if roll number already exists
    if check_user_exists(roll_no):
        return False, "Roll number already registered"
    
    try:
        client = get_bigquery_client()
        dataset_id = st.secrets.get("bigquery_dataset", "meme_generator")
        table_id = f"{dataset_id}.users"
        
        # Insert user data
        rows_to_insert = [
            {
                "name": name,
                "roll_number": roll_no,
                "registration_date": bigquery.ScalarQueryParameter(
                    "timestamp", "TIMESTAMP", bigquery.CURRENT_TIMESTAMP
                ).to_api_repr()["parameterValue"]["value"]
            }
        ]
        
        errors = client.insert_rows_json(table_id, rows_to_insert)
        if errors == []:
            return True, "Registration successful"
        else:
            return False, f"Registration failed: {errors}"
    except Exception as e:
        return False, f"Registration failed: {str(e)}"

def check_user_exists(roll_no):
    """Check if user with roll number exists in BigQuery"""
    try:
        client = get_bigquery_client()
        dataset_id = st.secrets.get("bigquery_dataset", "meme_generator")
        
        query = f"""
        SELECT COUNT(*) as count
        FROM `{dataset_id}.users`
        WHERE roll_number = @roll_number
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("roll_number", "STRING", roll_no)
            ]
        )
        
        query_job = client.query(query, job_config=job_config)
        result = list(query_job.result())[0]
        
        return result.count > 0
    except Exception:
        return False

def get_user_name(roll_no):
    """Get user name from roll number using BigQuery"""
    try:
        client = get_bigquery_client()
        dataset_id = st.secrets.get("bigquery_dataset", "meme_generator")
        
        query = f"""
        SELECT name
        FROM `{dataset_id}.users`
        WHERE roll_number = @roll_number
        LIMIT 1
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("roll_number", "STRING", roll_no)
            ]
        )
        
        query_job = client.query(query, job_config=job_config)
        results = list(query_job.result())
        
        if results:
            return results[0].name
        return None
    except Exception:
        return None

# Initialize session state for user login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# Initialize BigQuery tables
initialize_bigquery_tables()

api_keys=["GEMINI_API_KEY", "GM1"]
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
                st.rerun()
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
        st.rerun()

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
                st.success("Meme generated successfully")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please enter text for the meme.")
