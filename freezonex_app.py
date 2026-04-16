import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import os

# --- 1. Connection Logic ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

if os.path.exists("frezonex-key.json"):
    creds = ServiceAccountCredentials.from_json_keyfile_name("frezonex-key.json", scope)
else:
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

client = gspread.authorize(creds)
sheet = client.open("freezonex_app_data").sheet1

# --- 2. Initialize App Memory ---
if 'page' not in st.session_state:
    st.session_state.page = 'input'

# --- PAGE 1: THE INPUT FORM ---
if st.session_state.page == 'input':
    st.title("FREEZONEX")
    st.caption("The Height of Quality")
    
    with st.form("billing_form"):
        name = st.text_input("Customer Name")
        number = st.text_input('Customer Phone Number (e.g 0300 1234567)')
        item = st.selectbox("Product type", ['Chiller', 'Freezer', 'Water Cooler', 'Boiler', 'Other'])
        shape = st.selectbox('Select Shape', ['Round', 'Rectangular'])
        capacity = st.selectbox('Capacity in Liters', [50, 100, 150, 200, 250, 300, 500, 700, 1000, 1200, 1500, 2000])
        total_price = st.number_input("Price (PKR)", min_value=0)
        advance_price = st.number_input('Advance price (pkr)', min_value=0)
        
        submit_button = st.form_submit_button("Generate Invoice")

    if submit_button:
        # Check if basic fields are filled
        if not (name and number):
            st.error('Please enter the Customer Name and Phone Number.')
        
        # Check if phone number is valid (must be digits and length of 11)
        elif not number.isdigit() or len(number) != 11:
            st.error('Invalid phone number. It must be exactly 11 digits (e.g., 03001234567).')
        
        else:
            with st.spinner('Saving to Google Sheets...'):
                current_date = datetime.date.today().strftime("%d-%m-%Y")
                
                # 1. Save to Google Sheets
                sheet.append_row([current_date, name, number, item, shape, capacity, total_price, advance_price])
                
                # 2. Store in Session State for the next page
                st.session_state.invoice_data = {
                    "date": current_date, 
                    "name": name, 
                    "number": number, 
                    "item": item, 
                    "shape": shape, 
                    "capacity": capacity, 
                    "total_price": total_price, 
                    "advance_price": advance_price
                }
                
                # 3. Move to Invoice Page
                st.session_state.page = 'invoice'
                st.rerun()

# --- PAGE 2: THE CLEAN INVOICE ---
elif st.session_state.page == 'invoice':
    res = st.session_state.invoice_data
    
    # Calculate the remaining balance
    remaining_balance = res['total_price'] - res['advance_price']
    
    st.title("FREEZONEX (Official Receipt)")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Customer:** {res['name']}")
        st.write(f"**Phone #:** {res['number']}")
    with col2:
        st.write(f"**Date:** {res['date']}")
    
    st.markdown("---")
    st.write(f"**Order Details:** {res['capacity']}L {res['shape']} {res['item']}")
    
    st.subheader("Payment Summary")
    st.write(f"Total Amount: **{res['total_price']} PKR**")
    st.write(f"Advance Paid: **{res['advance_price']} PKR**")
    st.success(f"Remaining Balance: **{remaining_balance} PKR**")
    
    st.markdown("---")
    
    if st.button("Add New Entry"):
        st.session_state.page = 'input'
        st.rerun()

# --- THE FOOTER ---
st.divider()
st.caption("Created by Hafiz Zuhaib Idrees")