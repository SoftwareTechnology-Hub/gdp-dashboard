import streamlit as st
import time
from datetime import datetime

st.set_page_config(page_title="Virtual Chemical Lab", layout="wide")

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

# --- Initialize session_state ---
if 'selected_chemicals' not in st.session_state:
    st.session_state.selected_chemicals = {}

# --- Helper Functions ---
def standardize_amount(chemical, amount, unit):
    data = CHEMICAL_DATA[chemical]
    if unit == 'ml':
        volume_l = amount / 1000.0
    else:
        volume_l = amount
    if data['state'] == 'S':
        mass_g = amount * 2.0
        moles = mass_g / data['mm']
    else:
        moles = data['conc'] * volume_l
    return moles

def calculate_reaction(selected_chemicals):
    desc_list = []
    acids = {c: chem for c, chem in selected_chemicals.items() if 'Acid' in chem['type']}
    bases = {c: chem for c, chem in selected_chemicals.items() if 'Base' in chem['type']}
    acid_moles = sum(chem['moles'] for chem in acids.values()) if acids else 0
    base_moles = sum(chem['moles'] for chem in bases.values()) if bases else 0
    if acid_moles and base_moles:
        desc_list.append(f"Neutralization reaction! {min(acid_moles, base_moles):.3f} moles reacted.")
    carbonates = {c: chem for c, chem in selected_chemicals.items() if 'Carbonate' in chem['type']}
    if acids and carbonates:
        co2_moles = min(acid_moles, sum(chem['moles'] for chem in carbonates.values()))
        if co2_moles > 0:
            desc_list.append(f"CO2 gas evolved: {co2_moles:.3f} moles.")
    if not desc_list:
        if len(selected_chemicals) == 1:
            desc_list.append("Single chemical selected. No reaction.")
        else:
            desc_list.append("No known reaction. Simple mixture likely.")
    return ' '.join(desc_list)

def mix_colors(colors):
    r = sum(int(c[1:3],16) for c in colors)//len(colors)
    g = sum(int(c[3:5],16) for c in colors)//len(colors)
    b = sum(int(c[5:7],16) for c in colors)//len(colors)
    return f'#{r:02x}{g:02x}{b:02x}'

# --- Layout ---
left, center, right = st.columns([2,1,2])

# --- Left Panel: Chemical Selection ---
with left:
    st.subheader("Available Chemicals")
    for chem in SAFE_CHEMICALS:
        amt = st.number_input(f"{chem} amount", min_value=0.0, value=10.0, step=1.0, key=f"{chem}_amt")
        unit = st.selectbox(f"Unit for {chem}", ["ml","l"], key=f"{chem}_unit")
        add = st.button(f"Add {chem}", key=f"{chem}_add")
        if add:
            moles = standardize_amount(chem, amt, unit)
            st.session_state.selected_chemicals[chem] = {'amount': amt, 'unit': unit, 'moles': moles, 'type': CHEMICAL_DATA[chem]['type'], 'color': CHEMICAL_DATA[chem]['color']}
            st.success(f"{chem} added (~{moles:.3f} mol)")

    if st.button("Clear Selection"):
        st.session_state.selected_chemicals = {}
        st.success("Selection cleared!")

# --- Center Panel: Beaker Visualization ---
with center:
    st.subheader("Beaker Simulation")
    beaker_placeholder = st.empty()
    if st.session_state.selected_chemicals:
        color = mix_colors([c['color'] for c in st.session_state.selected_chemicals.values()])
        level = min(sum(c['amount'] for c in st.session_state.selected_chemicals.values()), 100)
        beaker_html = f'''
        <div style="width:100px; height:200px; border:2px solid #333; border-radius:5px; background:#fff; position:relative;">
            <div style="position:absolute; bottom:0; width:100%; height:{level*2}px; background:{color};"></div>
        </div>
        '''
        beaker_placeholder.markdown(beaker_html, unsafe_allow_html=True)
    else:
        beaker_placeholder.markdown("<div style='width:100px;height:200px;border:2px solid #333;border-radius:5px;'></div>", unsafe_allow_html=True)

# --- Right Panel: Reaction Output ---
with right:
    st.subheader("Reaction Output")
    if st.button("Mix Selected Chemicals"):
        if not st.session_state.selected_chemicals:
            st.warning("Select at least one chemical!")
        else:
            reaction = calculate_reaction(st.session_state.selected_chemicals)
            output_placeholder = st.empty()
            for i in range(5):
                output_placeholder.info("Reaction in progress" + "."*i)
                time.sleep(0.5)
            output_placeholder.success(reaction)
    
    st.markdown("### Safety Guidelines")
    st.info(
        "- Educational simulator only; do NOT try real reactions.\n"
        "- Hazardous reactions are blocked.\n"
        "- Reaction times and colors are simulated visually."
    )
