import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# --- 1. Connection Logic (UPDATED FOR CLOUD) ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# This line pulls the data from your Streamlit Secrets box
creds_dict = st.secrets["gcp_service_account"]

# This line uses the secret data instead of a local file
creds = ServiceAccountCredentials.from_json_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Use the exact name of your sheet here
sheet = client.open("freezonex_data").sheet1

# --- 2. Initialize App Memory ---
if 'page' not in st.session_state:
    st.session_state.page = 'input'

# --- PAGE 1: THE INPUT FORM ---
if st.session_state.page == 'input':
    st.title("Customer Billing Portal")
    
    with st.form("billing_form"):
        name = st.text_input("Customer Name")
        item = st.text_input("Product or Service")
        price = st.number_input("Price (PKR)", min_value=0)
        
        submit_button = st.form_submit_button("Generate Invoice")

    if submit_button:
        if name and item:
            with st.spinner('Saving to Google Sheets...'):
                current_date = datetime.date.today().strftime("%d-%m-%Y")
                sheet.append_row([current_date, name, item, price])
                
                st.session_state.invoice_data = {
                    "date": current_date, "name": name, "item": item, "price": price
                }
                st.session_state.page = 'invoice'
                st.rerun() 
        else:
            st.error("Please fill in the Name and Product fields.")

# --- PAGE 2: THE CLEAN INVOICE ---
elif st.session_state.page == 'invoice':
    res = st.session_state.invoice_data
    
    st.title("📄 OFFICIAL RECEIPT")
    st.markdown("---")
    st.header(f"Customer: {res['name']}")
    st.write(f"**Date:** {res['date']}")
    st.write(f"**Service:** {res['item']}")
    st.write(f"**Total Amount:** {res['price']} PKR")
    st.markdown("---")
    
    if st.button("Add New Entry"):
        st.session_state.page = 'input'
        st.rerun()
