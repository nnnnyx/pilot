import streamlit as st
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os

# Define the scope
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Function to authenticate with OAuth 2.0
def authenticate():
    creds = None
    # Load existing credentials if they exist
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If no valid credentials, prompt the user to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Use a console-based OAuth flow for headless environments
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_console()  # Use run_console() instead of run_local_server()
        # Save the credentials for future use
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

# Google Sheets Setup
def connect_to_google_sheet():
    # Authenticate with OAuth 2.0
    creds = authenticate()
    
    # Authorize the client
    client = gspread.authorize(creds)
    
    # Open the Google Sheet by name
    sheet = client.open("Pilot").sheet1  # Replace with your sheet name
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

        # Endorsement Selection (Multiple Endorsements per Policy)
        endorsements = st.multiselect(
            f"Select endorsements for {policy}:",
            [f"Endorsement {i}" for i in range(1, 14)]  # 13 endorsement options
        )

        # Questions for Each Endorsement
        for endorsement in endorsements:
            st.markdown(f"**{endorsement} Questions**")

            # System's Suggested Audit Resolution
            audit_resolution = st.radio(
                f"What was the system's suggested audit resolution for {endorsement}?",
                ["Yes", "No"],
                key=f"audit_{policy}_{endorsement}"  # Unique key for each radio button
            )

            # Agree with AI's Resolution
            agree_with_ai = st.radio(
                f"Did you agree with the AI's resolution for {endorsement}?",
                ["Yes", "No"],
                key=f"agree_{policy}_{endorsement}"  # Unique key for each radio button
            )

            # Explanation for Resolution
            explanation = st.selectbox(
                f"Please explain your resolution for {endorsement}:",
                [f"Option {i}" for i in range(1, 14)],  # 13 explanation options
                key=f"explain_{policy}_{endorsement}"  # Unique key for each selectbox
            )

            # Store responses for this endorsement
            responses.append({
                "Account Name": account_name,
                "Company Name": company_name,
                "Project Name": project_name,
                "ICS Link": ics_link,
                "Policy": policy,
                "Endorsement": endorsement,
                "Audit Resolution": audit_resolution,
                "Agree with AI": agree_with_ai,
                "Explanation": explanation
            })

    # Submit Button
    if st.button("Submit"):
        if not account_name or not company_name or not project_name or not ics_link:
            st.error("Please fill out all required fields.")
        else:
            try:
                # Connect to Google Sheet
                sheet = connect_to_google_sheet()

                # Prepare data to append
                for response in responses:
                    row = [
                        response["Account Name"],
                        response["Company Name"],
                        response["Project Name"],
                        response["ICS Link"],
                        response["Policy"],
                        response["Endorsement"],
                        response["Audit Resolution"],
                        response["Agree with AI"],
                        response["Explanation"]
                    ]
                    sheet.append_row(row)

                st.success("Form submitted successfully!")
            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
