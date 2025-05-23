import streamlit as st
import json
import os
import importlib
from stl_volume_calculator import calculate_stl_volume
importlib.reload(importlib.import_module('stl_volume_calculator'))
from stl_volume_calculator import calculate_stl_volume
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import pandas as pd

# Set page config
st.set_page_config(
    page_title="Formlabs Manufacturing on Demand",
    page_icon="formlabs_logo.jpg",
    layout="wide"
)

# Custom CSS with Formlabs branding and Source Sans Pro font
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css?family=Source+Sans+Pro:400,600,700&display=swap');
    html, body, [class*="st-"] {
        font-family: 'Source Sans Pro', sans-serif !important;
    }
    /* Formlabs Colors */
    :root {
        --formlabs-orange: #ff5a00;
        --formlabs-white: #fff;
        --formlabs-black: #1a1918;
    }
    /* Global Styles */
    .stApp {
        background-color: var(--formlabs-white);
        font-family: 'Source Sans Pro', sans-serif !important;
    }
    /* Headers */
    h1, h2, h3 {
        color: var(--formlabs-black) !important;
        font-family: 'Source Sans Pro', sans-serif !important;
    }

    /* Material Cards */
    .material-card {
        background: var(--formlabs-white);
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .material-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        border-color: var(--formlabs-orange);
    }

    /* Material Image */
    .material-image {
        border-radius: 8px;
        object-fit: contain;
        background: #f8f8f8;
        padding: 10px;
    }

    /* Material Name */
    .material-name {
        color: var(--formlabs-black);
        font-size: 1.2em;
        font-weight: 600;
        margin: 10px 0;
    }

    /* Material Price */
    .material-price {
        color: var(--formlabs-orange);
        font-size: 1.4em;
        font-weight: 700;
        margin: 10px 0;
    }

    /* Material Tags */
    .material-tag {
        background-color: #f5f5f5;
        color: var(--formlabs-black);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8em;
        margin: 2px;
        display: inline-block;
    }

    /* Buttons */
    .stButton>button {
        background-color: var(--formlabs-orange);
        color: var(--formlabs-white);
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #e64d00;
        box-shadow: 0 4px 8px rgba(255,90,0,0.2);
    }

    /* File Uploader */
    .stFileUploader>div {
        border: 2px dashed #e0e0e0;
        border-radius: 12px;
        padding: 20px;
    }

    .stFileUploader>div:hover {
        border-color: var(--formlabs-orange);
    }

    /* Radio Buttons */
    .stRadio>div {
        background-color: #f8f8f8;
        padding: 15px;
        border-radius: 12px;
    }

    /* Success Message */
    .stSuccess {
        background-color: #e6f4ea;
        border-radius: 8px;
        padding: 15px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #f8f8f8;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--formlabs-orange);
        color: var(--formlabs-white);
    }

    .landing-header {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        padding: 0 0 2rem 0;
    }
    .formlabs-logo {
        height: 40px;
    }
    .headline {
        font-size: 2.8rem;
        font-weight: 700;
        color: #1a1918;
        margin-bottom: 1rem;
        text-align: center;
    }
    .subheadline {
        font-size: 1.3rem;
        color: #444;
        margin-bottom: 2.5rem;
        text-align: center;
    }
    .dashed-box {
        border: 2px dashed #ff5a00;
        border-radius: 16px;
        padding: 2rem 2rem 2.5rem 2rem;
        background: #fff;
        max-width: 500px;
        margin: 0 auto 1.5rem auto;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .file-types {
        color: #1a1918;
        font-size: 1.1rem;
        margin-bottom: 1.2rem;
        letter-spacing: 0.5px;
    }
    .launch-btn {
        background: #ff5a00;
        color: #fff;
        border: none;
        border-radius: 8px;
        padding: 1rem 2.5rem;
        font-size: 1.3rem;
        font-weight: 700;
        margin-top: 2rem;
        cursor: pointer;
        transition: background 0.2s;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    .launch-btn:hover {
        background: #e64d00;
    }
    .center-btn {
        display: flex;
        justify-content: center;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

def load_materials():
    with open('materials_normalized.json', 'r') as f:
        return json.load(f)

def get_unit_display(material):
    """Get the appropriate unit display based on material type"""
    tags = [t.lower() for t in material.get('tags', [])]
    if 'sls' in tags:
        return "kg"
    return "L"

def create_material_card(material, select_callback=None, button_key=None):
    image_url = material['image_url']
    if image_url.startswith('/'):
        image_url = f"https://formlabs.com{image_url}"
    unit = get_unit_display(material)
    st.markdown(f"""
    <div class="material-card">
        <div style="display: flex; gap: 20px;">
            <div style="flex: 1;">
                <img src="{image_url}" class="material-image" width="150" alt="{material['name']}">
            </div>
            <div style="flex: 2;">
                <div class="material-name">{material['name']}</div>
                <div class="material-price">${material['normalized_price_per_kg_or_l']}/{unit}</div>
                <div style="margin-top: 10px;">
                    {''.join([f'<span class="material-tag">{tag}</span>' for tag in material['tags']])}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    # Button inside card
    selected = st.button(f"Select {material['name']}", key=button_key, use_container_width=True)
    if selected and select_callback:
        select_callback(material)
    st.markdown("</div>", unsafe_allow_html=True)

def generate_pdf(volume, material, cost):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Add Formlabs branding
    c.setFillColorRGB(1, 0.35, 0)  # Formlabs orange
    c.rect(0, 750, 612, 50, fill=True)
    
    # Add title
    c.setFont("Helvetica-Bold", 24)
    c.setFillColorRGB(1, 1, 1)  # White
    c.drawString(50, 770, "Formlabs Manufacturing on Demand")
    
    # Add details
    c.setFont("Helvetica", 12)
    c.setFillColorRGB(0.1, 0.1, 0.1)  # Dark gray
    y = 650
    c.drawString(50, y, f"Material: {material['name']}")
    y -= 20
    c.drawString(50, y, f"Volume: {volume:.2f} cm³")
    y -= 20
    unit = get_unit_display(material)
    c.drawString(50, y, f"Price per {unit}: ${material['normalized_price_per_kg_or_l']}")
    y -= 20
    c.drawString(50, y, f"Total Cost: ${cost:.2f}")
    
    c.save()
    buffer.seek(0)
    return buffer

def landing_page():
    st.markdown("""
    <style>
    .headline {
        font-size: 2.8rem;
        font-weight: 700;
        color: #1a1918;
        margin-bottom: 1rem;
        text-align: center;
        font-family: 'Source Sans Pro', sans-serif !important;
    }
    .subheadline {
        font-size: 1.3rem;
        color: #444;
        margin-bottom: 2.5rem;
        text-align: center;
        font-family: 'Source Sans Pro', sans-serif !important;
    }
    .dashed-box {
        border: 2px dashed #ff5a00;
        border-radius: 16px;
        padding: 2rem 2rem 2.5rem 2rem;
        background: #fff;
        max-width: 500px;
        margin: 0 auto 1.5rem auto;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .file-types {
        color: #1a1918;
        font-size: 1.1rem;
        margin-bottom: 1.2rem;
        letter-spacing: 0.5px;
    }
    .launch-btn {
        background: #ff5a00;
        color: #fff;
        border: none;
        border-radius: 8px;
        padding: 1rem 2.5rem;
        font-size: 1.3rem;
        font-weight: 700;
        margin-top: 2rem;
        cursor: pointer;
        transition: background 0.2s;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    .launch-btn:hover {
        background: #e64d00;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="subheadline">Access a wide range of 3D printing materials and instant quoting.<br>Upload your STL file, select your material, and get a quote in seconds.</div>',
        unsafe_allow_html=True,
    )

    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.markdown(
            """
            <div class="dashed-box">
                <div style="font-weight:600; margin-bottom:0.5rem;">
                    Get instant pricing.
                </div>
                <div class="file-types">
                    Supported file types: STL
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        launch = st.button("🚀 Start Your Instant Quote", key="launch", help="Begin your quote", use_container_width=True)
        if launch:
            st.session_state.step = 1
            st.experimental_rerun()
    return False

def is_sla(material):
    tags = [t.lower() for t in material.get('tags', [])]
    return 'sla' in tags

def main():
    st.title("Formlabs Manufacturing on Demand")
    
    # Initialize session state
    if 'step' not in st.session_state:
        st.session_state.step = 0
    if 'volume' not in st.session_state:
        st.session_state.volume = None
    if 'selected_material' not in st.session_state:
        st.session_state.selected_material = None
    if 'stl_units' not in st.session_state:
        st.session_state.stl_units = 'mm'
    
    # Step 0: Landing Page
    if st.session_state.step == 0:
        cta = landing_page()
        if cta:
            st.session_state.step = 1
            st.experimental_rerun()
        return
    
    # Step 1: File Upload
    if st.session_state.step == 1:
        st.header("Step 1: Upload STL File")
        
        # Add unit selection
        stl_units = st.radio(
            "Select the units of your STL file:",
            options=['mm', 'cm', 'inches'],
            horizontal=True,
            help="This helps us calculate the correct volume. Most CAD software exports in millimeters (mm)."
        )
        st.session_state.stl_units = stl_units
        
        uploaded_file = st.file_uploader("Upload STL file", type=['stl'])
        
        if uploaded_file is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.stl') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            try:
                volume = calculate_stl_volume(tmp_file_path, units=stl_units)
                st.session_state.volume = volume
                st.success(f"STL Volume: {volume:.2f} cm³")
                if st.button("Continue to Material Selection"):
                    st.session_state.step = 2
                    st.experimental_rerun()
            except Exception as e:
                st.error(str(e))
            finally:
                os.unlink(tmp_file_path)
    
    # Step 2: Material Selection
    elif st.session_state.step == 2:
        st.header("Step 2: Select Material")
        materials = load_materials()
        # Sort materials by price ascending
        sla_materials = sorted(materials['sla'], key=lambda m: m['normalized_price_per_kg_or_l'])
        sls_materials = sorted(materials['sls'], key=lambda m: m['normalized_price_per_kg_or_l'])
        if 'quote_items' not in st.session_state:
            st.session_state['quote_items'] = []
        def select_material_callback(material):
            st.session_state.selected_material = material
            st.session_state.step = 3
            st.session_state['quote_items'].append({
                'material': material,
                'volume': st.session_state.volume,
                'quantity': 1
            })
            st.experimental_rerun()
        sla_tab, sls_tab = st.tabs(["SLA Materials", "SLS Materials"])
        with sla_tab:
            for material in sla_materials:
                create_material_card(material, select_callback=select_material_callback, button_key=f"sla_{material['name']}")
        with sls_tab:
            for material in sls_materials:
                create_material_card(material, select_callback=select_material_callback, button_key=f"sls_{material['name']}")
    
    # Step 3: Quote Summary and PDF Generation
    elif st.session_state.step == 3:
        st.header("Step 3: Quote Summary")
        quote_items = st.session_state.get('quote_items', [])
        # Build line items with delete buttons inline in table
        line_items = []
        part_indices = []  # Track indices of main part rows for delete
        for idx, item in enumerate(quote_items):
            material = item['material']
            volume = item['volume']
            quantity = 1  # Always 1 now
            unit = get_unit_display(material)
            part_cost = volume * material['normalized_price_per_kg_or_l'] / 1000
            desc = f"Cost of part printed in {material['name']} ({volume:.2f} cm³)"
            line_items.append({
                'description': desc,
                'quantity': quantity,
                'price': part_cost * quantity,
                'is_support': False,
                'material_name': material['name'],
                'item_idx': idx
            })
            part_indices.append(len(line_items)-1)
            # Add SLA support generation if needed
            if is_sla(material):
                support_cost = part_cost * 0.3 * quantity
                line_items.append({
                    'description': f"Support Generation for {material['name']}",
                    'quantity': quantity,
                    'price': support_cost,
                    'is_support': True,
                    'material_name': material['name'],
                    'item_idx': idx
                })
        # Render custom table with delete button in last column for main part rows
        if line_items:
            st.markdown("""
            <style>
            .quote-table-header, .quote-table-row { display: flex; align-items: center; }
            .quote-table-header { font-weight: 700; border-bottom: 2px solid #eee; margin-bottom: 4px; }
            .quote-table-row { border-bottom: 1px solid #f2f2f2; min-height: 36px; }
            .quote-table-cell { flex: 2; padding: 6px 4px; }
            .quote-table-cell.qty, .quote-table-cell.price { flex: 1; text-align: right; }
            .quote-table-cell.delete { flex: 0.5; text-align: center; }
            .quote-table-cell button { background: none; border: none; color: #ff5a00; font-size: 1.1em; cursor: pointer; }
            </style>
            <div class='material-card'>
            <div class='material-name'>Quote Line Items</div>
            <div class='quote-table-header'>
                <div class='quote-table-cell'>Description</div>
                <div class='quote-table-cell qty'>Quantity</div>
                <div class='quote-table-cell price'>Price</div>
                <div class='quote-table-cell delete'></div>
            </div>
            </div>
            """, unsafe_allow_html=True)
            delete_idx = None
            for i, li in enumerate(line_items):
                cols = st.columns([6, 1, 1, 0.7])
                cols[0].markdown(f"{li['description']}")
                cols[1].markdown(f"{li['quantity']}")
                cols[2].markdown(f"${li['price']:.2f}")
                # Only show delete button for main part rows
                if not li['is_support']:
                    with cols[3]:
                        if st.button("❌", key=f"delete_{li['item_idx']}", help="Delete this part"):
                            delete_idx = li['item_idx']
                else:
                    cols[3].markdown("")
            total = sum(li['price'] for li in line_items)
            st.markdown(f"<div style='text-align:right; font-size:1.2em; font-weight:700;'>Total: ${total:.2f}</div>", unsafe_allow_html=True)
            if delete_idx is not None:
                # Remove the part and its support row (if present)
                # Find all line_items with item_idx == delete_idx
                st.session_state['quote_items'].pop(delete_idx)
                st.experimental_rerun()
        else:
            st.info("No parts in quote. Please add a part.")
        # PDF generation for all line items
        def generate_full_pdf(line_items, total):
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            # Header bar
            c.setFillColorRGB(1, 0.35, 0)
            c.rect(0, 750, 612, 50, fill=True, stroke=0)
            c.setFont("Helvetica-Bold", 24)
            c.setFillColorRGB(1, 1, 1)
            c.drawString(50, 770, "Formlabs Manufacturing on Demand Quote Summary")
            # Table header
            c.setFont("Helvetica-Bold", 14)
            c.setFillColorRGB(0.1, 0.1, 0.1)
            y = 700
            c.drawString(50, y, "Description")
            c.drawString(320, y, "Quantity")
            c.drawString(420, y, "Price")
            y -= 20
            c.setFont("Helvetica", 12)
            for li in line_items:
                c.drawString(50, y, li['description'][:45])
                c.drawString(320, y, str(li['quantity']))
                c.drawString(420, y, f"${li['price']:.2f}")
                y -= 18
                if y < 100:
                    c.showPage()
                    y = 750
            c.setFont("Helvetica-Bold", 14)
            c.drawString(320, y, "Total:")
            c.drawString(420, y, f"${total:.2f}")
            # Footer branding
            c.setFillColorRGB(1, 0.35, 0)
            c.rect(0, 0, 612, 30, fill=True, stroke=0)
            c.setFont("Helvetica", 10)
            c.setFillColorRGB(1, 1, 1)
            c.drawString(50, 12, "Generated by Formlabs Manufacturing on Demand Tool")
            c.save()
            buffer.seek(0)
            return buffer
        pdf_buffer = generate_full_pdf(line_items, sum(li['price'] for li in line_items))
        st.download_button(
            label="Download Quote PDF",
            data=pdf_buffer,
            file_name="formlabs_quote.pdf",
            mime="application/pdf"
        )
        # Add another part
        if st.button("Add Another Part"):
            st.session_state.step = 1
            st.session_state.volume = None
            st.session_state.selected_material = None
            st.experimental_rerun()
        # Start new quote (clear all)
        if st.button("Start New Quote"):
            st.session_state.step = 1
            st.session_state.volume = None
            st.session_state.selected_material = None
            st.session_state['quote_items'] = []
            st.experimental_rerun()

if __name__ == "__main__":
    main() 