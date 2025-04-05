import streamlit as st
from azure.storage.blob import BlobServiceClient
import datetime
import pandas as pd
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

# UI Setup
st.set_page_config(page_title="Health Total Analytics - CSV Uploader to Azure Blob", layout="centered")
st.title("📤 Upload Your CSV File to Azure Blob Storage")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]

    if missing_cols:
        st.error("❌ Upload blocked. The following required columns are missing:")        
        st.warning("⚠️ Please login to the database and create below columns in the target table before uploading.")
        st.code("\n".join(missing_cols), language="text")
    else:
        # Generate filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        blob_filename = f"{uploaded_file.name.split('.')[0]}_{timestamp}.csv"
        blob_path = f"{BLOB_FOLDER_PATH}{blob_filename}"

        if st.button("🚀 Upload to Azure Blob"):
            try:
                uploaded_file.seek(0)  # Reset file pointer to beginning before upload
                blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
                container_client = blob_service_client.get_container_client(CONTAINER_NAME)

                blob_client = container_client.get_blob_client(blob_path)
                blob_client.upload_blob(uploaded_file, overwrite=True)

                st.success("✅ File uploaded successfully!")
                st.info(f"📂 File path: `{CONTAINER_NAME}{blob_path}`")
            except Exception as e:
                st.error(f"❌ Upload failed: {str(e)}")
