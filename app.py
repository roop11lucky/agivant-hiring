import base64
import re
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

import requests
import streamlit as st


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
# HELPERS
# -----------------------------
def generate_candidate_id():
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


def submit_to_google_apps_script(payload):
    response = requests.post(
        st.secrets["google"]["apps_script_url"],
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    result = response.json()

    if not result.get("success"):
        raise Exception(result.get("message", "Submission failed."))

    return result


# -----------------------------
# FORM
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
    ["Select", "Diploma", "Bachelor's Degree", "Master's Degree", "PhD", "Other"],
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

    current_company = st.text_input("Current Company")
    current_designation = st.text_input("Current Designation")

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

            original_ext = Path(resume.name).suffix.lower()
            resume_name = f"{candidate_id}{original_ext}"

            resume_base64 = base64.b64encode(
                resume.getvalue()
            ).decode("utf-8")

            payload = {
                "candidate_id": candidate_id,
                "timestamp": timestamp,
                "full_name": full_name.strip(),
                "mobile": mobile.strip(),
                "email": email.strip().lower(),
                "aadhaar": re.sub(r"\s+", "", aadhaar),
                "pan": pan.strip().upper(),
                "current_city": current_city.strip(),
                "highest_qualification": highest_qualification,
                "institute": institute.strip(),
                "graduation_year": int(graduation_year),
                "cgpa_percentage": cgpa_percentage.strip(),
                "experience_type": experience_type,
                "total_experience": total_experience.strip(),
                "relevant_experience": relevant_experience.strip(),
                "current_company": current_company.strip(),
                "current_designation": current_designation.strip(),
                "notice_period": "" if notice_period == "Select" else notice_period,
                "primary_skill": primary_skill.strip(),
                "resume_name": resume_name,
                "resume_type": resume.type or "application/octet-stream",
                "resume_base64": resume_base64,
            }

            submit_to_google_apps_script(payload)

            st.success("Application submitted successfully.")
            st.info(f"Candidate ID: {candidate_id}")

            company_website = st.secrets["app"]["company_website"]

            st.markdown(
                f'''
                <meta http-equiv="refresh" content="2; url={company_website}">
                <p>Redirecting to the company website...</p>
                <p>
                    <a href="{company_website}">
                        Click here if you are not redirected automatically.
                    </a>
                </p>
                ''',
                unsafe_allow_html=True,
            )

        except Exception as e:
            st.error(
                "We could not submit your application. Please contact the recruitment team."
            )
            st.error(f"Technical Error: {type(e).__name__}: {e}")
