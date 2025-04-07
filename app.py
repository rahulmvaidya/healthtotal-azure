import streamlit as st
from azure.storage.blob import BlobServiceClient
import datetime
import pandas as pd
import io
import chardet

# ----------------------------
# Password Setup (edit this)
# ----------------------------
PASSWORD = "HealthAzureTotal@2025"  # Change this to your own password

# ----------------------------
# Backend Config (edit these)
# ----------------------------
AZURE_CONNECTION_STRING = st.secrets["AZURE_CONNECTION_STRING"]
CONTAINER_NAME = st.secrets["CONTAINER_NAME"]
BLOB_FOLDER_PATH = "/analytics/"
# ----------------------------

# Required columns list
REQUIRED_COLUMNS = [
    "Unique ID", "First Lead Created", "Last Lead Created", "First Contacted Date", "Last Contacted Date",
    "First FC Date", "Last FC Date", "First Joined Date", "Last Joined Date", "First Joined Weeks", 
    "Last Joined Weeks", "Total Amount Paid", "Ref given Count", "Collection from Ref", "Client Name", 
    "Mobile", "Age", "Weight", "Height", "Email", "Gender", "DOB", "City", "Address", "Pin code", 
    "Vertical", "Center", "Max Stage", "Acidity", "Acne ( Skin)", "Back Pain", "Fluctuating BP", 
    "High TC", "Diabeties", "History of Epilepsy", "Hair fall", "Hypertension", "hypothyroid", "IBS", 
    "Irregular menses", "Joint Pain", "low energy", "low Immunity", "Menopause", "Bypass Surgery", 
    "UnderWeight", "Overweight", "PCOD", "insomia( Sleep)", "psoriasis ( Skin)", "Cardio vascular disease", 
    "Dysmenorrhoea", "Depression", "anemia", "Asthma", "No Problem", "Arthritis", "WaterRetention", 
    "History of cancer", "Auto immune disorder", "Severe Rheumatoid Arthritis", "Angioplasty", 
    "High Uric Acid", "High Creatinine", "Migrain", "Renal stone", "Gallbladder stone", "High TG", 
    "Dyslipidemia", "Slip disc", "Leg cramps", "Leg Pain", "Fatigue", "Cervical spondylosis", 
    "Lumbar spondylosis", "Bodyache", "Anorexia", "Heel pain", "Calcaneal spur", "Acid reflux", 
    "Recurrent cold cough", "Recurrent UTI", "Tingling", "Numbness", "Varicose Vein", "Thalassemia minor", 
    "Hyper Prolactinemia", "Uterine Fibriod", "Urticaria", "Osteoarthritis", "Anxiety", 
    "Umbelical Hernia", "Hypotension", "leucorrhoea", "low vit B12", "low vit D3", "cardiac arrhythmia", 
    "Stomatitis", "Allergic rhinitis", "Vitiligo", "Menorrhagia", "sweet cravings", "Fatty Liver", 
    "Knee Pain", "Gas", "Bloating", "Pain", "Others", "Latest Lead Code", "First Lead Code", 
    "First Source", "Latest Source", "First Publisher", "Latest Publisher", "pk_id", "created_date"
]

# ----------------------------
# Authentication Check
# ----------------------------
def check_password():
    def password_entered():
        if st.session_state["password"] == PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("🔐 Enter password to continue:", type="password", on_change=password_entered, key="password")
        st.stop()
    elif not st.session_state["password_correct"]:
        st.error("❌ Incorrect password. Try again.")
        st.text_input("🔐 Enter password to continue:", type="password", on_change=password_entered, key="password")
        st.stop()

check_password()

# ----------------------------
# UI Setup
# ----------------------------
st.set_page_config(page_title="Health Total Analytics - CSV Uploader to Azure Blob", layout="centered")
st.title("📤 Upload Your CSV File to Azure Blob Storage")


# ----------------------------
# File Upload Section
# ----------------------------
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    # Step 1: Read bytes & detect encoding
    file_bytes = uploaded_file.read()
    detected_encoding = chardet.detect(file_bytes)["encoding"]

    if not detected_encoding:
        st.error("❌ Could not detect encoding. Please check your file.")
        st.stop()

    # Step 2: Read with encoding
    try:
        df = pd.read_csv(io.BytesIO(file_bytes), encoding=detected_encoding)
    except Exception as e:
        st.error(f"❌ Failed to read the CSV file using encoding `{detected_encoding}`: {str(e)}")
        st.stop()

    # Step 3: Column check
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    found_cols = len(REQUIRED_COLUMNS) - len(missing_cols)

    if missing_cols:
        st.error("❌ Upload blocked. The following required columns are missing:")
        st.info(f"✅ {found_cols} out of {len(REQUIRED_COLUMNS)} required columns found.")
        st.warning("⚠️ Please login to the database and create the following columns before uploading.")
        st.code("\n".join(missing_cols), language="text")
    else:
        st.success("✅ All required columns are present!")
        st.subheader("🔍 Preview of Uploaded File")
        st.dataframe(df.head(5))

        # Step 4: Blob upload
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        blob_filename = f"{uploaded_file.name.split('.')[0]}_{timestamp}.csv"
        blob_path = f"{BLOB_FOLDER_PATH}{blob_filename}"

        if st.button("🚀 Upload to Azure Blob"):
            try:
                blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
                container_client = blob_service_client.get_container_client(CONTAINER_NAME)
                blob_client = container_client.get_blob_client(blob_path)

                with st.spinner("⏳ Uploading your file to Azure Blob Storage..."):
                    blob_client.upload_blob(io.BytesIO(file_bytes), overwrite=True)

                st.success("✅ File uploaded successfully!")
                st.info(f"📂 File path: `{CONTAINER_NAME}{blob_path}`")
            except Exception as e:
                st.error(f"❌ Upload failed: {str(e)}")
