import streamlit as st
import requests
import pandas as pd

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

st.title("Service Details Dashboard")
po_line = st.text_input("Enter PO Line:")

if st.button("Fetch Data") and po_line:
    service_data = fetch_service_details(po_line)
    job_rates = fetch_job_rates()
    
    if service_data:
        df = pd.DataFrame(service_data)
        st.session_state.df = df  # Store data in session state
        if "actions" not in st.session_state:
            st.session_state.actions = {i: "pending" for i in range(len(df))}

if "df" in st.session_state:
    df = st.session_state.df
    st.subheader("Service Details")
    
    updated_data = []
    for i, row in df.iterrows():
        cols = st.columns(len(row) + 2)  # Create columns for each field + action buttons
        for j, value in enumerate(row):
            cols[j].write(value)  # Display data
        
        with cols[-2]:
            if st.button(f"Accept {i}", key=f"accept_{i}"):
                st.session_state.actions[i] = "accept"
        with cols[-1]:
            if st.button(f"Reject {i}", key=f"reject_{i}"):
                st.session_state.actions[i] = "reject"
        
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
    st.dataframe(pd.DataFrame(st.session_state.job_rates))
