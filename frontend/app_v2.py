import streamlit as st
import requests
import pandas as pd
# Custom CSS to position the logo and text at the bottom of the Streamlit app content, and increase the box size

footer_html = """
<footer>
  <div style="background-color: #2d3748; padding: 40px 16px; color: white; text-align: center;">
    <p style="font-size: 24px; font-weight: bold;">Streamlining Timesheet</p>
    <div>
      <p style="font-size: 18px;">Built as part of the GovTech {build} Hackathon</p>
    </div>
    <div style="font-size: 14px; margin-top: 10px;">
      <a href="https://www.tech.gov.sg/contact-us/" style="color: white; margin-right: 10px;">Contact Us</a>
      <a href="https://www.tech.gov.sg/report-vulnerability/" style="color: white; margin-right: 10px;">Report Vulnerability</a>
      <a href="https://www.tech.gov.sg/privacy/" style="color: white; margin-right: 10px;">Privacy Statement</a>
      <a href="https://www.tech.gov.sg/terms-of-use/" style="color: white;">Terms of Use</a>
    </div>
    <hr style="border-color: #cbd5e0; margin: 20px 0;">
    <p style="font-size: 14px;">© 2024 Government Technology Agency of Singapore | GovTech</p>
  </div>
</footer>
"""

# Display footer in Streamlit
st.markdown(footer_html, unsafe_allow_html=True)

BASE_URL = "http://ec2-13-250-97-26.ap-southeast-1.compute.amazonaws.com:8001"  # Change this to your actual FastAPI URL

def fetch_service_details(po_line):
    response = requests.get(f"{BASE_URL}/service/{po_line}")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch service details")
        return []

def fetch_job_rates():
    response = requests.get(f"{BASE_URL}/job_rates")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch job rates")
        return []

def update_status(po_line, updates):
    response = requests.put(f"{BASE_URL}/service/{po_line}/status", json=updates)
    if response.status_code == 200:
        st.success("Statuses updated successfully")
    else:
        st.error("Failed to update statuses")

def get_aggregated_amount(po_line):
    response = requests.get(f"{BASE_URL}/service/{po_line}/calculated_amount")
    if response.status_code == 200:
        return response.json().get("total_calculated_amount", 0)
    else:
        return 0

# Function to clear session state and refresh the page
def clear_screen():
    for key in list(st.session_state.keys()):
        del st.session_state[key]  # Clear all session state data
    st.rerun()  # Rerun the app to refresh the page

st.title("Service Details Dashboard")
po_line = st.text_input("Enter PO Line:", value="PO-001")  # Prefill PO line with "PO-001"

if st.button("Fetch Data") and po_line:
    service_data = fetch_service_details(po_line)
    job_rates = fetch_job_rates()
    
    if service_data:
        df = pd.DataFrame(service_data)
        st.session_state.df = df  # Store data in session state
        if "actions" not in st.session_state:
            st.session_state.actions = {i: "pending" for i in range(len(df))}
        if "feedback" not in st.session_state:
            st.session_state.feedback = {}

if "df" in st.session_state:
    df = st.session_state.df
    st.subheader("Service Details")

    updated_data = []
    for i, row in df.iterrows():
        st.write(f"**Row {i + 1}:**")
        
        # Flip the table to long format: each column value will be shown vertically
        flipped_row = row.to_frame().reset_index()
        flipped_row.columns = ["Field", "Value"]
        

        # Convert all values in the "Value" column to string
        flipped_row["Value"] = flipped_row["Value"].apply(str)

        # Display the flipped row as a table
        st.table(flipped_row)
        
        # Create columns for the action buttons beside the row
        col1, col2 = st.columns([1, 1])  # Two columns: one for "Accept" and one for "Reject"
        
        # Get feedback for the row, if any
        feedback_accept = st.session_state.feedback.get(i, {}).get("accept", "")
        feedback_reject = st.session_state.feedback.get(i, {}).get("reject", "")
        
        with col1:
            if st.button(f"Accept", key=f"accept_{i}", help="Click to accept the row"):
                st.session_state.actions[i] = "accept"
                st.session_state.feedback[i] = {"accept": f"Accepted"}
                # Immediately show feedback for this row
                st.success(f"Accepted")

        with col2:
            if st.button(f"Reject", key=f"reject_{i}", help="Click to reject the row"):
                st.session_state.actions[i] = "reject"
                st.session_state.feedback[i] = {"reject": f"Rejected"}
                # Immediately show feedback for this row
                st.error(f"Rejected")

        
        # Show feedback below each row
        if feedback_accept:
            st.success(feedback_accept)
        if feedback_reject:
            st.error(feedback_reject)

        updated_data.append(row)
    
    if st.button("Submit Actions"):
        updates = []
        for i, row in df.iterrows():
            new_status = st.session_state.actions.get(i, "pending")
            new_amount = row["calculated_amount"] if new_status == "accept" else 0
            updates.append({"status": new_status})
            df.at[i, "calculated_amount"] = new_amount
        
        update_status(po_line, updates)
        total_amount = get_aggregated_amount(po_line)
        st.write(f"Total Calculated Amount: {total_amount}")

if "df" in st.session_state and "job_rates" in st.session_state:
    st.subheader("Job Rates")
    # Display the job rates as a cleaner dataframe
    st.dataframe(pd.DataFrame(st.session_state.job_rates))

# Clear button to reset everything
if st.button("Clear Screen"):
    clear_screen()  # Clear session state and refresh the page
