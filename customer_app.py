import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# --- 1. Connection Logic ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = st.secrets["gcp_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
# Use the exact name of your sheet here
sheet = client.open("freezonex_data").sheet1

# --- 2. Initialize App Memory ---
if 'page' not in st.session_state:
    st.session_state.page = 'input'

# --- PAGE 1: THE INPUT FORM ---
if st.session_state.page == 'input':
    st.title("Customer Billing Portal")
    
    # We put the form in a variable called 'my_form'
    with st.form("billing_form"):
        name = st.text_input("Customer Name")
        item = st.text_input("Product or Service")
        price = st.number_input("Price (PKR)", min_value=0)
        
        # This is the button you see in your screenshot
        submit_button = st.form_submit_button("Generate Invoice")

    if submit_button:
        if name and item:
            with st.spinner('Saving to Google Sheets...'):
                current_date = datetime.date.today().strftime("%d-%m-%Y")
                sheet.append_row([current_date, name, item, price])
                
                # Save data so we can show it on the next page
                st.session_state.invoice_data = {
                    "date": current_date, "name": name, "item": item, "price": price
                }
                st.session_state.page = 'invoice'
                st.rerun() # This flips the page to the Invoice
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
