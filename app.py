import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets Setup
def connect_to_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("your-credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("Your Google Sheet Name").sheet1  # Replace with your sheet name
    return sheet

# Streamlit App
def main():
    st.title("Policy Endorsement Form")

    # Form Inputs
    account_name = st.text_input("Account Name")
    company_name = st.text_input("Company Name")
    project_name = st.text_input("Project Name")
    ics_link = st.text_input("ICS Link")

    # Policy Selection
    st.subheader("Which policies require endorsements?")
    policies = st.multiselect(
        "Select policies:",
        ["General Liability", "Automobile Liability", "Umbrella Liability", "Worker's Compensation"]
    )

    # Dynamic Questions for Selected Policies
    responses = []
    for policy in policies:
        st.subheader(f"{policy} Questions")

        endorsement_type = st.selectbox(
            f"Endorsement Type for {policy}:",
            [f"Option {i}" for i in range(1, 14)]
        )

        audit_resolution = st.radio(
            f"What was the system's suggested audit resolution for {policy}?",
            ["Yes", "No"]
        )

        agree_with_ai = st.radio(
            f"Did you agree with the AI's resolution for {policy}?",
            ["Yes", "No"]
        )

        explanation = st.selectbox(
            f"Please explain your resolution for {policy}:",
            [f"Option {i}" for i in range(1, 14)]
        )

        # Store responses for this policy
        responses.append({
            "Policy": policy,
            "Endorsement Type": endorsement_type,
            "Audit Resolution": audit_resolution,
            "Agree with AI": agree_with_ai,
            "Explanation": explanation
        })

    # Submit Button
    if st.button("Submit"):
        if not account_name or not company_name or not project_name or not ics_link:
            st.error("Please fill out all required fields.")
        else:
            # Connect to Google Sheet
            sheet = connect_to_google_sheet()

            # Prepare data to append
            for response in responses:
                row = [
                    account_name,
                    company_name,
                    project_name,
                    ics_link,
                    response["Policy"],
                    response["Endorsement Type"],
                    response["Audit Resolution"],
                    response["Agree with AI"],
                    response["Explanation"]
                ]
                sheet.append_row(row)

            st.success("Form submitted successfully!")

if __name__ == "__main__":
    main()
