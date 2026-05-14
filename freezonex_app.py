import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import requests

# --- 1. SETTINGS & CONNECTION ---
st.set_page_config(page_title="FREEZONEX - Industrial Log", layout="centered")

# Establish connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Automated Ambient Temp Function
def get_ambient_temp(city="Lahore"):
    try:
        res = requests.get(f"https://wttr.in/{city}?format=%t")
        return float(res.text.replace('°C', '').replace('+', '').strip())
    except:
        return 32.0  # Fallback temperature

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
        number = st.text_input('Customer Phone (e.g., 03001234567)')
        
        st.divider()
        st.subheader("🏗️ Machine Specifications")
        col1, col2 = st.columns(2)
        with col1:
            item = st.selectbox("Product Type", ['Refrigerator', 'Freezer', 'Chiller', 'Water Cooler'])
            # MODIFIED: Added Size in Cubic Feet
            size_cft = st.selectbox("Size (Cubic Feet)", [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, "Custom"])
            brand = st.text_input("Brand / Model Number")
        
        with col2:
            comp_type = st.selectbox("Compressor Type", ["Reciprocating", "Rotary", "Scroll", "Inverter"])
            comp_cap = st.selectbox("Compressor HP", ["1/8 HP", "1/6 HP", "1/4 HP", "1/3 HP", "1/2 HP", "1 HP", "2 HP+"])
            # MODIFIED: Added Watts
            watts = st.number_input("Power Consumption (Watts)", min_value=0, step=1)

        st.divider()
        st.subheader("⚡ Technical Readings (For Machine Learning)")
        c3, c4, c5 = st.columns(3)
        with c3:
            s_pressure = st.number_input("Suction PSI", step=0.1)
        with c4:
            d_pressure = st.number_input("Discharge PSI", step=0.1)
        with c5:
            amps = st.number_input("Ampere Load", step=0.01)

        fault = st.selectbox("Initial Fault", ["Not Cooling", "Overheating", "Gas Leak", "Compressor Dead", "Noisy", "Tripping"])
        diagnosis = st.text_area("Final Fix Applied")

        st.divider()
        st.subheader("💰 Billing")
        total_price = st.number_input("Total Price (PKR)", min_value=0)
        advance_price = st.number_input('Advance Paid (PKR)', min_value=0)
        
        submit_button = st.form_submit_button("Save Data & Generate Invoice")

    if submit_button:
        # Validation for Pakistan Phone Number
        if not (number.isdigit() and len(number) == 11 and number.startswith("03")):
            st.error('Invalid phone number. Must be 11 digits starting with 03.')
        elif not name:
            st.error('Please enter the Customer Name.')
        else:
            with st.spinner('Recording data...'):
                current_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                ambient_temp = get_ambient_temp()
                
                # --- PREPARE DATA FOR GOOGLE SHEETS ---
                new_row = pd.DataFrame([{
                    "Timestamp": current_date,
                    "Customer_Name": name,
                    "Phone": number,
                    "Ambient_Temp": ambient_temp,
                    "Product": item,
                    "Size_CFT": size_cft,
                    "Watts": watts,
                    "Brand_Model": brand,
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

                try:
                    # Update 'Sheet1' to your actual tab name if needed
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
    st.info(f"Recorded Ambient Temperature: {res['Ambient_Temp']}°C")
    
    st.write(f"**Date:** {res['Timestamp']}")
    st.write(f"**Customer:** {res['Customer_Name']} ({res['Phone']})")
    st.markdown("---")
    
    st.subheader("Job Details")
    st.write(f"**Machine:** {res['Size_CFT']} Cubic Feet {res['Product']}")
    st.write(f"**Brand:** {res['Brand_Model']}")
    st.write(f"**Power Profile:** {res['Watts']} Watts | {res['Amps']} Amps")
    
    st.subheader("Financial Summary")
    st.write(f"Total Amount: **{res['Total_Price']} PKR**")
    st.write(f"Advance Paid: **{res['Advance']} PKR**")
    st.success(f"Remaining Balance: **{remaining} PKR**")
    
    if st.button("Add New Job"):
        st.session_state.page = 'input'
        st.rerun()

st.divider()
st.caption("Data Intelligence System by Hafiz Zuhaib Idrees")
