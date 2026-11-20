
import streamlit as st
from chatbot import get_gemini_response


def render_symptom_checker():

    st.title("🩺 Symptom Information Checker")

    st.write(
        "Enter your symptoms to receive general educational "
        "health information."
    )

    st.info(
        "This tool is for educational purposes only. "
        "It cannot diagnose medical conditions or replace "
        "advice from a qualified healthcare professional."
    )

    st.warning(
        "If you have severe symptoms such as difficulty breathing, "
        "chest pain, fainting, a severe allergic reaction, or sudden "
        "weakness or confusion, seek emergency medical help immediately."
    )

    st.divider()

    symptoms = st.text_area(
        "Describe the symptoms",
        placeholder="Example: I have a sore throat and a mild cough.",
        height=130,
        max_chars=1000
    )

    duration = st.selectbox(
        "How long have you experienced these symptoms?",
        [
            "Select duration",
            "Less than 24 hours",
            "1–3 days",
            "4–7 days",
            "More than a week",
            "Not sure"
        ]
    )

    if st.button("Check Health Information", type="primary"):

        if not symptoms.strip():
            st.warning("Please enter your symptoms first.")

        elif duration == "Select duration":
            st.warning("Please select how long you have experienced them.")

        else:

            prompt = f"""
You are a responsible healthcare education assistant.

The user has entered the following symptoms:
{symptoms}

Duration:
{duration}

Your task is to provide GENERAL EDUCATIONAL INFORMATION only.

Follow these rules strictly:

1. Do not diagnose the user or claim they have a disease.
2. Do not prescribe medicines or provide medication dosages.
3. Explain possible general reasons for these symptoms without
   claiming that any particular reason applies to the user.
4. Suggest general questions the user could discuss with a
   qualified healthcare professional.
5. Explain that persistent, worsening, or concerning symptoms
   should be assessed by a qualified healthcare professional.
6. Do not claim that the user is safe or that their symptoms
   are harmless.
7. Do not replace professional medical advice.
8. Use simple, understandable language.
9. Do not ask for the user's name, address, phone number,
   or other identifying information.

Use this response structure:

### General Information
Explain what these symptoms can generally be associated with.

### Possible General Causes
List a few possible explanations without diagnosing.

### When to Seek Medical Advice
Explain when the user should contact a healthcare professional.

### Questions to Discuss with a Doctor
Give a few useful questions.

End with a short reminder that this is educational information,
not a medical diagnosis.
"""

            with st.spinner("Preparing health information..."):

                try:
                    response = get_gemini_response(prompt)

                    st.subheader("Health Information")

                    st.markdown(response)

                    st.caption(
                        "This information is educational only. "
                        "Please consult a qualified healthcare "
                        "professional for personal medical advice."
                    )

                except Exception:
                    st.error(
                        "Unable to retrieve information right now. "
                        "Please try again later."
                    )
