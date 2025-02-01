import streamlit as st
import pandas as pd
import os
from datetime import datetime

# File to store responses
RESPONSES_FILE = "form_responses.csv"

# Function to save responses to a CSV file
def save_responses(responses):
    # Create a DataFrame from the responses
    df = pd.DataFrame(responses)
    
    # Add a timestamp to each response
    df["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Check if the file already exists
    if os.path.exists(RESPONSES_FILE):
        # Append to the existing file
        df.to_csv(RESPONSES_FILE, mode="a", header=False, index=False)
    else:
        # Create a new file with headers
        df.to_csv(RESPONSES_FILE, mode="w", header=True, index=False)

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
                # Save responses to the CSV file
                save_responses(responses)
                st.success("Form submitted successfully!")
            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
