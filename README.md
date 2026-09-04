# Agivant Hiring Campaign Streamlit App

This version is preconfigured with:

- Google Sheet ID: `1QreeVlM379CLvLCoDHAZunzp9tIwwPkQ9LrQUK0ukgE`
- Worksheet: `Sheet1`
- Resume Drive Folder ID: `1Fl0r5cZFPeWL6Fjhz9uLh2vTuzXfaJV9`
- Logo location: `logo.png` in the project root

## Project structure

```text
hiring_campaign_app_v3/
│
├── app.py
├── logo.png                # Add your company logo here
├── requirements.txt
├── README.md
├── .gitignore
│
└── .streamlit/
    ├── secrets.example.toml
    └── secrets.toml        # Create locally; do not commit
```

## Google Sheet columns

Add these headers to Row 1 of `Sheet1`:

1. Candidate ID
2. Timestamp
3. Full Name
4. Mobile Number
5. Email
6. Aadhaar
7. PAN
8. Current City
9. Highest Qualification
10. Institute
11. Graduation Year
12. CGPA / Percentage
13. Fresher / Experienced
14. Total Experience
15. Relevant Experience
16. Current Company
17. Current Designation
18. Notice Period
19. Primary Skill
20. Resume Link

## Resume naming

Uploaded resumes are renamed automatically using the Candidate ID.

Examples:

- `AGI-260904-A1B2C3.pdf`
- `AGI-260904-C4D5E6.docx`

The original file extension is preserved.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .streamlit/secrets.example.toml .streamlit/secrets.toml
streamlit run app.py
```

## Required Google setup

1. Enable Google Sheets API.
2. Enable Google Drive API.
3. Create a Google service account.
4. Create/download its JSON key.
5. Share the Google Sheet with the service-account email as Editor.
6. Share the resume folder with the service-account email as Editor.
7. Copy the service-account JSON values into `.streamlit/secrets.toml`.
8. Change `company_website` if required.

## Important

Do not commit `.streamlit/secrets.toml` to GitHub.
