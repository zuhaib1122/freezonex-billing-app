import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import requests

# --- 1. SETTINGS & CONNECTION ---
st.set_page_config(page_title="FREEZONEX - Industrial Log", layout="centered")

# MARK: This name must match the name in your [connections.gsheets] secrets!
conn = st.connection("gsheets", type=GSheetsConnection)

# Function to get real-time ambient temp for Lahore (Automated)
def get_ambient_temp(city="Lahore"):
    try:
        res = requests.get(f"https://wttr.in/{city}?format=%t")
        return float(res.text.replace('°C', '').replace('+', '').strip())
    except:
        return 32.0  # Common Pakistan average as fallback

# Initialize Page State
if 'page' not in st.session_state:
    st.session_state.page = 'input'

# --- PAGE 1: SMART DATA INPUT ---
if st.session_state.page == 'input':
    st.title("❄️ FREEZONEX")
    st.caption("The Height of Quality | Industrial Repair & Billing Log")
    
    with st.form("repair_billing_form", clear_on_submit=True):
        st.subheader("👤 Customer Information")
        name = st.text_input("Customer Name")
        # Validation will occur on submit[cite: 1]
        number = st.text_input('Customer Phone (e.g., 03001234567)')
        
        st.divider()
        st.subheader("🏗️ Machine Specifications")
        col1, col2 = st.columns(2)
        with col1:
            item = st.selectbox("Product Type", ['Chiller', 'Freezer', 'Water Cooler', 'Boiler', 'Refrigerator'])
            shape = st.selectbox('Select Shape', ['Round', 'Rectangular', 'Vertical', 'Chest'])
            capacity = st.selectbox('Capacity (Liters)', [50, 100, 150, 200, 250, 300, 500, 700, 1000, 1200, 1500, 2000])
        
        with col2:
            brand = st.text_input("Brand / Model Number")
            comp_type = st.selectbox("Compressor Type", ["Reciprocating", "Rotary", "Scroll", "Inverter"])
            comp_cap = st.selectbox("Compressor HP/Capacity", ["1/8 HP", "1/6 HP", "1/4 HP", "1/3 HP", "1/2 HP", "1 HP", "2 HP+"])

        st.divider()
        st.subheader("⚡ Technical Readings (For Machine Learning)")
        c3, c4, c5 = st.columns(3)
        with c3:
            s_pressure = st.number_input("Suction PSI", help="Low side pressure")
        with c4:
            d_pressure = st.number_input("Discharge PSI", help="High side pressure")
        with c5:
            amps = st.number_input("Ampere Load", step=0.1)

        fault = st.selectbox("Initial Fault", ["Not Cooling", "Overheating", "Gas Leak", "Compressor Dead", "Noisy", "Tripping"])
        diagnosis = st.text_area("Final Fix Applied")

        st.divider()
        st.subheader("💰 Billing")
        total_price = st.number_input("Total Price (PKR)", min_value=0)
        advance_price = st.number_input('Advance Paid (PKR)', min_value=0)
        
        submit_button = st.form_submit_button("Save Data & Generate Invoice")

    if submit_button:
        # Strict Pakistan Phone Validation (11 digits, starts with 03)[cite: 1]
        if not (number.isdigit() and len(number) == 11 and number.startswith("03")):
            st.error('Invalid phone number. Must be 11 digits starting with 03 (e.g., 03211234567).')
        elif not name:
            st.error('Please enter the Customer Name.')
        else:
            with st.spinner('Recording data...'):
                # AUTOMATED VARIABLES[cite: 1]
                current_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                ambient_temp = get_ambient_temp()
                
                # --- PREPARE DATA FOR GOOGLE SHEETS ---
                new_row = pd.DataFrame([{
                    "Timestamp": current_date,
                    "Customer_Name": name,
                    "Phone": number,
                    "Ambient_Temp": ambient_temp,
                    "Product": item,
                    "Shape": shape,
                    "Capacity_L": capacity,
                    "Compressor": comp_type,
                    "HP": comp_cap,
                    "Suction_PSI": s_pressure,
                    "Discharge_PSI": d_pressure,
                    "Amps": amps,
                    "Fault": fault,
                    "Diagnosis": diagnosis,
                    "Total_Price": total_price,
                    "Advance": advance_price
                }])

                # Append to Sheet (Change 'Sheet1' if your tab name is different)
                try:
                    existing_df = conn.read(worksheet="Sheet1")
                    updated_df = pd.concat([existing_df, new_row], ignore_index=True)
                    conn.update(worksheet="Sheet1", data=updated_df)
                    
                    st.session_state.invoice_data = new_row.iloc[0].to_dict()
                    st.session_state.page = 'invoice'
                    st.rerun()
                except Exception as e:
                    st.error(f"Sheet Error: {e}")

# --- PAGE 2: PROFESSIONAL INVOICE ---
elif st.session_state.page == 'invoice':
    res = st.session_state.invoice_data
    remaining = res['Total_Price'] - res['Advance']
    
    st.title("📄 FREEZONEX Receipt")
    st.info(f"Entry saved with Ambient Temperature: {res['Ambient_Temp']}°C")
    
    st.write(f"**Date:** {res['Timestamp']}")
    st.write(f"**Customer:** {res['Customer_Name']} ({res['Phone']})")
    st.markdown("---")
    
    st.subheader("Job Details")
    st.write(f"**Machine:** {res['Capacity_L']}L {res['Shape']} {res['Product']}")
    st.write(f"**Diagnosis:** {res['Diagnosis']}")
    
    st.subheader("Financial Summary")
    st.write(f"Total Amount: **{res['Total_Price']} PKR**")
    st.write(f"Advance Paid: **{res['Advance']} PKR**")
    st.success(f"Remaining Balance: **{remaining} PKR**")
    
    if st.button("Add New Job"):
        st.session_state.page = 'input'
        st.rerun()

st.divider()
st.caption("Data Intelligence System by Hafiz Zuhaib Idrees")
