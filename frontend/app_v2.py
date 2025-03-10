import streamlit as st
import requests
import pandas as pd

#st.set_page_config(layout="wide")
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

st.markdown("""
    <style>
        /* Light Theme Styles */
        .streamlit-light .reportview-container {
            background-color: #f8f9fa;
            padding: 20px;
        }
        .streamlit-light .stButton>button {
            background-color: #4CAF50;
            color: white;
            font-size: 18px;
            border-radius: 10px;
            padding: 10px 20px;
        }
        .streamlit-light .stTextInput input {
            border-radius: 10px;
            padding: 10px;
        }

        /* Dark Theme Styles */
        .streamlit-dark .reportview-container {
            background-color: #1f1f1f;
            padding: 20px;
        }
        .streamlit-dark .stButton>button {
            background-color: #333333;
            color: white;
            font-size: 18px;
            border-radius: 10px;
            padding: 10px 20px;
        }
        .streamlit-dark .stTextInput input {
            border-radius: 10px;
            padding: 10px;
            background-color: #444444;
            color: white;
        }

    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        /* Light Theme Styles */
        .streamlit-light .stTable th {
            background-color: #4CAF50;
            color: white;
        }
        .streamlit-light .stTable tr:nth-child(odd) {
            background-color: #f2f2f2;
        }
        .streamlit-light .stTable tr:nth-child(even) {
            background-color: #ffffff;
        }
        .streamlit-light .stTable tr:hover {
            background-color: #ddd;
        }

        /* Dark Theme Styles */
        .streamlit-dark .stTable th {
            background-color: #1f1f1f;
            color: white;
        }
        .streamlit-dark .stTable tr:nth-child(odd) {
            background-color: #333333;
        }
        .streamlit-dark .stTable tr:nth-child(even) {
            background-color: #262626;
        }
        .streamlit-dark .stTable tr:hover {
            background-color: #444444;
        }

        /* Table general styling */
        .stTable {
            border-collapse: collapse;
            width: 100%;
            font-size: 14px;
            text-align: left;
        }
        .stTable th, .stTable td {
            padding: 8px 12px;
            border: 1px solid #ddd;
        }
    </style>
""", unsafe_allow_html=True)

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

def update_gro_approval(po_line, updates):
    response = requests.put(f"{BASE_URL}/service/{po_line}/gro_approval", json=updates)
    if response.status_code == 200:
        st.success("Updated successfully")
    else:
        st.error("Failed to update")

def get_aggregated_amount(po_line):
    response = requests.get(f"{BASE_URL}/service/{po_line}/calculated_amount")
    if response.status_code == 200:
        return response.json().get("total_calculated_amount", 0)
    else:
        return 0

st.title("GRO Approval Interface")

# Toggle between selection buttons and manual entry
manual_entry = st.checkbox("Manual Entry")
po_line = "PO-001"  # Default value

if manual_entry:
    po_line = st.text_input("Enter PO Line:", value=po_line)
    
    if st.button("Fetch Data") and po_line:
        service_data = fetch_service_details(po_line)
        job_rates = fetch_job_rates()

        if service_data:
            df = pd.DataFrame(service_data)
            st.session_state.df = df
            if "actions" not in st.session_state:
                st.session_state.actions = {i: "pending" for i in range(len(df))}
            if "feedback" not in st.session_state:
                st.session_state.feedback = {}

else:
    po_lines = ["PO-001", "PO-002", "PO-003", "PO-004"]

    # Dropdown for selecting PO line
    po_line = st.selectbox("Select PO Line", po_lines, index=0)

    # Fetch service details and job rates when a PO line is selected
    if po_line:
        service_data = fetch_service_details(po_line)
        job_rates = fetch_job_rates()
        if service_data:
            df = pd.DataFrame(service_data)
            st.session_state.df = df
            if "actions" not in st.session_state:
                st.session_state.actions = {i: "pending" for i in range(len(df))}
            if "feedback" not in st.session_state:
                st.session_state.feedback = {}



# if st.button("Fetch Data") and po_line:
#     service_data = fetch_service_details(po_line)
#     job_rates = fetch_job_rates()
    
#     if service_data:
#         df = pd.DataFrame(service_data)
#         st.session_state.df = df
#         if "actions" not in st.session_state:
#             st.session_state.actions = {i: "pending" for i in range(len(df))}
#         if "feedback" not in st.session_state:
#             st.session_state.feedback = {}

if "df" in st.session_state:
    df = st.session_state.df
    st.subheader("Service Details")

    updated_data = []
    for i, row in df.iterrows():
        flipped_row = row.to_frame().reset_index()
        flipped_row.columns = ["Field", "Value"]
        flipped_row["Value"] = flipped_row["Value"].apply(str)
        
        # Create a dictionary for renaming fields
        field_mapping = {
            "po_line": "PO Line",
            "company": "Company Name",
            "job_role": "Job Role",
            "service_month": "Service Month",
            "billable_days": "Billable Days",
            "non_billable_days": "Non-Billable Days",
            "service_start_date": "Service Start Date",
            "service_end_date": "Service End Date",
            "calculated_amount": "Calculated Amount",
            "name": "Employee Name",
            "ro_approval": "RO Approval",
            "gro_approval": "GRO Approval",
            "rates_id": "Rate ID",
            "rate": "Rate",
            "yyyy": "Year"
        }

        # Rename the 'Field' column values using the mapping
        flipped_row["Field"] = flipped_row["Field"].map(field_mapping).fillna(flipped_row["Field"])

        # Remove 'rates_id' and 'yyyy' from the DataFrame
        flipped_row = flipped_row[~flipped_row["Field"].isin(["Rate ID", "Year"])]

        # Convert values to string
        flipped_row["Value"] = flipped_row["Value"].apply(str)

        grouped_fields = {
            "Basic Info": ["PO Line", "Company Name", "Job Role"],
            "Service Details": ["Service Month", "Service Start Date", "Service End Date"],
            "Billing": ["Billable Days", "Non-Billable Days", "Calculated Amount"],
            "Approvals": ["RO Approval", "GRO Approval"]
        }

        # Custom CSS to standardize column width
        st.markdown("""
            <style>
            div[data-testid="stTable"] table {
                width: 100% !important;
            }
            div[data-testid="stTable"] table th {
                text-align: left !important;
                width: 50% !important;
            }
            </style>
        """, unsafe_allow_html=True)

        # Display tables in a 2x2 grid
        categories = list(grouped_fields.keys())
        col1, col2 = st.columns(2)

        for i in range(0, len(categories), 2):
            with col1:
                st.subheader(categories[i])
                df1 = flipped_row[flipped_row["Field"].isin(grouped_fields[categories[i]])]
                st.table(df1.set_index("Field"))

            if i + 1 < len(categories):  # Ensure we don't go out of bounds
                with col2:
                    st.subheader(categories[i + 1])
                    df2 = flipped_row[flipped_row["Field"].isin(grouped_fields[categories[i + 1]])]
                    st.table(df2.set_index("Field"))
            
        # Display the table
        #st.table(flipped_row)

        
        col1, col2 = st.columns([1, 1])
        
        feedback_accept = st.session_state.feedback.get(i, {}).get("accept", "")
        feedback_reject = st.session_state.feedback.get(i, {}).get("reject", "")
        
        with col1:
            if st.button(f"Approve Timesheet & Amount", key=f"accept_{i}"):
                st.session_state.actions[i] = "Approved"
         #       st.session_state.feedback[i] = {"accept": "Approved"}
                st.success("Accepted")

        with col2:
            if st.button(f"Reject Timesheet & Amount", key=f"reject_{i}"):
                st.session_state.actions[i] = "Rejected"
         #       st.session_state.feedback[i] = {"reject": "Rejected"}
                st.error("Rejected")

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
            updates.append({"gro_approval": new_status})
            df.at[i, "calculated_amount"] = new_amount
        
        update_gro_approval(po_line, updates)
        total_amount = get_aggregated_amount(po_line)
        st.write(f"Total Calculated Amount: {total_amount}")

if "df" in st.session_state and "job_rates" in st.session_state:
    st.subheader("Job Rates")
    st.dataframe(pd.DataFrame(st.session_state.job_rates))

if st.button("Clear Screen"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
