import re
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from io import BytesIO

import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload


# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Agivant Hiring Campaign",
    page_icon="icon.jpeg",
    layout="centered",
)

# -----------------------------
# LOGO + HEADER
# -----------------------------
logo_path = Path("logo.png")
if logo_path.exists():
    st.image(str(logo_path))

st.title("Agivant Hiring Campaign")
st.caption("Please complete the form below. Fields marked with * are mandatory.")


# -----------------------------
# GOOGLE CONNECTION
# -----------------------------
@st.cache_resource
def get_google_clients():
    credentials_dict = dict(st.secrets["gcp_service_account"])

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    credentials = Credentials.from_service_account_info(
        credentials_dict,
        scopes=scopes,
    )

    gc = gspread.authorize(credentials)
    drive_service = build(
        "drive",
        "v3",
        credentials=credentials,
        cache_discovery=False,
    )

    return gc, drive_service


def get_worksheet():
    gc, _ = get_google_clients()
    spreadsheet = gc.open_by_key(st.secrets["google"]["spreadsheet_id"])
    return spreadsheet.worksheet(st.secrets["google"]["worksheet_name"])


# -----------------------------
# HELPERS
# -----------------------------
def generate_candidate_id():
    # Example: AGI-260904-A1B2C3
    date_part = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%y%m%d")
    random_part = uuid.uuid4().hex[:6].upper()
    return f"AGI-{date_part}-{random_part}"


def validate_mobile(value):
    return bool(re.fullmatch(r"[6-9]\d{9}", value.strip()))


def validate_email(value):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value.strip()))


def validate_aadhaar(value):
    cleaned = re.sub(r"\s+", "", value)
    return bool(re.fullmatch(r"\d{12}", cleaned))


def validate_pan(value):
    return bool(re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", value.strip().upper()))


def upload_resume_to_drive(uploaded_file, candidate_id):
    _, drive_service = get_google_clients()

    original_ext = Path(uploaded_file.name).suffix.lower()
    filename = f"{candidate_id}{original_ext}"

    file_metadata = {
        "name": filename,
        "parents": [st.secrets["google"]["drive_folder_id"]],
    }

    media = MediaIoBaseUpload(
        BytesIO(uploaded_file.getvalue()),
        mimetype=uploaded_file.type or "application/octet-stream",
        resumable=False,
    )

    created = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id,webViewLink",
    ).execute()

    return created["webViewLink"]


def append_candidate(row):
    worksheet = get_worksheet()
    worksheet.append_row(row, value_input_option="USER_ENTERED")


# -----------------------------
# FORM
# NOTE: st.form() is intentionally NOT used here. Widgets inside a
# form only rerun the script on submit, so a radio button placed
# inside a form (anywhere in it) can never conditionally reveal
# other fields live. Using plain widgets + a regular st.button lets
# the "Fresher / Experienced" radio live in its original position
# (right after Education) while still reacting immediately.
# -----------------------------
st.subheader("Personal Details")

full_name = st.text_input("Full Name *")
mobile = st.text_input("Mobile Number *", max_chars=10)
email = st.text_input("Email *")

aadhaar = st.text_input(
    "Aadhaar Number *",
    max_chars=12,
    type="password",
    help="Enter your 12-digit Aadhaar number.",
)

pan = st.text_input(
    "PAN *",
    max_chars=10,
    help="Example: ABCDE1234F",
)

current_city = st.text_input("Current City *")

st.subheader("Education")

highest_qualification = st.selectbox(
    "Highest Qualification *",
    [
        "Select",
        "Diploma",
        "Bachelor's Degree",
        "Master's Degree",
        "PhD",
        "Other",
    ],
)

institute = st.text_input("Institute *")

graduation_year = st.number_input(
    "Graduation Year *",
    min_value=1980,
    max_value=2100,
    value=datetime.now(ZoneInfo("Asia/Kolkata")).year,
    step=1,
)

cgpa_percentage = st.text_input(
    "CGPA / Percentage *",
    placeholder="Example: 8.2 CGPA or 78%",
)

st.subheader("Professional Details")

experience_type = st.radio(
    "Fresher / Experienced *",
    ["Fresher", "Experienced"],
    horizontal=True,
    key="experience_type",
)

total_experience = ""
relevant_experience = ""
current_company = ""
current_designation = ""
notice_period = ""

if experience_type == "Experienced":
    st.markdown("#### Experience Details")

    total_experience = st.text_input(
        "Total Experience",
        placeholder="Example: 3 years 6 months",
    )

    relevant_experience = st.text_input(
        "Relevant Experience",
        placeholder="Example: 2 years",
    )

    current_company = st.text_input(
        "Current Company"
    )

    current_designation = st.text_input(
        "Current Designation"
    )

    notice_period = st.selectbox(
        "Notice Period",
        [
            "Select",
            "Immediate",
            "15 Days",
            "30 Days",
            "45 Days",
            "60 Days",
            "90 Days",
            "More than 90 Days",
        ],
    )

primary_skill = st.text_input(
    "Primary Skill *",
    placeholder="Example: Java, Python, Data Engineering",
)

resume = st.file_uploader(
    "Resume *",
    type=["pdf", "doc", "docx"],
    help="Accepted formats: PDF, DOC, DOCX",
)

consent = st.checkbox(
    "I confirm that the information provided is correct and may be used for recruitment purposes. *"
)

submitted = st.button(
    "Submit Application",
    use_container_width=True,
)


# -----------------------------
# SUBMISSION
# -----------------------------
if submitted:
    errors = []

    if not full_name.strip():
        errors.append("Full Name is required.")

    if not validate_mobile(mobile):
        errors.append("Enter a valid 10-digit Indian mobile number.")

    if not validate_email(email):
        errors.append("Enter a valid email address.")

    if not validate_aadhaar(aadhaar):
        errors.append("Aadhaar must contain exactly 12 digits.")

    if not validate_pan(pan):
        errors.append("Enter a valid PAN in the format ABCDE1234F.")

    if not current_city.strip():
        errors.append("Current City is required.")

    if highest_qualification == "Select":
        errors.append("Select Highest Qualification.")

    if not institute.strip():
        errors.append("Institute is required.")

    if not cgpa_percentage.strip():
        errors.append("CGPA / Percentage is required.")

    if not primary_skill.strip():
        errors.append("Primary Skill is required.")

    if resume is None:
        errors.append("Resume is required.")

    if not consent:
        errors.append("Please confirm the recruitment consent checkbox.")

    if errors:
        for error in errors:
            st.error(error)
    else:
        try:
            candidate_id = generate_candidate_id()

            timestamp = datetime.now(
                ZoneInfo("Asia/Kolkata")
            ).strftime("%Y-%m-%d %H:%M:%S IST")

            resume_link = upload_resume_to_drive(
                resume,
                candidate_id,
            )

            row = [
                candidate_id,
                timestamp,
                full_name.strip(),
                mobile.strip(),
                email.strip().lower(),
                re.sub(r"\s+", "", aadhaar),
                pan.strip().upper(),
                current_city.strip(),
                highest_qualification,
                institute.strip(),
                int(graduation_year),
                cgpa_percentage.strip(),
                experience_type,
                total_experience.strip(),
                relevant_experience.strip(),
                current_company.strip(),
                current_designation.strip(),
                "" if notice_period == "Select" else notice_period,
                primary_skill.strip(),
                resume_link,
            ]

            append_candidate(row)

            st.success("Application submitted successfully.")
            st.info(f"Candidate ID: {candidate_id}")

            company_website = st.secrets["app"]["company_website"]

            st.markdown(
                f"""
                <meta http-equiv="refresh" content="2; url={company_website}">
                <p>Redirecting to the company website...</p>
                <p>
                    <a href="{company_website}">
                        Click here if you are not redirected automatically.
                    </a>
                </p>
                """,
                unsafe_allow_html=True,
            )

        except Exception as e:
            st.error(
        "We could not submit your application. Please contact the recruitment team."
    )

            st.error(f"Technical Error: {type(e).__name__}: {e}")
