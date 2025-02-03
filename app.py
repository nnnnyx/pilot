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
            try:
                # Use a manual OAuth flow for headless environments
                flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
                # Generate the authorization URL
                auth_url, _ = flow.authorization_url(prompt="consent")
                st.write("Please go to the following URL to authorize the app:")
                st.write(auth_url)
                # Ask the user to enter the authorization code
                auth_code = st.text_input("Enter the authorization code:")
                if auth_code:
                    # Fetch the token using the authorization code
                    flow.fetch_token(code=auth_code)
                    creds = flow.credentials
                    # Save the credentials for future use
                    with open("token.json", "w") as token:
                        token.write(creds.to_json())
                else:
                    st.error("Authorization code is required.")
                    return None
            except Exception as e:
                st.error(f"An error occurred during authentication: {e}")
                return None
    return creds

# Google Sheets Setup
def connect_to_google_sheet():
    # Authenticate with OAuth 2.0
    creds = authenticate()
    if not creds:
        st.error("Authentication failed. Please try again.")
        return None
    
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

    # Named Endorsements
    endorsements_list = [
        "Additional Insured Endorsement",
        "Additional Insured Endorsement for Ongoing Operations",
        "Additional Insured Endorsement for Completed Operations",
        "Primary Non-Contributory Endorsement",
        "Waiver of Subrogation Endorsement",
        "Notice of Cancellation Endorsement",
        "Follow Form Endorsement"
    ]

    # Explanation Options
    explanation_options = [
        "Displayed endorsement doesn't meet the required endo (wrong algorithm)",
        "Tooltip missing a relevant endo from the index (wrong extraction/algorithm)",
        "Tooltip missing a relevant endo not found in the index (wrong extraction)",
        "Tooltip missing relevant manuscript endo not in the index (wrong extraction)",
        "Correct endo identified but there’s a pol numb gap (next algorithm phase)",
        "Correct endo but there's a date gap (next algorithm phase)",
        "Correct endo identified but there's a schedule gap (next algorithm phase)",
        "Correct endo identified but there's a watermark gap (next algorithm phase)",
        "Correct endo identified, but can't be used as AIE for Vendors (next algorithm phase)",
        "Correct endo identified, but can't be used due to overridden gap (next algorithm phase)",
        "Displayed code was extracted from different sources (wrong extraction)",
        "No endorsements were identified, but Follow Form was provided (next algorithm phase)",
        "No endorsements were identified, but provisions were given [For Umbrella Liability Only] (next algorithm phase)"
    ]

    # Dynamic Questions for Selected Policies
    responses = []
    for policy in policies:
        st.subheader(f"{policy} Questions")

        # Endorsement Selection (Multiple Endorsements per Policy)
        endorsements = st.multiselect(
            f"Select endorsements for {policy}:",
            endorsements_list
        )

        # Questions for Each Endorsement
        for endorsement in endorsements:
            st.markdown(f"**{endorsement} Questions**")

            # System's Suggested Audit Resolution
            audit_resolution = st.radio(
                f"What was the system's suggested audit resolution for {endorsement}?",
                ["Yes", "No"],
                index=None,  # No pre-selection
                key=f"audit_{policy}_{endorsement}"  # Unique key for each radio button
            )

            # Agree with AI's Resolution
            agree_with_ai = st.radio(
                f"Did you agree with the AI's resolution for {endorsement}?",
                ["Yes", "No"],
                index=None,  # No pre-selection
                key=f"agree_{policy}_{endorsement}"  # Unique key for each radio button
            )

            # Explanation for Resolution (Optional)
            explanation = st.selectbox(
                f"Please explain your resolution for {endorsement}:",
                [""] + explanation_options,  # Add an empty option
                index=0,  # Default to the empty option
                key=f"explain_{policy}_{endorsement}"  # Unique key for each selectbox
            )

            # Store responses for this endorsement
            if audit_resolution and agree_with_ai:  # Explanation is optional
                responses.append({
                    "Account Name": account_name,
                    "Company Name": company_name,
                    "Project Name": project_name,
                    "ICS Link": ics_link,
                    "Policy": policy,
                    "Endorsement": endorsement,
                    "Audit Resolution": audit_resolution,
                    "Agree with AI": agree_with_ai,
                    "Explanation": explanation if explanation else "No explanation provided"
                })

    # Submit Button
    if st.button("Submit"):
        if not account_name or not company_name or not project_name or not ics_link:
            st.error("Please fill out all required fields.")
        elif not responses:
            st.error("Please answer all endorsement questions.")
        else:
            try:
                # Connect to Google Sheet
                sheet = connect_to_google_sheet()
                if not sheet:
                    st.error("Failed to connect to Google Sheets.")
                    return

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
