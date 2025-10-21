import streamlit as st
import time
from datetime import datetime

# --- Page Configuration ---
# Use a darker theme and a simple icon
st.set_page_config(
    page_title="Virtual Chemical Lab", 
    layout="wide", 
    initial_sidebar_state="expanded",
    page_icon="🧪"
)

# --- CSS Styling for a modern, lab-like look ---
st.markdown("""
<style>
/* Main container background */
.main {
    background-color: #f0f2f6; /* Light gray background */
}
/* Header style */
.stApp header {
    background-color: #007bff; /* Primary blue color for header */
    color: white;
}
/* Subheader style */
h2, h3 {
    color: #007bff; /* Blue text for headings */
    border-bottom: 2px solid #007bff20; /* Subtle underline */
    padding-bottom: 5px;
    margin-top: 15px;
}
/* Sidebar style */
[data-testid="stSidebar"] {
    background-color: #ffffff; /* White sidebar */
    box-shadow: 2px 0 5px rgba(0,0,0,0.1);
}
/* Button style */
.stButton>button {
    width: 100%;
    border-radius: 5px;
    margin-top: 5px;
    transition: background-color 0.3s;
}
.stButton>button:hover {
    background-color: #0056b3;
    color: white;
    border-color: #0056b3;
}
/* Beaker styling */
.beaker-container {
    display: flex;
    justify-content: center;
    align-items: flex-end; /* Align to the bottom of the container */
    height: 300px; /* Increased height for better visibility */
    width: 100%;
    margin-top: 20px;
    background-color: #ffffff; /* White background for the beaker area */
    border-radius: 10px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}
.beaker-glass {
    width: 150px; /* Increased size */
    height: 250px; /* Increased size */
    border: 5px solid #333;
    border-radius: 0 0 10px 10px;
    background: #ffffff50; /* Semi-transparent white for glass effect */
    position: relative;
    overflow: hidden;
    margin-bottom: 25px; /* Space from the bottom of its container */
}
.beaker-liquid {
    position: absolute;
    bottom: 0;
    width: 100%;
    transition: height 0.5s ease-out; /* Smooth liquid animation */
    border-radius: 0 0 5px 5px;
    box-shadow: inset 0 0 10px rgba(0,0,0,0.5); /* Inner shadow for depth */
}
/* Log/Output styling */
.log-box {
    background-color: #e9ecef; /* Light gray background for log */
    padding: 10px;
    border-radius: 5px;
    height: 300px; /* Fixed height for log area */
    overflow-y: scroll; /* Scrollable log */
    font-family: monospace;
    font-size: 14px;
    white-space: pre-wrap; /* Ensure text wraps */
}
.stText {
    margin: 0;
    padding: 0;
}

</style>
""", unsafe_allow_html=True)

st.title("🧪 Virtual Chemistry Lab Simulator")
st.markdown("---")

# --- Chemical Data ---
CHEMICAL_DATA = {
    "Water (H2O)": {"mm": 18.02, "type": "Solvent", "conc": 55.5, "state": "L", "color": "#1E90FF"},
    "Sodium chloride (table salt)": {"mm": 58.44, "type": "Ionic Solid", "conc": 0, "state": "S", "color": "#F0F8FF"},
    "Vinegar (dilute acetic acid)": {"mm": 60.05, "type": "Weak Acid", "conc": 0.85, "state": "L", "color": "#FFFACD"},
    "Baking soda (sodium bicarbonate)": {"mm": 84.01, "type": "Carbonate Base", "conc": 0, "state": "S", "color": "#F5F5DC"},
    "Sugar (sucrose)": {"mm": 342.3, "type": "Molecular Solid", "conc": 0, "state": "S", "color": "#FFFAFA"},
    "Ethanol (dilute)": {"mm": 46.07, "type": "Molecular Liquid", "conc": 1.7, "state": "L", "color": "#F0FFFF"},
    "Hydrochloric acid (very dilute)": {"mm": 36.46, "type": "Strong Acid", "conc": 0.1, "state": "L", "color": "#FFE4E1"},
    "Sodium hydroxide (very dilute)": {"mm": 40.00, "type": "Strong Base", "conc": 0.1, "state": "L", "color": "#FAFAD2"},
    "Hydrogen peroxide (3%)": {"mm": 34.01, "type": "Oxidizer", "conc": 0.88, "state": "L", "color": "#F0FFF0"},
    "Bleach (sodium hypochlorite, dilute)": {"mm": 74.44, "type": "Oxidizer", "conc": 0.7, "state": "L", "color": "#ADD8E6"},
    "Ammonia solution (household, dilute)": {"mm": 17.03, "type": "Weak Base", "conc": 1.5, "state": "L", "color": "#E0FFFF"},
    "Calcium carbonate (chalk)": {"mm": 100.09, "type": "Carbonate Solid", "conc": 0, "state": "S", "color": "#FFFAF0"},
    "Copper sulfate (dilute)": {"mm": 159.61, "type": "Ionic Solution", "conc": 0.1, "state": "L", "color": "#4682B4"},
}

SAFE_CHEMICALS = list(CHEMICAL_DATA.keys())

# --- Session State ---
if 'selected_chemicals' not in st.session_state:
    st.session_state.selected_chemicals = {}
if 'log' not in st.session_state:
    st.session_state.log = []

# --- Helper Functions ---
def standardize_amount(chemical, amount, unit):
    data = CHEMICAL_DATA[chemical]
    
    # Standardize liquid amount to Liters
    if data['state'] == 'L':
        volume_l = amount / 1000.0 if unit == 'ml' else amount
        moles = data['conc'] * volume_l
    # Standardize solid amount to Grams (assuming input 'g' or arbitrary mass/volume ratio)
    else: # data['state'] == 'S'
        # For simplicity, assume solid input is in 'g' or an equivalent measure
        mass_g = amount
        moles = mass_g / data['mm']
    
    return moles

def calculate_reaction(selected):
    desc = []
    acids = {c: chem for c, chem in selected.items() if 'Acid' in chem['type']}
    bases = {c: chem for c, chem in selected.items() if 'Base' in chem['type']}
    carbonates = {c: chem for c, chem in selected.items() if 'Carbonate' in chem['type']}
    solids = {c: chem for c, chem in selected.items() if chem['state']=='S' and 'Acid' not in chem['type'] and 'Base' not in chem['type']}

    # Calculate total reactive moles
    acid_moles = sum(c['moles'] for c in acids.values()) if acids else 0
    base_moles = sum(c['moles'] for c in bases.values()) if bases else 0
    
    reaction_happened = False
    
    # 1. Acid-Base Neutralization
    if acid_moles > 0 and base_moles > 0:
        min_moles = min(acid_moles, base_moles)
        desc.append(f"**Neutralization!** Salt and water formed. Reacted: $\\approx {min_moles:.3f}$ mol")
        reaction_happened = True

    # 2. Acid-Carbonate Reaction (CO2 gas)
    if acids and carbonates:
        total_carbonate_moles = sum(c['moles'] for c in carbonates.values())
        co2_moles = min(acid_moles, total_carbonate_moles)
        if co2_moles > 0:
            desc.append(f"**Gas Evolution!** $\\text{CO}_2$ gas bubbled off: $\\approx {co2_moles:.3f}$ mol")
            reaction_happened = True

    # 3. Dissolution (Solid in water)
    if 'Water (H2O)' in selected and solids:
        for s_name, s_data in solids.items():
            # Check if solid is soluble (for simplicity, we assume the selected solids are soluble enough)
            if s_data['moles'] > 0:
                desc.append(f"**Dissolving!** {s_name} dissolved in water ($\\approx {s_data['moles']:.3f}$ mol)")
                reaction_happened = True
    
    # 4. Specific Precipitation Example (Copper Sulfate + Base)
    if 'Copper sulfate (dilute)' in selected and bases:
        desc.append("**Precipitation!** Blue copper hydroxide solid formed. (Simplified)")
        reaction_happened = True

    if not desc:
        if len(selected)==1:
            desc.append("Single chemical selected. No reaction.")
        else:
            desc.append("No known reaction. Likely a simple mixture or dissolution.")
            
    if reaction_happened:
        return "<span style='color:red; font-weight:bold;'>REACTION OCCURRED!</span> " + ' | '.join(desc)
    else:
        return ' | '.join(desc)

def mix_colors(colors):
    # Simple color averaging for a mixture effect
    r = sum(int(c[1:3],16) for c in colors)//len(colors)
    g = sum(int(c[3:5],16) for c in colors)//len(colors)
    b = sum(int(c[5:7],16) for c in colors)//len(colors)
    return f'#{r:02x}{g:02x}{b:02x}'


# --- Sidebar: Chemical Selection ---
with st.sidebar:
    st.header("🧪 Chemical Inventory")
    st.markdown("Use the controls below to **add chemicals** to your virtual beaker.")
    
    for chem in SAFE_CHEMICALS:
        expander = st.expander(f"**{chem}**", expanded=False)
        data = CHEMICAL_DATA[chem]
        with expander:
            # Display chemical info
            st.markdown(f"**Type:** {data['type']} | **MM:** {data['mm']} g/mol | **State:** {data['state']}")
            
            col_amt, col_unit = st.columns([2, 1])
            with col_amt:
                amt = st.number_input(
                    "Amount", 
                    min_value=0.0, 
                    value=10.0, 
                    step=1.0, 
                    key=f"{chem}_amt",
                    label_visibility="collapsed"
                )
            with col_unit:
                # Units depend on state: ml/l for Liquid, g for Solid
                unit_options = ["ml", "l"] if data['state'] == 'L' else ["g"]
                unit = st.selectbox(
                    "Unit", 
                    unit_options, 
                    key=f"{chem}_unit",
                    label_visibility="collapsed"
                )
            
            if st.button(f"Add **{chem}**", key=f"{chem}_add", use_container_width=True):
                moles = standardize_amount(chem, amt, unit)
                st.session_state.selected_chemicals[chem] = {
                    'amount': amt, 
                    'unit': unit, 
                    'moles': moles, 
                    'type': data['type'], 
                    'color': data['color'], 
                    'state': data['state']
                }
                st.session_state.log.append(f"💧 Added {amt} {unit} of {chem} (≈{moles:.3f} mol)")
                st.sidebar.success(f"Added {chem}!")


    st.markdown("---")
    if st.button("🗑️ Clear Beaker & Selection", use_container_width=True, type="primary"):
        st.session_state.selected_chemicals = {}
        st.session_state.log.append(f"✅ Selection and Beaker cleared.")
        st.experimental_rerun()


# --- Main Layout ---
col1, col2 = st.columns([1, 1])

# --- Column 1: Beaker Simulation & Reaction Trigger ---
with col1:
    st.header("🔬 Virtual Beaker")

    # Display Beaker Simulation
    beaker_html = ""
    total_volume_ml = sum(c['amount'] for c in st.session_state.selected_chemicals.values() if c['state'] == 'L')
    total_solid_g = sum(c['amount'] for c in st.session_state.selected_chemicals.values() if c['state'] == 'S')
    
    # Max safe volume for visualization (e.g., 200 ml)
    max_volume_viz = 200.0
    
    if st.session_state.selected_chemicals:
        liquid_level_ml = total_volume_ml
        
        # Calculate liquid height percentage (max 100% for 250px high beaker)
        liquid_height_percent = min((liquid_level_ml / max_volume_viz) * 100, 100)
        
        # Mix colors and set a minimum height for visibility
        color = mix_colors([c['color'] for c in st.session_state.selected_chemicals.values()])
        
        if liquid_level_ml == 0 and total_solid_g > 0:
            # If only solids, show a small colored pile at the bottom (min 5% height)
            liquid_height_percent = 5 
        elif liquid_level_ml > 0:
            # Ensure a minimum height if liquid is present
            liquid_height_percent = max(liquid_height_percent, 10)
        else:
            liquid_height_percent = 0
            
        
        beaker_html = f'''
        <div class="beaker-container">
            <div class="beaker-glass">
                <div class="beaker-liquid" style="height:{liquid_height_percent}%; background:{color};"></div>
            </div>
        </div>
        '''
        st.markdown(beaker_html, unsafe_allow_html=True)
        
        st.markdown(f"**Total Volume/Mass:** {total_volume_ml:.2f} mL (Liquid) | {total_solid_g:.2f} g (Solid)")

    else:
        st.markdown("""
        <div class="beaker-container">
            <div class="beaker-glass"></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("**Status:** Empty Beaker. Add chemicals from the sidebar.")


    st.markdown("---")
    
    if st.button("▶️ **START REACTION (Mix)**", use_container_width=True, type="primary"):
        if not st.session_state.selected_chemicals:
            st.warning("Select chemicals first!")
        else:
            # Simulation of mixing time
            with st.spinner('Mixing chemicals and calculating reaction...'):
                time.sleep(1) # Simulate a small delay
                reaction = calculate_reaction(st.session_state.selected_chemicals)
                st.session_state.log.append(f"💥 Reaction: {reaction}")
                st.success("Reaction analysis complete!")
    
    st.markdown("---")

    st.subheader("Selected Chemicals")
    if st.session_state.selected_chemicals:
        # Generate a list for the dataframe
        display_data = []
        for name, data in st.session_state.selected_chemicals.items():
            amount_display = f"{data['amount']} {data['unit']}"
            moles_display = f"{data['moles']:.3f}"
            display_data.append({
                "Chemical": name,
                "Amount": amount_display,
                "Type": data['type'],
                "Moles (approx)": moles_display
            })
            
        st.dataframe(
            display_data,
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No chemicals selected yet.")


# --- Column 2: Log and Reaction Details ---
with col2:
    st.header("📊 Reaction Log & Safety")
    
    # Reaction Output (placed above the log)
    st.subheader("Final Observation")
    if st.session_state.log and "Reaction: " in st.session_state.log[-1]:
        output = st.session_state.log[-1].split("Reaction: ")[1]
        st.markdown(f"### **Latest Result:**")
        st.markdown(output, unsafe_allow_html=True)
    else:
        st.markdown("Awaiting first reaction...")

    st.markdown("---")
    
    # Log Box
    st.subheader("Activity Log")
    log_content = "\n".join(st.session_state.log)
    
    # FIX: Pre-process the content to move the .replace() outside the f-string expression
    html_log_content = log_content.replace("\n", "<br>")
    st.markdown(f'<div class="log-box">{html_log_content}</div>', unsafe_allow_html=True)


    st.markdown("---")
    st.subheader("Safety Guidelines")
    st.info(
        "**⚠️ IMPORTANT:**\n\n"
        "- This is an **educational simulator only**. Do NOT attempt any of these reactions in a real-world setting.\n"
        "- The simulator is simplified. **Hazardous reactions are generally blocked**.\n"
        "- **Reactions, color changes, and volumes are approximations** for learning purposes."
    )
