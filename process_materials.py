import json
import re

def is_pigment(material):
    # Check if 'Pigment' is in the name or tags (case-insensitive)
    name = material['name'].lower()
    if 'pigment' in name:
        return True
    for tag in material.get('tags', []):
        if 'pigment' in tag.lower():
            return True
    return False

def extract_quantity_and_unit(text):
    # Look for patterns like '6 kg', '0.7L', '1 kg', '1L', etc.
    match = re.search(r'(\d+(?:\.\d+)?)\s*(kg|l|liter|litre)', text, re.IGNORECASE)
    if match:
        quantity = float(match.group(1))
        unit = match.group(2).lower()
        # Normalize unit
        if unit.startswith('l'):
            unit = 'l'
        elif unit.startswith('kg'):
            unit = 'kg'
        return quantity, unit
    return None, None

def normalize_material(material):
    # Try to find quantity/unit in name or tags
    quantity, unit = extract_quantity_and_unit(material['name'])
    if not quantity:
        for tag in material.get('tags', []):
            quantity, unit = extract_quantity_and_unit(tag)
            if quantity:
                break
    # If not found, assume 1 kg or 1 L
    if not quantity:
        quantity = 1.0
        unit = None
    price = material['price']
    normalized_price = price / quantity
    material['normalized_price_per_kg_or_l'] = round(normalized_price, 2)
    material['quantity'] = quantity
    material['unit'] = unit if unit else 'unknown'
    return material

def process_materials(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        materials = json.load(f)
    processed = {'sla': [], 'sls': []}
    for mtype in ['sla', 'sls']:
        for material in materials[mtype]:
            if is_pigment(material):
                continue
            norm_material = normalize_material(material)
            processed[mtype].append(norm_material)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed, f, indent=2)
    print(f"Processed {len(processed['sla'])} SLA and {len(processed['sls'])} SLS materials.")

if __name__ == '__main__':
    process_materials('materials.json', 'materials_normalized.json') 