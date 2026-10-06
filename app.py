import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from urllib.parse import quote
from datetime import datetime
import hashlib

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

from utils.voice import listen_for_voice, speak
from utils.ai import get_safety_advice
from utils.alerts import create_emergency_alert
from utils.risk_prediction import predict_safety_risk


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="SafeHer AI",
    page_icon="🛡️",
    layout="wide"
)


# =========================================================
# DATABASE SETUP
# =========================================================

engine = create_engine(
    "sqlite:///safeher.db",
    connect_args={"check_same_thread": False}
)

Base = declarative_base()



class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    name = Column(
        String,
        nullable=False
    )

    email = Column(
        String,
        unique=True,
        nullable=False
    )

    password = Column(
        String,
        nullable=False
    )


class EmergencyContact(Base):

    __tablename__ = "emergency_contacts"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    name = Column(
        String,
        nullable=False
    )

    phone = Column(
        String,
        nullable=False
    )


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)



# =========================================================
# LOGIN / REGISTER SYSTEM
# =========================================================

def hash_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def show_auth_page():
    st.markdown(
        """
        <style>
        .auth-title {
            font-size: 42px;
            font-weight: 700;
            text-align: center;
            margin-top: 40px;
            margin-bottom: 5px;
        }

        .auth-subtitle {
            font-size: 19px;
            text-align: center;
            margin-bottom: 25px;
        }

        .auth-box {
            max-width: 550px;
            margin: auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="auth-title">🛡️ SafeHer AI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="auth-subtitle">'
        'Your Personal AI Safety Assistant'
        '</div>',
        unsafe_allow_html=True
    )

    auth_tab1, auth_tab2 = st.tabs(
        ["🔐 Login", "📝 Register"]
    )

    with auth_tab1:

        st.subheader("Welcome Back")

        login_email = st.text_input(
            "Email",
            key="login_email"
        )

        login_password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "🔐 Login",
            use_container_width=True,
            key="login_button"
        ):

            if (
                not login_email.strip()
                or not login_password
            ):
                st.warning(
                    "Please enter your email and password."
                )

            else:

                db = Session()

                user = db.query(User).filter(
                    User.email == login_email.strip().lower()
                ).first()

                if (
                    user
                    and user.password
                    == hash_password(login_password)
                ):

                    st.session_state["logged_in"] = True
                    st.session_state["user_id"] = user.id
                    st.session_state["user_name"] = user.name
                    st.session_state["user_email"] = user.email

                    db.close()

                    st.success(
                        "✅ Login successful!"
                    )

                    st.rerun()

                else:

                    db.close()

                    st.error(
                        "❌ Invalid email or password."
                    )

    with auth_tab2:

        st.subheader("Create Your SafeHer AI Account")

        register_name = st.text_input(
            "Full Name",
            key="register_name"
        )

        register_email = st.text_input(
            "Email",
            key="register_email"
        )

        register_password = st.text_input(
            "Password",
            type="password",
            key="register_password"
        )

        register_confirm = st.text_input(
            "Confirm Password",
            type="password",
            key="register_confirm"
        )

        if st.button(
            "📝 Create Account",
            use_container_width=True,
            key="register_button"
        ):

            if (
                not register_name.strip()
                or not register_email.strip()
                or not register_password
                or not register_confirm
            ):

                st.warning(
                    "Please fill in all fields."
                )

            elif register_password != register_confirm:

                st.error(
                    "❌ Passwords do not match."
                )

            elif len(register_password) < 6:

                st.warning(
                    "Password must contain at least 6 characters."
                )

            else:

                db = Session()

                existing_user = db.query(User).filter(
                    User.email
                    == register_email.strip().lower()
                ).first()

                if existing_user:

                    db.close()

                    st.error(
                        "❌ An account with this email already exists."
                    )

                else:

                    new_user = User(
                        name=register_name.strip(),
                        email=register_email.strip().lower(),
                        password=hash_password(
                            register_password
                        )
                    )

                    db.add(new_user)
                    db.commit()

                    db.close()

                    st.success(
                        "✅ Account created successfully! "
                        "Please go to the Login tab."
                    )


if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "user_id" not in st.session_state:
    st.session_state["user_id"] = None

if "user_name" not in st.session_state:
    st.session_state["user_name"] = ""

if "user_email" not in st.session_state:
    st.session_state["user_email"] = ""


if not st.session_state["logged_in"]:

    show_auth_page()

    st.stop()


# =========================================================
# LOGOUT
# =========================================================

logout_col1, logout_col2 = st.columns([8, 1])

with logout_col1:

    st.write(
        f"👋 Welcome, **{st.session_state['user_name']}**"
    )

with logout_col2:

    if st.button(
        "Logout",
        use_container_width=True,
        key="logout_button"
    ):

        st.session_state["logged_in"] = False
        st.session_state["user_id"] = None
        st.session_state["user_name"] = ""
        st.session_state["user_email"] = ""

        st.rerun()


# =========================================================
# SESSION STATE
# =========================================================

if "show_location" not in st.session_state:
    st.session_state["show_location"] = False

if "show_ai" not in st.session_state:
    st.session_state["show_ai"] = False

if "voice_sos" not in st.session_state:
    st.session_state["voice_sos"] = False

if "sos_active" not in st.session_state:
    st.session_state["sos_active"] = False

if "current_location" not in st.session_state:
    st.session_state["current_location"] = (
        "Location not available"
    )

if "latitude" not in st.session_state:
    st.session_state["latitude"] = None

if "longitude" not in st.session_state:
    st.session_state["longitude"] = None

if "sos_history" not in st.session_state:
    st.session_state["sos_history"] = []


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 45px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 20px;
        margin-bottom: 20px;
    }

    .sos-active {
        padding: 20px;
        border-radius: 15px;
        border: 3px solid red;
        text-align: center;
        margin-bottom: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🛡️ SafeHer AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Your Personal AI Safety Assistant'
    '</div>',
    unsafe_allow_html=True
)

st.write(
    "AI-powered personal safety assistance with "
    "emergency contacts, location support, voice SOS, "
    "intelligent safety guidance and ML-based risk prediction."
)

st.divider()


# =========================================================
# SOS ACTIVE STATUS
# =========================================================

if st.session_state["sos_active"]:

    st.markdown(
        """
        <div class="sos-active">
            <h1>🚨 SOS MODE ACTIVE 🚨</h1>
            <p>
                Emergency assistance mode is currently active.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.error(
        "⚠️ Emergency mode is active. "
        "Stay in a safe location and contact "
        "emergency services if you are in immediate danger."
    )


# =========================================================
# MAIN FEATURE BUTTONS
# =========================================================

col1, col2, col3, col4 = st.columns(4)


# =========================================================
# SOS BUTTON
# =========================================================

with col1:

    st.error("🚨 SOS Emergency")

    if not st.session_state["sos_active"]:

        if st.button(
            "ACTIVATE SOS",
            use_container_width=True
        ):

            st.session_state["sos_active"] = True

            st.success(
                "🚨 SOS mode activated!"
            )

            st.rerun()

    else:

        if st.button(
            "🛑 DEACTIVATE SOS",
            use_container_width=True
        ):

            st.session_state["sos_active"] = False

            st.warning(
                "SOS mode deactivated."
            )

            st.rerun()


# =========================================================
# LOCATION BUTTON
# =========================================================

with col2:

    st.info("📍 My Location")

    if st.button(
        "View Location",
        use_container_width=True
    ):

        st.session_state["show_location"] = True

        st.rerun()


# =========================================================
# AI ASSISTANT BUTTON
# =========================================================

with col3:

    st.success("🤖 AI Assistant")

    if st.button(
        "Open AI Assistant",
        use_container_width=True
    ):

        st.session_state["show_ai"] = True

        st.rerun()


# =========================================================
# VOICE SOS BUTTON
# =========================================================

with col4:

    st.warning("🎙️ Voice SOS")

    if st.button(
        "Start Voice SOS",
        use_container_width=True
    ):

        st.session_state["voice_sos"] = True

        st.rerun()


# =========================================================
# FREE SOS EMERGENCY SYSTEM
# =========================================================

if st.session_state["sos_active"]:

    st.divider()

    st.subheader(
        "🚨 Free SOS Emergency Alert System"
    )

    st.write(
        "This SOS system does not require Twilio or "
        "any paid SMS API. It prepares an emergency "
        "message and provides free SMS and phone-call "
        "options through your device."
    )


    # -----------------------------------------------------
    # USER DETAILS
    # -----------------------------------------------------

    sos_col1, sos_col2 = st.columns(2)

    with sos_col1:

        user_name = st.text_input(
            "Your Name",
            value="SafeHer User",
            key="sos_user_name"
        )

    with sos_col2:

        emergency_type = st.selectbox(
            "Emergency Type",
            [
                "SOS",
                "Unsafe Situation",
                "Being Followed",
                "Medical Emergency",
                "Harassment",
                "Other Emergency"
            ],
            key="emergency_type"
        )


    # -----------------------------------------------------
    # LOCATION
    # -----------------------------------------------------

    st.write("### 📍 Current Location")

    st.info(
        st.session_state["current_location"]
    )

    if st.session_state["latitude"] is not None:

        st.write(
            f"**Latitude:** "
            f"{st.session_state['latitude']:.5f}"
        )

        st.write(
            f"**Longitude:** "
            f"{st.session_state['longitude']:.5f}"
        )


    # -----------------------------------------------------
    # LOAD EMERGENCY CONTACTS
    # -----------------------------------------------------

    db = Session()

    emergency_contacts = db.query(
        EmergencyContact
    ).all()

    db.close()


    st.write(
        "### 👥 Emergency Contacts"
    )


    if emergency_contacts:

        for contact in emergency_contacts:

            st.write(
                f"👤 **{contact.name}** — "
                f"📞 {contact.phone}"
            )

    else:

        st.warning(
            "No emergency contacts are saved yet. "
            "Please add contacts below."
        )


    # -----------------------------------------------------
    # CREATE SOS ALERT
    # -----------------------------------------------------

    if st.button(
        "🚨 CREATE SOS ALERT",
        use_container_width=True
    ):

        alert_message = create_emergency_alert(
            user_name=user_name,
            location=st.session_state[
                "current_location"
            ],
            emergency_type=emergency_type
        )


        # Save alert in history

        alert_time = datetime.now().strftime(
            "%d-%m-%Y %I:%M %p"
        )


        st.session_state[
            "sos_history"
        ].append(
            {
                "time": alert_time,
                "type": emergency_type,
                "location": st.session_state[
                    "current_location"
                ],
                "message": alert_message
            }
        )


        st.error(
            "🚨 SOS ALERT CREATED"
        )


        st.subheader(
            "📨 Emergency Message"
        )


        st.code(
            alert_message,
            language="text"
        )


        st.success(
            "✅ Emergency alert has been recorded."
        )


        st.info(
            "📱 Demo Mode: Copy this message and "
            "send it to your trusted emergency contact."
        )


    # -----------------------------------------------------
    # EMERGENCY SERVICES - 112
    # -----------------------------------------------------

    st.write(
        "### 🇮🇳 Emergency Services"
    )

    st.write(
        "If you are in immediate danger, contact "
        "emergency services."
    )


    st.markdown(
        """
        <a href="tel:112">
            <button style="
                width:100%;
                padding:15px;
                background-color:#d32f2f;
                color:white;
                border:none;
                border-radius:10px;
                font-size:18px;
                font-weight:bold;
                cursor:pointer;
            ">
                📞 CALL 112
            </button>
        </a>
        """,
        unsafe_allow_html=True
    )


    # -----------------------------------------------------
    # CONTACT ACTIONS
    # -----------------------------------------------------

    if emergency_contacts:

        st.write(
            "### 📱 Contact Your Trusted People"
        )

        st.info(
            "These buttons use your device's SMS or "
            "phone application. No Twilio account or "
            "paid SMS API is required."
        )


        for contact in emergency_contacts:

            clean_phone = (
                contact.phone
                .replace(" ", "")
                .replace("-", "")
            )


            location_text = (
                st.session_state[
                    "current_location"
                ]
            )


            message = (
                f"🚨 SAFEHER AI SOS ALERT 🚨\n\n"
                f"{user_name} may need immediate help.\n\n"
                f"Emergency Type: {emergency_type}\n\n"
                f"Location: {location_text}\n"
            )


            if st.session_state["latitude"] is not None:

                message += (
                    f"\nLatitude: "
                    f"{st.session_state['latitude']:.5f}"
                    f"\nLongitude: "
                    f"{st.session_state['longitude']:.5f}"
                )


            encoded_message = quote(
                message
            )


            action_col1, action_col2 = st.columns(2)


            with action_col1:

                st.markdown(
                    f"""
                    <a href="sms:{clean_phone}?body={encoded_message}">
                        <button style="
                            width:100%;
                            padding:12px;
                            background-color:#1976d2;
                            color:white;
                            border:none;
                            border-radius:8px;
                            font-size:16px;
                            cursor:pointer;
                        ">
                            📱 SMS {contact.name}
                        </button>
                    </a>
                    """,
                    unsafe_allow_html=True
                )


            with action_col2:

                st.markdown(
                    f"""
                    <a href="tel:{clean_phone}">
                        <button style="
                            width:100%;
                            padding:12px;
                            background-color:#388e3c;
                            color:white;
                            border:none;
                            border-radius:8px;
                            font-size:16px;
                            cursor:pointer;
                        ">
                            📞 CALL {contact.name}
                        </button>
                    </a>
                    """,
                    unsafe_allow_html=True
                )


            st.write("")


    # -----------------------------------------------------
    # IMPORTANT NOTE
    # -----------------------------------------------------

    st.warning(
        "⚠️ Note: A Streamlit web app running on a "
        "laptop cannot silently send an SMS for free "
        "by itself. The SMS button opens the device's "
        "messaging app with the emergency message prepared."
    )


# =========================================================
# VOICE SOS
# =========================================================

if st.session_state["voice_sos"]:

    st.divider()

    st.subheader(
        "🎙️ Voice SOS"
    )

    st.write(
        "Press the button below and speak clearly "
        "into your microphone."
    )


    if st.button(
        "🎙️ Start Listening",
        use_container_width=True
    ):

        with st.spinner(
            "Listening..."
        ):

            spoken_text = listen_for_voice()


        st.write(
            "### 🗣️ You said:"
        )

        st.info(
            spoken_text
        )


        spoken_lower = spoken_text.lower()


        emergency_words = [
            "help",
            "emergency",
            "danger",
            "sos",
            "save me",
            "attack",
            "following me"
        ]


        emergency_detected = any(
            word in spoken_lower
            for word in emergency_words
        )


        if emergency_detected:

            st.session_state[
                "sos_active"
            ] = True


            st.error(
                "🚨 EMERGENCY DETECTED"
            )


            speak(
                "Emergency detected. "
                "Please stay safe."
            )


            st.warning(
                "SafeHer AI detected an emergency "
                "keyword in your voice."
            )


            st.info(
                "SOS mode has been activated."
            )


        else:

            st.success(
                "Voice message received successfully."
            )


# =========================================================
# LOCATION
# =========================================================

if st.session_state["show_location"]:

    st.divider()

    st.subheader(
        "📍 SafeHer AI Location"
    )

    st.write(
        "Enter your current area or city "
        "to display it on the safety map."
    )


    location_name = st.text_input(
        "Enter your location",
        placeholder="Example: Hyderabad",
        key="location_input"
    )


    if st.button(
        "🔎 Find Location",
        use_container_width=True
    ):

        if location_name.strip():

            try:

                geolocator = Nominatim(
                    user_agent="safeher_ai"
                )


                location = geolocator.geocode(
                    location_name
                )


                if location:

                    latitude = location.latitude

                    longitude = location.longitude


                    st.session_state[
                        "current_location"
                    ] = location.address


                    st.session_state[
                        "latitude"
                    ] = latitude


                    st.session_state[
                        "longitude"
                    ] = longitude


                    st.success(
                        f"Location found: "
                        f"{location.address}"
                    )


                    st.write(
                        f"**Latitude:** "
                        f"{latitude:.5f}"
                    )


                    st.write(
                        f"**Longitude:** "
                        f"{longitude:.5f}"
                    )


                    safety_map = folium.Map(
                        location=[
                            latitude,
                            longitude
                        ],
                        zoom_start=14
                    )


                    folium.Marker(
                        [
                            latitude,
                            longitude
                        ],
                        popup=(
                            "📍 SafeHer AI Location"
                        ),
                        tooltip=(
                            "Selected Location"
                        ),
                        icon=folium.Icon(
                            color="red",
                            icon="info-sign"
                        )
                    ).add_to(
                        safety_map
                    )


                    st_folium(
                        safety_map,
                        width=1100,
                        height=500
                    )


                else:

                    st.error(
                        "Location not found."
                    )


            except Exception as error:

                st.error(
                    f"Location error: {error}"
                )


        else:

            st.warning(
                "Please enter a location."
            )


# =========================================================
# AI ASSISTANT
# =========================================================

if st.session_state["show_ai"]:

    st.divider()

    st.subheader(
        "🤖 SafeHer AI Safety Assistant"
    )

    st.write(
        "Describe your situation and SafeHer AI "
        "will provide practical safety guidance."
    )


    question = st.text_area(
        "What is happening?",
        placeholder=(
            "Example: I am walking alone at night "
            "and someone is following me."
        ),
        key="ai_question"
    )


    if st.button(
        "🛡️ Get Safety Guidance",
        use_container_width=True
    ):

        if question.strip():

            with st.spinner(
                "SafeHer AI is analyzing your situation..."
            ):

                advice = get_safety_advice(
                    question
                )


            st.subheader(
                "🛡️ Safety Guidance"
            )


            st.write(
                advice
            )


        else:

            st.warning(
                "Please describe your situation first."
            )


# =========================================================
# AI / ML SAFETY RISK PREDICTION
# =========================================================

st.divider()

st.subheader(
    "🧠 AI Safety Risk Prediction"
)

st.write(
    "Answer the questions below to estimate "
    "your current safety risk."
)


risk_col1, risk_col2 = st.columns(2)


# =========================================================
# RISK INPUTS - COLUMN 1
# =========================================================

with risk_col1:

    is_night = st.checkbox(
        "🌙 Is it currently night?"
    )

    is_alone = st.checkbox(
        "👤 Are you alone?"
    )

    someone_following = st.checkbox(
        "🚶 Is someone following you?"
    )


# =========================================================
# RISK INPUTS - COLUMN 2
# =========================================================

with risk_col2:

    unfamiliar_area = st.checkbox(
        "📍 Are you in an unfamiliar area?"
    )

    low_battery = st.checkbox(
        "🔋 Is your phone battery low?"
    )


# =========================================================
# RISK PREDICTION BUTTON
# =========================================================

if st.button(
    "🧠 Predict Safety Risk",
    use_container_width=True
):

    try:

        risk_level, icon, advice = predict_safety_risk(
            night=is_night,
            alone=is_alone,
            following=someone_following,
            unfamiliar_area=unfamiliar_area,
            low_battery=low_battery
        )


        st.subheader(
            f"{icon} {risk_level}"
        )


        if risk_level == "HIGH RISK":

            st.error(
                advice
            )

            st.warning(
                "🚨 Consider activating SOS and "
                "contacting a trusted person."
            )


        elif risk_level == "MEDIUM RISK":

            st.warning(
                advice
            )


        else:

            st.success(
                advice
            )


    except Exception as error:

        st.error(
            f"Risk prediction error: {error}"
        )


# =========================================================
# EMERGENCY CONTACTS
# =========================================================

st.divider()

st.subheader(
    "👥 Emergency Contacts"
)

st.write(
    "Add trusted people who can be contacted "
    "during an emergency."
)


contact_col1, contact_col2 = st.columns(2)


with contact_col1:

    contact_name = st.text_input(
        "Contact Name",
        key="contact_name"
    )


with contact_col2:

    contact_phone = st.text_input(
        "Contact Phone",
        key="contact_phone"
    )


# =========================================================
# SAVE CONTACT
# =========================================================

if st.button(
    "💾 Save Emergency Contact",
    use_container_width=True
):

    if (
        contact_name.strip()
        and contact_phone.strip()
    ):

        db = Session()


        new_contact = EmergencyContact(
            name=contact_name.strip(),
            phone=contact_phone.strip()
        )


        db.add(
            new_contact
        )


        db.commit()

        db.close()


        st.success(
            f"✅ {contact_name} saved successfully!"
        )


        st.rerun()


    else:

        st.warning(
            "Please enter both name and phone number."
        )


# =========================================================
# DISPLAY SAVED CONTACTS
# =========================================================

st.subheader(
    "📋 Saved Emergency Contacts"
)


db = Session()


contacts = db.query(
    EmergencyContact
).all()


db.close()


if contacts:

    for contact in contacts:

        contact_col1, contact_col2 = st.columns(
            [4, 1]
        )


        with contact_col1:

            st.write(
                f"👤 **{contact.name}** "
                f"— 📞 {contact.phone}"
            )


        with contact_col2:

            st.write(
                f"ID: {contact.id}"
            )


else:

    st.info(
        "No emergency contacts saved yet."
    )


# =========================================================
# SOS ALERT HISTORY
# =========================================================

if st.session_state["sos_history"]:

    st.divider()

    st.subheader(
        "📜 SOS Alert History"
    )

    st.write(
        "Emergency alerts created during this "
        "SafeHer AI session."
    )


    for index, alert in enumerate(
        reversed(
            st.session_state["sos_history"]
        ),
        start=1
    ):

        with st.expander(
            f"🚨 Alert {index} — {alert['time']}"
        ):

            st.write(
                f"**Emergency Type:** "
                f"{alert['type']}"
            )

            st.write(
                f"**Location:** "
                f"{alert['location']}"
            )

            st.code(
                alert["message"],
                language="text"
            )


# =========================================================
# PROJECT FEATURE STATUS
# =========================================================

st.divider()

st.subheader(
    "📊 SafeHer AI Features"
)


status_col1, status_col2, status_col3 = st.columns(3)


with status_col1:

    st.success(
        "✅ SOS Emergency"
    )

    st.success(
        "✅ Emergency Contacts"
    )

    st.success(
        "✅ SQLite Database"
    )


with status_col2:

    st.success(
        "✅ Location Map"
    )

    st.success(
        "✅ Voice SOS"
    )

    st.success(
        "✅ Gemini AI Assistant"
    )


with status_col3:

    st.success(
        "✅ ML Risk Prediction"
    )

    st.success(
        "✅ Free SMS Launcher"
    )

    st.success(
        "✅ Free Phone Call Launcher"
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🛡️ SafeHer AI | AI-powered personal safety assistant"
)