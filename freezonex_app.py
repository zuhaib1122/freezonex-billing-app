# --- Updated Form Section ---
with st.form("repair_billing_form", clear_on_submit=True):
    st.subheader("👤 Customer Information")
    name = st.text_input("Customer Name")
    number = st.text_input('Customer Phone (e.g., 03001234567)')
    
    st.divider()
    st.subheader("🏗️ Machine Specifications")
    col1, col2 = st.columns(2)
    with col1:
        item = st.selectbox("Product Type", ['Refrigerator', 'Freezer', 'Chiller', 'Water Cooler'])
        # Replaced Liters/Shape with Cubic Feet
        size_cft = st.selectbox("Size (Cubic Feet)", [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, "Custom"])
        brand = st.text_input("Brand / Model Number")
    
    with col2:
        comp_type = st.selectbox("Compressor Type", ["Reciprocating", "Rotary", "Scroll", "Inverter"])
        comp_cap = st.selectbox("Compressor HP", ["1/8 HP", "1/6 HP", "1/4 HP", "1/3 HP", "1/2 HP", "1 HP", "2 HP+"])
        # Added Watts column[cite: 1]
        watts = st.number_input("Power Consumption (Watts)", min_value=0, step=1)

    st.divider()
    st.subheader("⚡ Technical Readings (For Machine Learning)")
    c3, c4, c5 = st.columns(3)
    with c3:
        s_pressure = st.number_input("Suction PSI", step=0.1)
    with c4:
        d_pressure = st.number_input("Discharge PSI", step=0.1)
    with c5:
        # Keeping Amps as it's useful for power factor calculations with Watts
        amps = st.number_input("Ampere Load", step=0.01)

    # ... [Rest of your submission logic] ...
