from bs4 import BeautifulSoup
import json
import re

def extract_price(price_text):
    # Extract numeric price from text like "$149" or "$799"
    match = re.search(r'\$(\d+)', price_text)
    if match:
        return int(match.group(1))
    return None

def parse_materials(html_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    materials = {
        'sla': [],
        'sls': []
    }
    
    # Updated card selector based on provided HTML
    material_cards = soup.find_all('div', class_='ui-relative ui-flex ui-w-full ui-flex-row ui-gap-4')
    
    for card in material_cards:
        # Extract image and name
        img_elem = card.find('img')
        image_url = img_elem.get('src', '') if img_elem else ''
        name = ''
        if img_elem and img_elem.has_attr('alt'):
            name = img_elem['alt'].strip()
        h2_elem = card.find('h2', class_='ui-text-material-title')
        if h2_elem and h2_elem.has_attr('title'):
            name = h2_elem['title'].strip()
        
        # Extract price
        price_elem = card.find('div', class_='ui-flex ui-items-center ui-gap-2')
        price = extract_price(price_elem.text.strip()) if price_elem else None
        
        # Extract tags
        tags = [span.text.strip() for span in card.find_all('span', class_='ui-bg-gray-100')]
        material_type = None
        for tag in tags:
            if tag == 'SLA':
                material_type = 'sla'
                break
            elif tag == 'SLS':
                material_type = 'sls'
                break
        
        if material_type and name and price:
            material_data = {
                'name': name,
                'price': price,
                'image_url': image_url,
                'tags': tags
            }
            materials[material_type].append(material_data)
    
    return materials

if __name__ == '__main__':
    materials = parse_materials('price-list/material_price_list.html')
    
    # Save to JSON file
    with open('materials.json', 'w', encoding='utf-8') as f:
        json.dump(materials, f, indent=2)
    
    # Print summary
    print(f"Found {len(materials['sla'])} SLA materials")
    print(f"Found {len(materials['sls'])} SLS materials") 