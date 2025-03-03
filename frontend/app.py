import streamlit as st
import requests
import pandas as pd

API_URL = "http://ec2-13-250-97-26.ap-southeast-1.compute.amazonaws.com:8000"

st.title("🔍 PO Records Lookup")

# Style adjustments
st.markdown("""
<style>
    .big-font { font-size:20px !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# User input for PO Number
identifier = st.text_input("📌 Enter PO Number:")

if st.button("🔍 Fetch PO Record"):
    if identifier:
        response = requests.get(f"{API_URL}/po/{identifier}")
        
        if response.status_code == 200:
            po_record = response.json()
            st.session_state["po_record"] = po_record
            st.session_state["identifier"] = identifier
            # Display results nicely
            st.markdown('<p class="big-font">✅ PO Record Found:</p>', unsafe_allow_html=True)
            
            # Convert JSON to Pandas DataFrame for tabular display
            df = pd.DataFrame([po_record])
            df = df.melt(var_name="Field", value_name="Value")
            st.dataframe(df)  # Interactive table
            
        else:
            st.error("❌ PO Record not found!")
    else:
        st.warning("⚠️ Please enter a PO Number.")

# Step 2: Allow user to update the "acknowledgement" field
if "po_record" in st.session_state and "identifier" in st.session_state:
    st.subheader("Update Acknowledgement")

    # Prefill with current value, allow editing
    new_acknowledgement = st.text_input("Acknowledgement:", st.session_state["po_record"].get("acknowledgement", "GR approved"))

    # "Send" button to update acknowledgement
    if st.button("Send Acknowledgement Update"):
        update_data = {"acknowledgement": new_acknowledgement}
        response = requests.put(f"{API_URL}/update-acknowledgement/{st.session_state['identifier']}", json=update_data)

        # 🔥 *Check if response contains valid JSON*
        try:
            response_data = response.json()
            if response.status_code == 200:
                st.success(response_data["message"])
            else:
                st.error(f"Error: {response_data.get('detail', 'Unknown error')}")
        except requests.exceptions.JSONDecodeError:
            st.error(f"Error: API returned an invalid response ({response.status_code}). Check FastAPI logs.")
