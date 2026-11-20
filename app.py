
import streamlit as st
from datetime import date, datetime

# ==========================================
# IMPORT PROJECT MODULES
# ==========================================

from chatbot import get_gemini_response

from reminders import (
    init_db,
    register_user,
    login_user,
    add_reminder,
    get_reminders,
    delete_reminder
)

from symptom_checker import render_symptom_checker


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Healthcare AI Assistant",
    page_icon="🏥",
    layout="wide"
)


# ==========================================
# INITIALIZE DATABASE
# ==========================================

init_db()


# ==========================================
# SESSION STATE
# ==========================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "username" not in st.session_state:
    st.session_state.username = ""

if "messages" not in st.session_state:
    st.session_state.messages = []


# ==========================================
# APPLICATION HEADER
# ==========================================

def show_header():

    st.markdown(
        """
        <div style="
            background: linear-gradient(90deg, #0f766e, #2563eb);
            padding: 22px;
            border-radius: 12px;
            color: white;
            text-align: center;
        ">
            <h1>🏥 Healthcare AI Assistant</h1>
            <p>Your Smart Personal Healthcare Information Assistant</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")


# ==========================================
# LOGIN AND REGISTRATION PAGE
# ==========================================

def authentication_page():

    show_header()

    st.subheader("Welcome!")

    st.write("Login to your account or create a new account.")

    login_tab, register_tab = st.tabs(
        ["🔐 Login", "📝 Register"]
    )

    # ======================================
    # LOGIN
    # ======================================

    with login_tab:

        st.subheader("Login to Your Account")

        with st.form("login_form"):

            login_username = st.text_input(
                "Username",
                key="login_username"
            )

            login_password = st.text_input(
                "Password",
                type="password",
                key="login_password"
            )

            login_button = st.form_submit_button(
                "Login",
                use_container_width=True
            )

        if login_button:

            if not login_username or not login_password:

                st.warning("Please enter username and password.")

            else:

                user = login_user(
                    login_username,
                    login_password
                )

                if user:

                    st.session_state.logged_in = True
                    st.session_state.user_id = user
                    st.session_state.username = login_username
                    st.session_state.messages = []

                    st.success("Login successful!")

                    st.rerun()

                else:

                    st.error(
                        "Invalid username or password."
                    )

    # ======================================
    # REGISTRATION
    # ======================================

    with register_tab:

        st.subheader("Create a New Account")

        with st.form("register_form"):

            new_username = st.text_input(
                "Choose Username"
            )

            new_password = st.text_input(
                "Choose Password",
                type="password"
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password"
            )

            register_button = st.form_submit_button(
                "Register",
                use_container_width=True
            )

        if register_button:

            if not new_username or not new_password:

                st.warning(
                    "Please fill in all required fields."
                )

            elif new_password != confirm_password:

                st.error("Passwords do not match.")

            elif len(new_password) < 8:

                st.error(
                    "Password must contain at least 8 characters."
                )

            else:

                result = register_user(
                    new_username,
                    new_password
                )

                if result:

                    st.success(
                        "Registration successful! "
                        "Please login using your new account."
                    )

                else:

                    st.error(
                        "Username already exists or registration failed."
                    )


# ==========================================
# DASHBOARD
# ==========================================

def dashboard_page():

    st.title("🏠 Dashboard")

    st.write(
        f"Welcome back, **{st.session_state.username}**!"
    )

    st.write(
        "Manage your healthcare information from one place."
    )

    reminders = get_reminders(
        st.session_state.user_id
    )

    total_reminders = len(reminders)

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "👤 Account",
            "Active"
        )

    with col2:

        st.metric(
            "💊 Total Reminders",
            total_reminders
        )

    with col3:

        st.metric(
            "🤖 AI Assistant",
            "Available"
        )

    st.divider()

    st.subheader("🚀 Quick Access")

    col1, col2 = st.columns(2)

    with col1:

        st.info(
            """
            **🤖 AI Chat**

            Ask general healthcare questions
            and receive AI-generated information.
            """
        )

        st.info(
            """
            **🩺 Symptom Checker**

            Enter your symptoms and receive
            general health information.
            """

        )

    with col2:

        st.info(
            """
            **💊 Medicine Reminders**

            Organize your medicine reminders
            and scheduled times.
            """
        )

        st.info(
            """
            **📚 Health Information**

            Explore educational health topics
            and wellness information.
            """
        )

    st.divider()

    st.subheader("📅 Your Recent Reminders")

    if reminders:

        for reminder in reminders[:5]:

            st.write(
                f"💊 **{reminder[1]}**"
                f" | Date: {reminder[2]}"
                f" | Time: {reminder[3]}"
            )

    else:

        st.info("You don't have any reminders yet.")


# ==========================================
# AI CHAT PAGE
# ==========================================

def ai_chat_page():

    st.title("🤖 Healthcare AI Chat")

    st.write(
        "Ask questions about general healthcare, "
        "wellness and healthy lifestyle."
    )

    st.info(
        "AI responses are for educational purposes only "
        "and are not medical diagnoses."
    )

    st.divider()

    # Display previous messages

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    # Chat input

    user_input = st.chat_input(
        "Ask your healthcare question..."
    )

    if user_input:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_input
            }
        )

        with st.chat_message("user"):

            st.markdown(user_input)

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                try:

                    response = get_gemini_response(
                        user_input
                    )

                    if response:

                        st.markdown(response)

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": response
                            }
                        )

                    else:

                        st.warning(
                            "No response received. Please try again."
                        )

                except Exception as e:

                    st.error(
                        "Unable to connect to AI right now."
                    )

                    st.caption(str(e))

    st.divider()

    if st.button("🗑️ Clear Chat"):

        st.session_state.messages = []

        st.rerun()


# ==========================================
# HEALTH INFORMATION PAGE
# ==========================================

def health_information_page():

    st.title("📚 Health Information")

    st.write(
        "Explore general healthcare and wellness information."
    )

    topics = {

        "🥗 Healthy Lifestyle": """
        ### Healthy Lifestyle

        Maintaining a healthy lifestyle supports overall wellbeing.

        **General Tips:**

        - Eat a balanced and varied diet.
        - Stay physically active.
        - Drink sufficient water.
        - Maintain a regular sleep schedule.
        - Maintain good personal hygiene.
        - Attend routine health checkups.
        """,

        "😴 Sleep Health": """
        ### Sleep Health

        Sleep is important for physical and mental wellbeing.

        **Healthy Sleep Habits:**

        - Maintain a consistent sleep schedule.
        - Create a comfortable sleeping environment.
        - Reduce screen use before bedtime.
        - Avoid excessive caffeine.
        - Follow a relaxing bedtime routine.
        """,

        "💧 Hydration": """
        ### Hydration

        Water helps the body perform important functions.

        **General Tips:**

        - Drink water regularly.
        - Increase fluid intake when needed.
        - Eat fruits and vegetables containing water.
        - Pay attention to signs of dehydration.
        """,

        "🧠 Mental Wellbeing": """
        ### Mental Wellbeing

        Mental wellbeing is an important part of overall health.

        **General Tips:**

        - Maintain supportive relationships.
        - Make time for enjoyable activities.
        - Take breaks during stressful activities.
        - Maintain a healthy daily routine.
        - Talk to a trusted person when you need support.
        """,

        "🏃 Physical Activity": """
        ### Physical Activity

        Regular physical activity supports general health.

        **General Tips:**

        - Choose activities you enjoy.
        - Include movement in your daily routine.
        - Take regular breaks from sitting.
        - Allow adequate time for rest and recovery.
        """
    }

    selected_topic = st.selectbox(
        "Choose a Health Topic",
        list(topics.keys())
    )

    st.divider()

    st.markdown(
        topics[selected_topic]
    )

    st.info(
        "This information is educational and does not replace "
        "individual medical advice."
    )


# ==========================================
# SYMPTOM CHECKER PAGE
# ==========================================

def symptom_checker_page():

    render_symptom_checker()


# ==========================================
# MEDICINE REMINDERS PAGE
# ==========================================

def reminders_page():

    st.title("💊 Medicine Reminders")

    st.write(
        "Create and manage your personal medicine reminders."
    )

    st.divider()

    # ======================================
    # ADD REMINDER
    # ======================================

    st.subheader("➕ Add New Reminder")

    with st.form("add_reminder_form"):

        medicine_name = st.text_input(
            "Medicine / Reminder Name",
            placeholder="Enter reminder name"
        )

        reminder_date = st.date_input(
            "Reminder Date",
            value=date.today(),
            min_value=date.today()
        )

        reminder_time = st.time_input(
            "Reminder Time"
        )

        add_button = st.form_submit_button(
            "Save Reminder",
            use_container_width=True
        )

    if add_button:

        if not medicine_name.strip():

            st.warning(
                "Please enter a reminder name."
            )

        else:

            add_reminder(
                st.session_state.user_id,
                medicine_name.strip(),
                reminder_date.strftime("%Y-%m-%d"),
                reminder_time.strftime("%H:%M")
            )

            st.success(
                "Reminder added successfully!"
            )

            st.rerun()

    st.divider()

    # ======================================
    # DISPLAY REMINDERS
    # ======================================

    st.subheader("📋 Your Saved Reminders")

    reminders = get_reminders(
        st.session_state.user_id
    )

    if reminders:

        for reminder in reminders:

            reminder_id = reminder[0]
            title = reminder[1]
            saved_date = reminder[2]
            saved_time = reminder[3]

            with st.container(border=True):

                col1, col2 = st.columns(
                    [4, 1]
                )

                with col1:

                    st.markdown(
                        f"### 💊 {title}"
                    )

                    st.write(
                        f"📅 Date: {saved_date}"
                    )

                    st.write(
                        f"⏰ Time: {saved_time}"
                    )

                with col2:

                    if st.button(
                        "🗑️ Delete",
                        key=f"delete_{reminder_id}"
                    ):

                        delete_reminder(
                            reminder_id,
                            st.session_state.user_id
                        )

                        st.success(
                            "Reminder deleted successfully."
                        )

                        st.rerun()

    else:

        st.info(
            "No reminders found. Add your first reminder above."
        )


# ==========================================
# MY PROFILE PAGE
# ==========================================

def profile_page():

    st.title("👤 My Profile")

    st.write("Your account information.")

    st.divider()

    st.write(
        f"**Username:** {st.session_state.username}"
    )

    st.write(
        f"**Account Status:** Active"
    )

    st.write(
        f"**User ID:** {st.session_state.user_id}"
    )

    st.divider()

    st.info(
        "Your healthcare assistant account is ready to use."
    )


# ==========================================
# MAIN APPLICATION
# ==========================================

def main():

    # ======================================
    # AUTHENTICATION CHECK
    # ======================================

    if not st.session_state.logged_in:

        authentication_page()

        return

    # ======================================
    # SIDEBAR
    # ======================================

    with st.sidebar:

        st.title("🏥 Healthcare AI")

        st.write(
            f"Welcome, {st.session_state.username}"
        )

        st.divider()

        page = st.radio(
            "Navigation",
            [
                "Dashboard",
                "AI Chat",
                "Symptom Checker",
                "Health Information",
                "Reminders",
                "My Profile"
            ]
        )

        st.divider()

        st.write("⚕️ Healthcare AI Assistant")

        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):

            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.username = ""
            st.session_state.messages = []

            st.rerun()

    # ======================================
    # PAGE ROUTING
    # ======================================

    if page == "Dashboard":

        dashboard_page()

    elif page == "AI Chat":

        ai_chat_page()

    elif page == "Symptom Checker":

        symptom_checker_page()

    elif page == "Health Information":

        health_information_page()

    elif page == "Reminders":

        reminders_page()

    elif page == "My Profile":

        profile_page()


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    main()
