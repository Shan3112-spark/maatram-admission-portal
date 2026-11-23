
import streamlit as st
import json
import uuid
from pathlib import Path
from datetime import datetime
import pytesseract

# Use the Windows Tesseract path on a local Windows computer.
# On Streamlit Cloud/Linux, pytesseract uses the installed "tesseract" command.
WINDOWS_TESSERACT = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
if WINDOWS_TESSERACT.exists():
    pytesseract.pytesseract.tesseract_cmd = str(WINDOWS_TESSERACT)

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Maatram | Smart Admission",
    page_icon="🎓",
    layout="wide"
)

BASE_DIR = Path(__file__).parent
ASSET_DIR = BASE_DIR / "assets"
UPLOAD_DIR = BASE_DIR / "uploads"
DATABASE = BASE_DIR / "applications.json"

UPLOAD_DIR.mkdir(exist_ok=True)




# ==========================================
# 2. CUSTOM DESIGN - LARGE FONT VERSION
# ==========================================

st.markdown("""
<style>

/* PAGE BACKGROUND */
.stApp {
    background-color: #FFFEF9 !important;
    font-size: 20px !important;
}

/* GENERAL TEXT */
.stMarkdown p {
    color: #222222 !important;
    font-size: 19px !important;
    line-height: 1.6 !important;
}

/* HEADINGS */
.stMarkdown h1 {
    color: #171717 !important;
    font-size: 42px !important;
    font-weight: 800 !important;
}

.stMarkdown h2 {
    color: #171717 !important;
    font-size: 34px !important;
    font-weight: 750 !important;
}

.stMarkdown h3 {
    color: #171717 !important;
    font-size: 27px !important;
    font-weight: 700 !important;
}

/* HERO BANNER */
.hero {
    background-color: #FFD83D;
    padding: 42px;
    border-radius: 18px;
    margin-bottom: 30px;
}

.hero h1 {
    font-size: 42px !important;
    color: #171717 !important;
}

.hero p {
    font-size: 20px !important;
    color: #171717 !important;
}

/* INPUT LABELS */
.stTextInput label,
.stNumberInput label,
.stDateInput label,
.stFileUploader label,
.stCheckbox label,
.stRadio label {
    color: #202020 !important;
    font-size: 19px !important;
    font-weight: 700 !important;
}

/* INPUT BOXES */
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stTextArea textarea {
    background-color: #FFFFFF !important;
    color: #171717 !important;
    font-size: 20px !important;
    border: 2px solid #888888 !important;
    border-radius: 9px !important;
    min-height: 52px !important;
}

/* PLACEHOLDER */
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #666666 !important;
    opacity: 1 !important;
}

/* RADIO OPTIONS */
.stRadio div[role="radiogroup"] label {
    font-size: 19px !important;
    color: #202020 !important;
}

/* BUTTONS */
.stButton button,
.stFormSubmitButton button {
    background-color: #FFD02F !important;
    color: #171717 !important;
    font-size: 19px !important;
    font-weight: 800 !important;
    min-height: 52px !important;
    border: 2px solid #D2A400 !important;
    border-radius: 10px !important;
}

/* FORM */
div[data-testid="stForm"] {
    background-color: #FFFFFF !important;
    padding: 28px !important;
    border: 1px solid #DDDDDD !important;
    border-radius: 16px !important;
}

/* CAPTIONS */
div[data-testid="stCaptionContainer"] p {
    color: #444444 !important;
    font-size: 16px !important;
}

/* METRIC CARDS */
div[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid #DDDDDD !important;
    padding: 20px !important;
    border-radius: 12px !important;
}

div[data-testid="stMetricLabel"] {
    color: #333333 !important;
    font-size: 17px !important;
}

div[data-testid="stMetricValue"] {
    color: #171717 !important;
    font-size: 32px !important;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: #252525 !important;
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label {
    color: #FFFFFF !important;
}


/* FORCE ALL TEXT TO BLACK */
.stApp,
.stApp p,
.stApp span,
.stApp label,
.stApp small,
.stApp li,
.stApp div,
.stApp input,
.stApp textarea,
.stApp button,
.stApp [data-testid="stMarkdownContainer"] *,
.stApp [data-testid="stCaptionContainer"] *,
.stApp [data-testid="stMetricLabel"],
.stApp [data-testid="stMetricValue"] {
    color: #000000 !important;
}

/* Placeholder text */
.stApp input::placeholder,
.stApp textarea::placeholder {
    color: #000000 !important;
    opacity: 1 !important;
}

/* Keep yellow buttons readable */
.stButton button,
.stFormSubmitButton button {
    color: #000000 !important;
}


</style>
""", unsafe_allow_html=True)




# ==========================================
# 3. DATABASE FUNCTIONS
# ==========================================

def load_applications():
    if DATABASE.exists():
        try:
            return json.loads(DATABASE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
    return []


def save_applications(applications):
    DATABASE.write_text(
        json.dumps(applications, indent=4),
        encoding="utf-8"
    )


def delete_uploaded_file(relative_path):
    """Delete an uploaded file only if it is inside this project's uploads folder."""
    if not relative_path:
        return

    try:
        file_path = (BASE_DIR / relative_path).resolve()
        upload_dir = UPLOAD_DIR.resolve()

        # Prevent deleting files outside the uploads folder.
        if upload_dir in file_path.parents and file_path.is_file():
            file_path.unlink()
    except (OSError, ValueError):
        # Continue deleting the application record even if a file is already missing.
        pass


# ==========================================
# 4. HEADER
# ==========================================

left, right = st.columns([1, 4])

with left:
    logo_path = ASSET_DIR / "maatram_logo.png"

    if logo_path.exists():
        try:
            st.image(str(logo_path), width=180)
        except Exception:
            st.markdown("### MAATRAM")
    else:
        st.markdown("### MAATRAM")

with right:
    st.markdown("### Smart Admission Document Validation")
    st.caption("Digital Admission Verification Portal")

st.divider()

st.markdown("""
<div class="hero">
    <h1>Admission Verification Portal</h1>
    <p>A smarter and more reliable way to validate admission documents.</p>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 5. SESSION STATE
# ==========================================

if "student_logged_in" not in st.session_state:
    st.session_state.student_logged_in = False

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False


# ==========================================
# 6. ROLE SELECTION
# ==========================================

st.subheader("Welcome")

role = st.radio(
    "Select your portal",
    ["Student Portal", "Verifier / Admin Portal"],
    horizontal=True
)

# ==========================================
# 7. STUDENT PORTAL
# ==========================================

if role == "Student Portal":

    st.title("Student Portal")

    if not st.session_state.student_logged_in:

        st.subheader("Student Login")

        username = st.text_input("Student ID")
        password = st.text_input("Password", type="password")

        if st.button("Login", key="student_login"):

            if username == "student" and password == "student123":
                st.session_state.student_logged_in = True
                st.rerun()
            else:
                st.error("Invalid login. Demo: student / student123")

    else:

        st.success("Student logged in successfully!")

        if st.button("Student Logout"):
            st.session_state.student_logged_in = False
            st.rerun()

        st.divider()

        st.title("Student Application Form")

        st.info(
            "Instructions: Enter accurate information, "
            "upload a clear profile photo and marksheet, "
            "and verify your marks before submission."
        )

        with st.form("student_application"):

            # PERSONAL DETAILS
            st.subheader("1. Personal Details")

            name = st.text_input("Full Name")
            application_id = st.text_input("Application ID")
            email = st.text_input("Email Address")
            phone = st.text_input("Mobile Number")
            dob = st.date_input(
                "Date of Birth",
                value=None,
                min_value=datetime(1950, 1, 1).date(),
                max_value=datetime.now().date()
            )

            # DOCUMENT UPLOAD
            st.subheader("2. Upload Documents")

            photo = st.file_uploader(
                "Upload Profile Photo",
                type=["jpg", "jpeg", "png"]
            )

            marksheet = st.file_uploader(
                "Upload Marksheet",
                type=["jpg", "jpeg", "png", "pdf"]
            )

            # MANUAL MARKS
            st.subheader("3. Enter Your Marks")

            st.caption("Enter the marks exactly as shown in your marksheet.")

            maths = st.number_input("Mathematics", 0, 100, 0)
            physics = st.number_input("Physics", 0, 100, 0)
            chemistry = st.number_input("Chemistry", 0, 100, 0)
            english = st.number_input("English", 0, 100, 0)
            computer = st.number_input("Computer Science", 0, 100, 0)

            # DECLARATION
            agree = st.checkbox(
                "I confirm that the information provided is correct."
            )

            submitted = st.form_submit_button(
                "Submit Application",
                use_container_width=True
            )

        if submitted:

            if not all([
                name.strip(),
                application_id.strip(),
                email.strip(),
                phone.strip(),
                dob,
                photo,
                marksheet
            ]):
                st.error("Please complete all fields and upload both documents.")

            elif not agree:
                st.error("Please accept the declaration before submitting.")

            else:

                applications = load_applications()

                duplicate = any(
                    item["application_id"].lower() == application_id.strip().lower()
                    for item in applications
                )

                if duplicate:
                    st.error("This Application ID has already been submitted.")

                else:

                    photo_filename = f"{uuid.uuid4()}_{Path(photo.name).name}"
                    marksheet_filename = f"{uuid.uuid4()}_{Path(marksheet.name).name}"

                    photo_path = UPLOAD_DIR / photo_filename
                    marksheet_path = UPLOAD_DIR / marksheet_filename

                    photo_path.write_bytes(photo.getvalue())
                    marksheet_path.write_bytes(marksheet.getvalue())

                    record = {
                        "name": name.strip(),
                        "application_id": application_id.strip(),
                        "email": email.strip(),
                        "phone": phone.strip(),
                        "dob": str(dob),
                        "photo_path": str(photo_path.relative_to(BASE_DIR)),
                        "marksheet_path": str(marksheet_path.relative_to(BASE_DIR)),
                        "marks": {
                            "Mathematics": maths,
                            "Physics": physics,
                            "Chemistry": chemistry,
                            "English": english,
                            "Computer Science": computer
                        },
                        "status": "Submitted",
                        "submitted_at": datetime.now().isoformat()
                    }

                    applications.append(record)
                    save_applications(applications)

                    st.success("Application submitted successfully!")
                    st.write("Application ID:", application_id)
                    st.info("Your application is awaiting verifier review.")


# ==========================================
# 8. ADMIN / VERIFIER PORTAL
# ==========================================

else:

    st.title("Verifier / Admin Portal")

    if not st.session_state.admin_logged_in:

        st.subheader("Admin Login")

        username = st.text_input("Admin ID")
        password = st.text_input("Admin Password", type="password")

        if st.button("Admin Login"):

            if username == "admin" and password == "admin123":
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Invalid login. Demo: admin / admin123")

    else:

        st.success("Admin logged in successfully!")

        if st.button("Admin Logout"):
            st.session_state.admin_logged_in = False
            st.rerun()

        applications = load_applications()

        st.divider()
        st.title("Application Dashboard")

        total = len(applications)
        pending = sum(1 for a in applications if a["status"] == "Submitted")
        approved = sum(1 for a in applications if a["status"] == "Approved")
        rejected = sum(1 for a in applications if a["status"] == "Rejected")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Total Applications", total)
        c2.metric("Pending Review", pending)
        c3.metric("Approved", approved)
        c4.metric("Rejected", rejected)

        st.divider()

        st.subheader("Submitted Applications")

        if not applications:
            st.info("No student applications have been submitted yet.")

        else:

            for index, app in enumerate(applications):

                with st.expander(
                    f"{app['name']} — {app['application_id']} | {app['status']}"
                ):

                    left, right = st.columns(2)

                    with left:
                        st.write("**Student Name:**", app["name"])
                        st.write("**Application ID:**", app["application_id"])
                        st.write("**Email:**", app["email"])
                        st.write("**Phone:**", app["phone"])
                        st.write("**Date of Birth:**", app["dob"])
                        st.write("**Submitted:**", app["submitted_at"])

                    with right:
                        st.write("**Profile Photo**")

                        photo_path = BASE_DIR / app["photo_path"]

                        if photo_path.exists():
                            st.image(str(photo_path), width=150)

                        st.write("**Uploaded Marksheet**")

                        marksheet_path = BASE_DIR / app["marksheet_path"]

                        if marksheet_path.exists():
                            if marksheet_path.suffix.lower() == ".pdf":
                                st.download_button(
                                    "Download Marksheet PDF",
                                    data=marksheet_path.read_bytes(),
                                    file_name=marksheet_path.name,
                                    key=f"pdf_{index}"
                                )
                            else:
                                st.image(
                                    str(marksheet_path),
                                    width=250
                                )

                    st.subheader("Manually Entered Marks")

                    st.table({
                        "Subject": list(app["marks"].keys()),
                        "Entered Marks": list(app["marks"].values())
                    })

                    st.write("**Current Status:**", app["status"])

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        if st.button("Approve", key=f"approve_{index}"):
                            app["status"] = "Approved"
                            save_applications(applications)
                            st.success("Application approved.")
                            st.rerun()

                    with col2:
                        if st.button("Reject", key=f"reject_{index}"):
                            app["status"] = "Rejected"
                            save_applications(applications)
                            st.warning("Application rejected.")
                            st.rerun()

                    with col3:
                        if st.button("Delete", key=f"delete_{index}"):
                            st.session_state[f"confirm_delete_{index}"] = True
                            st.rerun()

                    # Ask for confirmation before permanently deleting the application.
                    if st.session_state.get(f"confirm_delete_{index}", False):
                        st.warning(
                            f"Are you sure you want to permanently delete "
                            f"{app['name']}'s application ({app['application_id']})?"
                        )

                        confirm_col, cancel_col = st.columns(2)

                        with confirm_col:
                            if st.button(
                                "Yes, Delete Permanently",
                                key=f"confirm_delete_yes_{index}"
                            ):
                                delete_uploaded_file(app.get("photo_path"))
                                delete_uploaded_file(app.get("marksheet_path"))

                                applications.pop(index)
                                save_applications(applications)

                                st.session_state.pop(
                                    f"confirm_delete_{index}", None
                                )
                                st.success("Application and uploaded documents deleted.")
                                st.rerun()

                        with cancel_col:
                            if st.button(
                                "Cancel",
                                key=f"confirm_delete_no_{index}"
                            ):
                                st.session_state.pop(
                                    f"confirm_delete_{index}", None
                                )
                                st.rerun()


# ==========================================
# 9. FOOTER
# ==========================================

st.divider()

st.caption(
    "Maatram HackForge 2026–27 | Smart Admission Document Validation | Prototype"
)